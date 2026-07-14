# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.utils import nowdate, add_days


def after_install():
    """Run after the app is installed on a site.
    Note: Custom DocTypes are NOT synced yet at this point,
    so we can only create system-level records (like roles).
    """
    create_roles()


def after_migrate():
    """Run after bench migrate. DocTypes are now synced,
    so we can safely create records referencing custom DocTypes."""
    create_number_cards()
    create_notification_settings()
    create_demo_data()


def create_roles():
    """Create the Shop Owner role if it doesn't exist."""
    if not frappe.db.exists("Role", "Shop Owner"):
        role = frappe.get_doc({
            "doctype": "Role",
            "role_name": "Shop Owner",
            "desk_access": 1,
            "home_page": "/app/udhaar-ledger",
        })
        role.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Created role: Shop Owner")


def create_number_cards():
    """Create Number Card definitions for the workspace."""
    if not frappe.db.exists("Number Card", "Total Outstanding Udhaar"):
        card = frappe.get_doc({
            "doctype": "Number Card",
            "name": "Total Outstanding Udhaar",
            "label": "Total Outstanding Udhaar",
            "document_type": "Udhaar Entry",
            "function": "Sum",
            "aggregate_function_based_on": "amount",
            "filters_json": '[["Udhaar Entry","entry_type","=","Credit Given"]]',
            "type": "Document Type",
            "color": "#3498db",
            "format": "₹{0}",
        })
        card.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Created Number Card: Total Outstanding Udhaar")

    if not frappe.db.exists("Number Card", "Customers Over Limit"):
        card = frappe.get_doc({
            "doctype": "Number Card",
            "name": "Customers Over Limit",
            "label": "Customers Over Limit",
            "document_type": "Udhaar Customer",
            "function": "Count",
            "filters_json": '[]',
            "type": "Document Type",
            "color": "#e74c3c",
        })
        card.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Created Number Card: Customers Over Limit")


def create_notification_settings():
    """Create default notification configuration for credit limit breaches."""
    if not frappe.db.exists("Notification", "Credit Limit Breach"):
        notification = frappe.get_doc({
            "doctype": "Notification",
            "name": "Credit Limit Breach",
            "subject": "Credit Limit Breach: {{ doc.customer }}",
            "document_type": "Udhaar Entry",
            "event": "New",
            "channel": ["System Notification"],
            "condition": "frappe.db.get_value('Udhaar Customer', doc.customer, 'current_balance') > frappe.db.get_value('Udhaar Customer', doc.customer, 'credit_limit')",
            "message": frappe._("""
                <h3>Credit Limit Breach Alert</h3>
                <p>Customer <strong>{{ doc.customer }}</strong> has exceeded their credit limit.</p>
                <ul>
                    <li>Entry Amount: <strong>{{ doc.amount }}</strong></li>
                    <li>Balance After: <strong>{{ doc.balance_after }}</strong></li>
                    <li>Date: <strong>{{ doc.date }}</strong></li>
                </ul>
            """),
            "value_changed": "amount",
        })
        notification.insert(ignore_permissions=True)
        frappe.db.commit()
        print("✓ Created Notification: Credit Limit Breach")


def create_demo_data():
    """Create demonstration data for first-time installation."""
    print("\n--- Creating Demo Data for Kirana Ledger ---")

    # Demo Customers
    demo_customers = [
        {"customer_name": "Ramesh Kumar", "phone": "+919876543210", "preferred_language": "Hindi", "credit_limit": 5000},
        {"customer_name": "Suresh Patel", "phone": "+919876543211", "preferred_language": "Hindi", "credit_limit": 3000},
        {"customer_name": "Priya Sharma", "phone": "+919876543212", "preferred_language": "Hindi", "credit_limit": 4000},
        {"customer_name": "Venkatesh Iyer", "phone": "+919876543213", "preferred_language": "Tamil", "credit_limit": 6000},
        {"customer_name": "Mohan Singh", "phone": "+919876543214", "preferred_language": "Hindi", "credit_limit": 2000},
        {"customer_name": "Lakshmi Devi", "phone": "+919876543215", "preferred_language": "Telugu", "credit_limit": 3500},
        {"customer_name": "Abdul Rahman", "phone": "+919876543216", "preferred_language": "Hindi", "credit_limit": 7000},
        {"customer_name": "Kavitha Nair", "phone": "+919876543217", "preferred_language": "Malayalam", "credit_limit": 2500},
    ]

    created_customers = {}
    for c in demo_customers:
        if not frappe.db.exists("Udhaar Customer", c["customer_name"]):
            customer = frappe.get_doc({
                "doctype": "Udhaar Customer",
                "customer_name": c["customer_name"],
                "phone": c["phone"],
                "preferred_language": c["preferred_language"],
                "credit_limit": c["credit_limit"],
                "current_balance": 0,
            })
            customer.insert(ignore_permissions=True)
            created_customers[c["customer_name"]] = customer.name
            print(f"  ✓ Created customer: {c['customer_name']}")
        else:
            created_customers[c["customer_name"]] = c["customer_name"]
            print(f"  - Customer exists: {c['customer_name']}")

    frappe.db.commit()

    # Demo Udhaar Entries
    demo_entries = [
        {"customer": "Ramesh Kumar", "entry_type": "Credit Given", "amount": 1500, "date": add_days(nowdate(), -7), "items_description": "Rice, Dal, Oil - weekly groceries"},
        {"customer": "Ramesh Kumar", "entry_type": "Credit Given", "amount": 800, "date": add_days(nowdate(), -3), "items_description": "Atta, sugar, tea"},
        {"customer": "Ramesh Kumar", "entry_type": "Payment Received", "amount": 1000, "date": nowdate(), "items_description": "Partial payment"},
        {"customer": "Suresh Patel", "entry_type": "Credit Given", "amount": 2000, "date": add_days(nowdate(), -5), "items_description": "Monthly ration"},
        {"customer": "Suresh Patel", "entry_type": "Credit Given", "amount": 500, "date": add_days(nowdate(), -2), "items_description": "Milk packets, bread"},
        {"customer": "Priya Sharma", "entry_type": "Credit Given", "amount": 3000, "date": add_days(nowdate(), -10), "items_description": "Cooking oil, spices, pulses"},
        {"customer": "Venkatesh Iyer", "entry_type": "Credit Given", "amount": 5000, "date": add_days(nowdate(), -15), "items_description": "Bulk groceries - 2 weeks supply"},
        {"customer": "Venkatesh Iyer", "entry_type": "Payment Received", "amount": 2000, "date": add_days(nowdate(), -1), "items_description": "Part payment received"},
        {"customer": "Mohan Singh", "entry_type": "Credit Given", "amount": 1000, "date": add_days(nowdate(), -4), "items_description": "Biscuits, cold drinks, snacks"},
        {"customer": "Lakshmi Devi", "entry_type": "Credit Given", "amount": 2500, "date": add_days(nowdate(), -8), "items_description": "Groceries - dal, chawal, tel"},
        {"customer": "Abdul Rahman", "entry_type": "Credit Given", "amount": 6000, "date": add_days(nowdate(), -20), "items_description": "Monthly household shopping"},
        {"customer": "Abdul Rahman", "entry_type": "Credit Given", "amount": 1500, "date": add_days(nowdate(), -6), "items_description": "Extra supplies - soap, shampoo"},
        {"customer": "Kavitha Nair", "entry_type": "Credit Given", "amount": 2000, "date": add_days(nowdate(), -12), "items_description": "Groceries and household items"},
    ]

    for e in demo_entries:
        customer_name = created_customers.get(e["customer"])
        if customer_name:
            entry = frappe.get_doc({
                "doctype": "Udhaar Entry",
                "customer": customer_name,
                "entry_type": e["entry_type"],
                "amount": e["amount"],
                "date": e["date"],
                "items_description": e["items_description"],
            })
            entry.insert(ignore_permissions=True)
            print(f"  ✓ Created entry: {e['entry_type']} ₹{e['amount']} for {e['customer']}")

    frappe.db.commit()

    # Demo Quick Inventory Items
    demo_items = [
        {"item_name": "Basmati Rice (5kg)", "current_stock_estimate": 15, "reorder_flag": 0},
        {"item_name": "Cooking Oil (1L)", "current_stock_estimate": 25, "reorder_flag": 0},
        {"item_name": "Wheat Flour (5kg)", "current_stock_estimate": 3, "reorder_flag": 1},
        {"item_name": "Sugar (1kg)", "current_stock_estimate": 20, "reorder_flag": 0},
        {"item_name": "Tea (250g)", "current_stock_estimate": 8, "reorder_flag": 0},
        {"item_name": "Toor Dal (1kg)", "current_stock_estimate": 2, "reorder_flag": 1},
        {"item_name": "Biscuits Packets", "current_stock_estimate": 45, "reorder_flag": 0},
        {"item_name": "Soap Bar", "current_stock_estimate": 30, "reorder_flag": 0},
    ]

    for item in demo_items:
        if not frappe.db.exists("Quick Inventory Item", item["item_name"]):
            inv_item = frappe.get_doc({
                "doctype": "Quick Inventory Item",
                "item_name": item["item_name"],
                "current_stock_estimate": item["current_stock_estimate"],
                "reorder_flag": item["reorder_flag"],
            })
            inv_item.insert(ignore_permissions=True)
            print(f"  ✓ Created inventory item: {item['item_name']}")
        else:
            print(f"  - Inventory item exists: {item['item_name']}")

    frappe.db.commit()

    print("--- Demo Data Created Successfully! ---\n")
