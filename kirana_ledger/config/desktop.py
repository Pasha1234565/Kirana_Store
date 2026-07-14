# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from frappe import _


def get_data():
    return [
        {
            "module_name": "Kirana Ledger",
            "color": "#2C3E50",
            "icon": "octicon octicon-inbox",
            "type": "module",
            "label": _("Kirana Ledger"),
            "description": _("Hyper-Local Inventory + Udhaar (Credit) Ledger for Kirana Stores."),
        }
    ]
