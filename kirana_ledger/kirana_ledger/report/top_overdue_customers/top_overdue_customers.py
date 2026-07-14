# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute(filters=None):
    columns = [
        {"label": "Customer", "fieldname": "customer", "fieldtype": "Link", "options": "Udhaar Customer", "width": 200},
        {"label": "Phone", "fieldname": "phone", "fieldtype": "Data", "width": 150},
        {"label": "Balance", "fieldname": "current_balance", "fieldtype": "Currency", "width": 120},
        {"label": "Credit Limit", "fieldname": "credit_limit", "fieldtype": "Currency", "width": 120},
        {"label": "Language", "fieldname": "preferred_language", "fieldtype": "Data", "width": 100},
    ]

    data = frappe.db.sql(
        """
        SELECT
            `tabUdhaar Customer`.`name` AS customer,
            `tabUdhaar Customer`.`phone`,
            `tabUdhaar Customer`.`current_balance`,
            `tabUdhaar Customer`.`credit_limit`,
            `tabUdhaar Customer`.`preferred_language`
        FROM `tabUdhaar Customer`
        WHERE `tabUdhaar Customer`.`current_balance` > 0
        ORDER BY `tabUdhaar Customer`.`current_balance` DESC
        LIMIT 50
        """,
        as_dict=1,
    )

    return columns, data
