# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import frappe


def execute(filters=None):
    columns = [
        {"label": "Date", "fieldname": "date", "fieldtype": "Date", "width": 120},
        {"label": "Entry Type", "fieldname": "entry_type", "fieldtype": "Data", "width": 150},
        {"label": "Total Amount", "fieldname": "total_amount", "fieldtype": "Currency", "width": 150},
    ]

    data = frappe.db.sql(
        """
        SELECT
            `tabUdhaar Entry`.`date`,
            `tabUdhaar Entry`.`entry_type`,
            SUM(`tabUdhaar Entry`.`amount`) AS total_amount
        FROM
            `tabUdhaar Entry`
        GROUP BY
            `tabUdhaar Entry`.`date`,
            `tabUdhaar Entry`.`entry_type`
        ORDER BY
            `tabUdhaar Entry`.`date` DESC
        """,
        as_dict=1,
    )

    return columns, data
