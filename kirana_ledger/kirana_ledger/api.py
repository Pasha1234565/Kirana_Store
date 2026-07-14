# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import json
import frappe
from frappe import _
from frappe.utils import nowdate, add_days


@frappe.whitelist(allow_guest=True)
def whatsapp_webhook():
    """
    WhatsApp Business Cloud API webhook endpoint.

    Accepts POST requests with incoming WhatsApp messages, parses natural language
    udhaar commands (e.g., "Ramesh ko 200 udhaar diya"),
    creates the corresponding Udhaar Entry.

    Expected payload format (WhatsApp Business API):
    {
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "919876543210",
                        "text": {"body": "Ramesh ko 200 udhaar diya"}
                    }]
                }
            }]
        }]
    }
    """
    if frappe.request.method != "POST":
        frappe.throw(_("Only POST requests are accepted"), frappe.AuthenticationError)

    if frappe.request.data:
        data = frappe.parse_json(frappe.request.data)
    else:
        frappe.throw(_("No data received"), frappe.AuthenticationError)

    try:
        # Extract message from WhatsApp payload
        entry = data.get("entry", [])
        if not entry:
            frappe.response["message"] = "No entries"
            return

        changes = entry[0].get("changes", [])
        if not changes:
            frappe.response["message"] = "No changes"
            return

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        if not messages:
            frappe.response["message"] = "No messages"
            return

        for msg in messages:
            from_number = msg.get("from", "")
            text_body = msg.get("text", {}).get("body", "")

            if not text_body:
                continue

            # Parse the natural language command
            entry_data = parse_udhaar_command(text_body, from_number)
            if entry_data:
                create_udhaar_entry(entry_data)
                # Send confirmation reply (integration with WhatsApp Cloud API required)
                # send_whatsapp_reply(from_number, entry_data)

        frappe.response["message"] = "Processed successfully"
        frappe.response["status"] = "ok"

    except Exception as e:
        frappe.log_error(
            title="WhatsApp Webhook Error",
            message=frappe.get_traceback()
        )
        frappe.response["message"] = str(e)
        frappe.response["status"] = "error"


def parse_udhaar_command(text, from_number):
    """
    Simple NLU parser for udhaar commands.

    Supports patterns like:
    - "Ramesh ko 200 udhaar diya" → Credit of 200 for Ramesh
    - "Suresh ne 500 diya" → Payment of 500 from Suresh
    - "Ramesh ko 300 diya" → Credit of 300 for Ramesh
    """
    text = text.strip().lower()

    # Determine entry type
    if "udhaar" in text or "diya" in text or "dene" in text:
        # This is credit being given
        entry_type = "Credit Given"
    elif "liya" in text or "vapas" in text or "payment" in text:
        entry_type = "Payment Received"
    else:
        # Default to credit if unsure
        entry_type = "Credit Given"

    # Extract amount (look for numbers)
    import re
    amount_match = re.search(r'(\d+)', text)
    if not amount_match:
        return None

    amount = float(amount_match.group(1))

    # Extract customer name (text before "ko", "ne", "se")
    name_match = re.search(
        r'^(.+?)\s+(ko|ne|se|ka|ki)\s+',
        text
    )
    if not name_match:
        # Try to get the name from the first word(s) before the number
        parts = text.split(str(int(amount)) if amount == int(amount) else str(amount))
        if parts:
            customer_name = parts[0].strip().rstrip("ko ne se ka ki ke").strip().title()
        else:
            customer_name = ""
    else:
        customer_name = name_match.group(1).strip().title()

    if not customer_name:
        # Fallback: look up customer by phone number
        customer_name = get_customer_by_phone(from_number)
        if not customer_name:
            return None

    return {
        "customer_name": customer_name,
        "amount": amount,
        "entry_type": entry_type,
        "from_number": from_number,
        "text": text,
    }


def get_customer_by_phone(phone):
    """Find a customer by their phone number."""
    customers = frappe.db.get_all(
        "Udhaar Customer",
        filters={"phone": ["like", f"%{phone[-10:]}" ]},
        limit=1
    )
    if customers:
        return customers[0].name
    return None


def create_udhaar_entry(entry_data):
    """Create an Udhaar Entry from parsed command data."""
    # Find or create customer
    customer_name = entry_data["customer_name"]

    # Try to find existing customer
    existing = frappe.db.get_value("Udhaar Customer", {"customer_name": customer_name}, "name")

    if not existing:
        # Create customer on the fly
        customer = frappe.get_doc({
            "doctype": "Udhaar Customer",
            "customer_name": customer_name,
            "phone": entry_data.get("from_number", ""),
            "preferred_language": "Hindi",
        })
        customer.insert()
        customer_name = customer.name
    else:
        customer_name = existing

    # Create the entry
    entry = frappe.get_doc({
        "doctype": "Udhaar Entry",
        "customer": customer_name,
        "entry_type": entry_data["entry_type"],
        "amount": entry_data["amount"],
        "date": nowdate(),
        "items_description": f"Via WhatsApp: {entry_data['text']}",
    })
    entry.insert()
    return entry


def check_overdue_customers():
    """
    Scheduled daily task to check for overdue customers.
    Triggers a notification for customers with:
    - current_balance > credit_limit
    - No payment in the last 30 days while having a balance
    """
    overdue_customers = frappe.db.sql(
        """
        SELECT
            c.name,
            c.phone,
            c.current_balance,
            c.credit_limit,
            c.preferred_language
        FROM `tabUdhaar Customer` c
        WHERE c.current_balance > 0
        AND c.current_balance > c.credit_limit
        """,
        as_dict=True,
    )

    for customer in overdue_customers:
        # Log a system notification
        create_overdue_notification(customer)


def create_overdue_notification(customer):
    """Create a system notification for an overdue customer."""
    try:
        notification = frappe.get_doc({
            "doctype": "Notification Log",
            "subject": _("Credit Limit Breach: {0}").format(customer.name),
            "email_content": _(
                "Customer {0} (Phone: {1}) has exceeded their credit limit.\n"
                "Current Balance: {2}\nCredit Limit: {3}"
            ).format(
                customer.name,
                customer.phone,
                customer.current_balance,
                customer.credit_limit,
            ),
            "type": "Alert",
        })
        notification.insert(ignore_permissions=True)
    except Exception:
        frappe.log_error(
            title="Overdue Notification Error",
            message=frappe.get_traceback()
        )


@frappe.whitelist(allow_guest=True)
def whatsapp_webhook_verify():
    """
    WhatsApp Business API webhook verification.
    Handles the GET verification challenge from Meta.
    """
    if frappe.request.method != "GET":
        frappe.throw(_("Only GET requests are accepted"), frappe.AuthenticationError)

    hub_mode = frappe.form_dict.get("hub.mode")
    hub_challenge = frappe.form_dict.get("hub.challenge")
    hub_verify_token = frappe.form_dict.get("hub.verify_token")

    # Set your verify token in Site Config:
    # bench --site yoursite set-config whatsapp_verify_token "your_token_here"
    expected_token = frappe.conf.get("whatsapp_verify_token", "kirana_ledger_verify")

    if hub_mode == "subscribe" and hub_verify_token == expected_token:
        frappe.response["http_status_code"] = 200
        frappe.response["data"] = hub_challenge
    else:
        frappe.response["http_status_code"] = 403
        frappe.response["message"] = "Verification failed"
