# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class UdhaarCustomer(Document):
    def validate(self):
        if self.phone:
            self.validate_phone()

    def validate_phone(self):
        import re
        # Basic phone validation - allow digits, +, and hyphens
        phone = self.phone.strip()
        if not re.match(r'^\+?[\d\-\(\)\s]{7,15}$', phone):
            frappe.throw(
                frappe._("Phone number is not valid. Enter a valid phone number with country code (e.g., +919876543210).")
            )

    def get_balance(self):
        """Calculate current balance by summing all Udhaar Entries"""
        credit_given = frappe.db.get_all(
            "Udhaar Entry",
            filters={"customer": self.name, "entry_type": "Credit Given"},
            pluck="amount"
        )
        payments = frappe.db.get_all(
            "Udhaar Entry",
            filters={"customer": self.name, "entry_type": "Payment Received"},
            pluck="amount"
        )
        total_credit = sum(credit_given) if credit_given else 0
        total_payments = sum(payments) if payments else 0
        return total_credit - total_payments

    # Balance is persisted in `current_balance` DB field, updated on every Udhaar Entry save.
    # No need to recompute on every load.
