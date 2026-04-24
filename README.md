# 🧠 BizMind AI Assistant

> An enterprise-grade, AI-powered business operations assistant that manages **Inventory**, **Accounting**, **Analytics**, and **Helpdesk** — all through a secure, role-based web interface powered by a local LLM.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red?logo=streamlit)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-green)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

---

## 📋 Features

| Module | Capabilities |
|--------|-------------|
| 📦 **Inventory** | Track stock levels, reorder alerts, add/update/delete products, CSV export |
| 💰 **Accounting** | Log income/expense, monthly P&L charts, transaction history, CSV export |
| 📊 **Analytics** | Revenue trends, top products, category breakdown, date-range filtering |
| 🤝 **Helpdesk** | AI-generated ticket responses, priority management, status tracking |
| 🛡️ **Admin Panel** | User management, role assignment, add/delete users |
| 💬 **AI Chat** | Persistent sidebar chat powered by local Qwen2.5 with live SQL context |

---

## 🏗️ Architecture

```
bizmind/
├── app.py                    # Main dashboard entry point
├── .env                      # Environment configuration
├── run.bat                   # One-click Windows launcher
├── .streamlit/
│   └── config.toml           # Dark enterprise theme
├── database/
│   ├── db.py                 # SQLAlchemy engine & session
│   ├── models.py             # ORM models + Pydantic schemas
│   └── seed_data.py          # Database seeder with sample data
├── ai/
│   └── assistant.py          # NLP-to-SQL agent (Ollama/Qwen2.5)
├── modules/
│   ├── auth.py               # bcrypt auth, RBAC, login UI
│   ├── inventory.py          # Inventory business logic
│   ├── accounting.py         # Accounting business logic
│   ├── analytics.py          # Sales analytics & aggregations
│   └── helpdesk.py           # Ticket management + AI responses
├── pages/
│   ├── 1_Inventory.py        # Inventory Streamlit page
│   ├── 2_Accounting.py       # Accounting Streamlit page (Admin only)
│   ├── 3_Analytics.py        # Analytics Streamlit page (Admin only)
│   ├── 4_Helpdesk.py         # Helpdesk Streamlit page
│   └── 5_Admin.py            # Admin control panel (Admin only)
└── utils/
    ├── sidebar.py            # Persistent AI chat sidebar component
    └── logger.py             # Centralized logging system
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- [Ollama](https://ollama.ai) installed and running
- `qwen2.5` model pulled (`ollama pull qwen2.5`)

### 1. Clone the Repository
```bash
git clone https://github.com/Mat-rixMJ/Bizmind.git
cd Bizmind
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment
Create a `.env` file:
```env
OLLAMA_MODEL=qwen2.5
```

### 4. Initialize & Seed Database
```bash
python database/seed_data.py
```

### 5. Launch the App

**Option A — Windows One-Click Launcher:**
```
Double-click run.bat
```

**Option B — Manual:**
```bash
python -m streamlit run app.py
```

App opens at: **http://localhost:8501**

---

## 🔑 Default Login Credentials

| Username | Password | Role |
|----------|----------|------|
| `admin` | `admin123` | Administrator (full access) |
| `staff` | `staff123` | Standard (Inventory + Helpdesk only) |

> ⚠️ Change these credentials immediately in any production deployment via the Admin Panel.

---

## 🔒 Security Features

- **Passwords**: Hashed with `bcrypt` — never stored in plain text
- **RBAC**: Accounting and Analytics pages are admin-only
- **Input Validation**: All form inputs validated via `Pydantic` before touching the database
- **SQL Safety**: AI agent only executes `SELECT` queries — no write access
- **Local LLM**: All AI inference runs entirely on your local machine via Ollama — zero business data leaves your system

---

## 🤖 How the AI Works

The BizMind AI chat uses a **two-step NLP-to-SQL pipeline**:

1. **Query Generation** — Qwen2.5 receives the user's question and the database schema, then writes a targeted `SELECT` SQL query
2. **Response Generation** — Python executes the query to fetch only the relevant data rows, which are then passed back to Qwen2.5 to compose a natural language answer

This prevents context window overflow and ensures the AI always answers from **live, accurate business data**.

---

## 🧪 Running Tests

```bash
python run_tests.py
```

Expected: **22/22 tests passed** covering all modules, ORM operations, and the AI pipeline.

---

## 📦 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| ORM | SQLAlchemy 2.0 |
| Validation | Pydantic v2 |
| Database | SQLite |
| AI Engine | Ollama (Qwen2.5) |
| Auth | bcrypt / passlib |
| Charts | Plotly Express |
| Data | Pandas |
| Logging | Python `logging` → `bizmind.log` |

---

## 📄 License

This project is licensed under the MIT License.
