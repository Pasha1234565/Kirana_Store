// Copyright (c) 2024, Pasha1234565 and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Customers Over Credit Limit"] = {
    "filters": [
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
