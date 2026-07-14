# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class UdhaarEntry(Document):
    def before_save(self):
        """Auto-update customer balance on save."""
        self.update_customer_balance()

    def update_customer_balance(self):
        """Recalculate and update the customer's current balance after this entry."""
        if not self.customer:
            return

        customer = frappe.get_doc("Udhaar Customer", self.customer)

        # Compute balance from all entries for this customer, excluding current entry
        filters = {"customer": self.customer}
        if not self.get("__islocal") and self.name:
            filters["name"] = ["!=", self.name]

        credit_given = frappe.db.get_all(
            "Udhaar Entry",
            filters={**filters, "entry_type": "Credit Given"},
            pluck="amount"
        )
        payments = frappe.db.get_all(
            "Udhaar Entry",
            filters={**filters, "entry_type": "Payment Received"},
            pluck="amount"
        )

        total_credit = sum(credit_given) if credit_given else 0
        total_payments = sum(payments) if payments else 0

        # Add current entry amount
        if self.entry_type == "Credit Given":
            total_credit += self.amount
        else:
            total_payments += self.amount

        new_balance = total_credit - total_payments

        # Update both the entry and the customer
        self.balance_after = new_balance
        customer.db_set("current_balance", new_balance)
