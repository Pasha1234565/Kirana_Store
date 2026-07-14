// Copyright (c) 2024, Pasha1234565 and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Top Overdue Customers"] = {
    "filters": [
        {
            "fieldname": "min_balance",
            "label": __("Minimum Balance"),
            "fieldtype": "Currency",
            "default": 100,
            "reqd": 0
        },
        {
            "fieldname": "language",
            "label": __("Preferred Language"),
            "fieldtype": "Select",
            "options": "\nHindi\nTamil\nTelugu\nMalayalam\nKannada\nEnglish",
            "default": "",
            "reqd": 0
        }
    ]
};
