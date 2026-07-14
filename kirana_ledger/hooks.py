# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__ as app_version

app_name = "kirana_ledger"
app_title = "Kirana Ledger"
app_publisher = "Pasha1234565"
app_description = "Hyper-Local Inventory + Udhaar (Credit) Ledger for Kirana Stores"
app_email = ""
app_license = "MIT"

# Apps
# ------------------
# apps = ["frappe"]

# Fixtures
# ----------
# Workspace, Number Cards, and Role are created programmatically via after_install hook
fixtures = []

# Document Events
# ---------------
# Udhaar Entry's before_save is handled by the DocType controller itself
# (via the before_save method in udhaar_entry.py)
# doc_events = {}

# User Data Protection
# --------------------
user_data_fields = [
    {
        "doctype": "Udhaar Customer",
        "filter_by": "phone",
        "redact_fields": ["customer_name", "phone"],
    }
]

# After Install
# -------------
after_install = "kirana_ledger.kirana_ledger.setup.after_install"

# After Migrate
# -------------
after_migrate = "kirana_ledger.kirana_ledger.setup.after_migrate"

# Scheduled Tasks
# ----------------
scheduler_events = {
    "daily": [
        "kirana_ledger.kirana_ledger.api.check_overdue_customers"
    ]
}

# Website
# ----------
# WhatsApp webhook is accessible via @frappe.whitelist at:
# /api/method/kirana_ledger.kirana_ledger.api.whatsapp_webhook
