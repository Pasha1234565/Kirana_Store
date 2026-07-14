# 🏪 Kirana Ledger — Hyper-Local Inventory + Udhaar Ledger

**A Frappe/ERPNext v15 custom app** for small kirana (retail) stores to manage:
- **Udhaar (credit) ledger** — Track who owes what, with regional language support
- **Quick inventory** — Lightweight stock estimates (not full ERP item tracking)
- **WhatsApp-first** — Entry via WhatsApp messages (Meta Business API integration)

> ⚠️ **Important caveat**: This app was built as a Frappe portfolio/demo project.  
> For a real-world kirana store product, a slim mobile app + WhatsApp Business API + lightweight backend (FastAPI/Firebase/Supabase) would be more appropriate than a full ERPNext stack.  
> See the [Architecture Note](#-architecture-note) section for details.

---

## ✨ Features

### 📋 Core DocTypes

| DocType | Purpose |
|---|---|
| **Udhaar Customer** | Customer with name, phone, preferred language, credit limit, auto-computed balance |
| **Udhaar Entry** | Credit given or payment received, auto-updates customer balance |
| **Quick Inventory Item** | Lightweight stock estimates with reorder flags |

### 📊 Reports

| Report | Description |
|---|---|
| **Daily Udhaar Summary** | Total credit given vs. collected, grouped by day |
| **Customers Over Credit Limit** | Customers whose balance exceeds their credit limit |
| **Top Overdue Customers** | Highest-balance customers, with preferred language shown |

### 📱 WhatsApp Integration (API)

The app includes a webhook endpoint (`/api/method/kirana_ledger.kirana_ledger.api.whatsapp_webhook`) for the Meta WhatsApp Business Cloud API.

Example commands it can parse:
- *"Ramesh ko 200 udhaar diya"* → Creates a ₹200 Udhaar Entry
- *"Suresh ne 500 diya"* → Creates a ₹500 Payment Entry
- *"Ramesh ko 300 diya"* → Creates a ₹300 Credit Entry

### 🖥️ Workspace

An **Udhaar Ledger** workspace is auto-created on install with:
- Number cards for Total Outstanding Udhaar & Customers Over Limit
- Shortcuts to New Customer, New Entry, Inventory, and Reports

---

## 🚀 Installation

### Prerequisites

- ERPNext v15 / Frappe v15+ installed via Frappe Bench
- Python 3.10+
- MariaDB 10.6+

### Known Issue: Frappe v15+ esbuild bug

Frappe v15's esbuild has a bug that crashes when `bench get-app` tries to build an app that isn't yet registered in `sites/apps.txt`. The app has no frontend assets, so **the build step is unnecessary**. Use the manual installation below to bypass this.

### Steps (Manual — Recommended)

```bash
# 1. Go to your bench and clone the app directly
cd ~/frappe-bench/apps
git clone https://github.com/Pasha1234565/Kirana_Store.git kirana_ledger

# 2. Go back to bench root
cd ~/frappe-bench

# 3. Add app to sites/apps.txt so Frappe can find it
echo "kirana_ledger" >> ~/frappe-bench/sites/apps.txt

# 4. Install on your site
bench --site yoursite.local install-app kirana_ledger

# 5. Migrate to sync DocTypes and create demo data
bench --site yoursite.local migrate
```

> The `after_migrate` hook will automatically:
> - Create **Number Cards** (Total Outstanding Udhaar & Customers Over Limit)
> - Create **demo customers** (8 customers with Udhaar entries)
> - Create **demo inventory items** (8 items with stock estimates)
> - Create the **Credit Limit Breach** notification
> 
> The **Shop Owner** role is created during `install-app`.

### Post-Install Setup

1. Assign the **Shop Owner** role to your user:
   - Go to *User* → Select your user → Add *Shop Owner* role
2. The **Udhaar Ledger** workspace will appear in the desk module list

---

## 🔧 Configuration

### WhatsApp Webhook

To connect WhatsApp Business API:

1. Create a Meta Business App at [developers.facebook.com](https://developers.facebook.com)
2. Set your webhook verify token in site config:
   ```bash
   bench --site yoursite.local set-config whatsapp_verify_token "your_secure_token"
   ```
3. Point WhatsApp webhook to:
   ```
   https://yoursite.com/api/method/kirana_ledger.kirana_ledger.api.whatsapp_webhook
   ```

### Notifications

The app auto-creates a **Credit Limit Breach** notification that triggers when:
- A new Udhaar Entry is created
- The customer's balance exceeds their credit limit

---

## 🗺️ Architecture

```
kirana_ledger/                     # Repo root
├── kirana_ledger/                 # Python package
│   ├── hooks.py                   # Frappe hooks configuration
│   ├── kirana_ledger/             # Module
│   │   ├── doctype/               # DocType definitions
│   │   │   ├── udhaar_customer/
│   │   │   ├── udhaar_entry/
│   │   │   └── quick_inventory_item/
│   │   ├── report/                # Query reports
│   │   ├── workspace/             # Desk workspace
│   │   ├── api.py                 # WhatsApp webhook & scheduled tasks
│   │   └── setup.py               # Post-install demo data
│   └── config/                    # Desktop & docs config
├── setup.py
├── requirements.txt
├── README.md
└── license.txt
```

### Key Hooks

- **`after_install`** → `kirana_ledger.kirana_ledger.setup.after_install` — Creates roles, number cards, demo data
- **`doc_events`** → `Udhaar Entry before_save` — Auto-updates customer balance
- **`scheduler_events`** → Daily check for overdue customers

---

## 💡 Usage

### Quick Entry Workflow

1. Open the **Udhaar Ledger** workspace
2. Click **New Udhaar Customer** → Enter name, phone, language, credit limit
3. Click **New Udhaar Entry** → Select customer, enter amount, choose type
4. The customer's balance updates automatically

### Making an Entry via WhatsApp (when configured)

Text *"Ramesh ko 200 udhaar diya"* to your WhatsApp Business number.  
The app will create an Udhaar Entry for ₹200 in Ramesh's name.

---

## 🏗️ Architecture Note

This app uses Frappe/ERPNext which is designed for:
- Desktop-first admin interfaces with complex workflows
- Full accounting-grade stock ledgers
- Server environments with 2GB+ RAM and fast connections

For a real kirana store product, consider:
- **Frontend**: Flutter or React Native mobile app (lightweight, offline-capable)
- **Messaging**: WhatsApp Business Cloud API
- **Backend**: FastAPI or Supabase
- **Auth**: Phone/OTP based
- **Target UX**: < 10 seconds per transaction on ₹6,000 Android phones

---

## 📄 License

MIT
