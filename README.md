# 🧠 BizMind AI Assistant (V3.1+)

> An enterprise-grade, AI-powered business operations assistant that manages **Inventory**, **Accounting**, **Analytics**, and **Helpdesk** — now powered by a professional **Flask** web architecture and local LLM grounding.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Features

| Module | Capabilities |
|--------|-------------|
| 📦 **Inventory** | Track stock levels, reorder alerts, add/update/delete products, professional HTML view |
| 💰 **Accounting** | Log income/expense, monthly P&L tracking, transaction history (SQL-backed) |
| 📊 **Analytics** | Revenue trends, top products, category breakdown via AI-driven SQL queries |
| 🤝 **Helpdesk** | AI-generated ticket responses, priority management, status tracking |
| 🛡️ **Admin Panel** | Secure session-based authentication and role management |
| 💬 **AI Chat** | Multi-step grounded NLP-to-SQL pipeline using local Qwen2.5 |

---

## 🏗️ Architecture (Enterprise Web Migration)

The project has recently migrated from Streamlit to a more scalable **Flask** architecture to support professional web styling and custom routing.

```
bizmind/
├── server.py                 # Flask entry point & Route handlers
├── .env                      # Environment configuration
├── run.bat                   # One-click Windows launcher
├── database/
│   ├── db.py                 # SQLAlchemy engine & session
│   ├── models.py             # ORM models + Pydantic schemas
│   └── seed_data.py          # Database seeder (Electronics focus)
├── ai/
│   └── assistant.py          # Grounded NLP-to-SQL agent (Ollama/Qwen2.5)
├── templates/                # Professional HTML5/CSS3 UI
│   ├── dashboard.html        # Main analytics overview
│   └── inventory.html        # Product management interface
├── static/                   # CSS, JS, and Images
├── scripts/                  # Data generation & testing utilities
└── utils/
    ├── sidebar.py            # AI chat logic
    └── logger.py             # Centralized logging (bizmind.log)
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running
- `qwen2.5` model pulled (`ollama pull qwen2.5`)

### 1. Clone & Install
```bash
git clone https://github.com/Mat-rixMJ/Bizmind.git
cd Bizmind
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python database/seed_data.py
```

### 3. Launch the App
**Windows Launcher:**
```bash
Double-click run.bat
```
**Manual Start:**
```bash
python server.py
```
App opens at: **http://localhost:5000**

---

## 🤖 AI Precision & Grounding

The BizMind AI (V3.1) uses a sophisticated **Reflective Grounding** technique:

1. **Schema Awareness**: AI knows the exact SQLite schema and constraints.
2. **SQL Generation**: Converts natural language (e.g., "What's our revenue this month?") into valid SQL.
3. **Markdown Context**: Query results are injected into the LLM as structured Markdown tables.
4. **Rupee Enforcement**: All financial outputs are strictly formatted with the **₹** symbol.
5. **Zero Hallucination**: If the data doesn't exist, the AI explicitly states "Information not found" rather than guessing.

---

## 📈 Current Progress

- ✅ **Framework Shift**: Successfully migrated core logic from Streamlit to Flask for better performance and UI control.
- ✅ **Electronics Dataset**: Updated database with a rich set of electronics products (Phones, Laptops, Components).
- ✅ **Logging**: Implemented robust logging in `bizmind.log` for auditing all AI-generated SQL queries.
- ✅ **Security**: Added session-based authentication and role-based access logic in `server.py`.

---

## 🧪 Testing
```bash
python run_tests.py
```
*Validated for SQL injection safety and grounding accuracy.*

---

## 📄 License
MIT License - Developed for the BizMind Enterprise Suite.
