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

    # Balance is persisted in `current_balance` DB field, updated on every Udhaar Entry save.
    # Computation happens in udhaar_entry.py update_customer_balance()
