# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe
from frappe.model.document import Document


class QuickInventoryItem(Document):
    def validate(self):
        if self.current_stock_estimate < 0:
            frappe.throw(
                frappe._("Current stock estimate cannot be negative.")
            )
