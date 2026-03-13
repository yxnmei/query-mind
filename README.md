# 🧠 QueryMind

> **Ask anything. Get answers.**

QueryMind is an AI-powered Text-to-SQL application that lets anyone query a relational database using plain English. Powered by **Gemini 2.5 Flash** and built with **Streamlit**, it transforms natural-language questions into SQL queries, executes them instantly, and visualises the results — no SQL knowledge required.

![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-red?style=flat-square&logo=streamlit)
![Gemini](https://img.shields.io/badge/Gemini-2.5%20Flash-orange?style=flat-square&logo=google)
![SQLite](https://img.shields.io/badge/SQLite-3-lightblue?style=flat-square&logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## 🌐 Live Demo

**👉 [https://query-mind.streamlit.app/](https://query-mind.streamlit.app/)**


## ✨ Features

- 💬 **Natural language querying** — type a question, get a SQL result instantly
- 🔍 **Auto schema introspection** — reads your database structure automatically, no hardcoding
- 📂 **Multi-format file upload** — supports `.sqlite`, `.db`, `.csv`, and `.xlsx`
- 💾 **Persistent uploads** — uploaded datasets are saved and available across restarts
- 🗄️ **Multi-database selector** — switch between uploaded datasets with one click
- 🤖 **AI-generated example questions** — Gemini suggests 5 relevant questions for every new dataset
- 📊 **Auto-visualisation** — results are automatically charted using Plotly where applicable
- 🛡️ **SQL safety layer** — blocks any destructive queries (DROP, DELETE, ALTER, etc.)
- 🧵 **Conversation memory** — supports natural follow-up questions within a session


## 🖥️ Demo

**Dataset used:** Singapore HDB Resale Prices (data.gov.sg)

Example questions you can ask:
- *"Which town has the highest average resale price?"*
- *"Show me the average resale price by year from 2015 to 2024"*
- *"Which towns have average prices above $600,000 for 4-room flats in the last 3 years?"*
- *"What is the month-over-month change in average resale price for 5-room flats?"*


## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Language Model | Google Gemini 2.5 Flash via `google-genai` |
| Frontend | Streamlit |
| Database | SQLite via SQLAlchemy |
| Data Processing | Pandas |
| Visualisation | Plotly Express |
| Environment | Python 3.9+, python-dotenv |


## 🗂️ Project Structure

```
QueryMind/
├── data/
│   ├── ecommerce.sqlite        ← default sample database
│   ├── uploads/                ← user-uploaded databases (persistent)
│   └── seed_database.py        ← script to regenerate sample data
├── src/
│   ├── app.py                  ← Streamlit UI
│   ├── gemini_interface.py     ← Gemini 2.5 Flash integration
│   ├── sql_executor.py         ← Safe SQL execution layer
│   ├── schema_inspector.py     ← Auto schema introspection
│   └── utils.py                ← File upload, visualisation, helpers
├── .env.example                ← Environment variable template
├── .gitignore
├── requirements.txt
└── README.md
```



## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/QueryMind.git
cd QueryMind
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up your API key

```bash
cp .env.example .env
```

Open `.env` and fill in your key:
```
GEMINI_API_KEY=your_api_key_here
```

Get a free API key at [aistudio.google.com](https://aistudio.google.com).

### 5. Seed the sample database (optional)

```bash
python data/seed_database.py
```

### 6. Run the app

```bash
streamlit run src/app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.


## 📁 Using Your Own Data

1. Click **"Upload Your Own Data"** in the sidebar
2. Drop in a `.csv`, `.xlsx`, `.sqlite`, or `.db` file
3. QueryMind auto-converts it, reads the schema, and generates suggested questions
4. Your file is saved to `data/uploads/` and available on every future restart

---

## 🔒 Security

- Only `SELECT` statements are permitted — all write operations are blocked at the executor level
- API keys are loaded from `.env` and never exposed in the UI
- `.env` and `data/uploads/` are excluded from version control via `.gitignore`



## ☁️ Deployment (Streamlit Community Cloud)

1. Push this repo to GitHub (make sure `.env` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub
3. Click **"New app"** → select your repo → set main file to `src/app.py`
4. Under **Advanced settings → Secrets**, add:
```toml
GEMINI_API_KEY = "your_api_key_here"
```
5. Click **Deploy** — your app will be live in ~2 minutes!


## 🔮 Future Improvements

- [ ] Export query results as CSV
- [ ] Natural language chart customisation ("make it a pie chart")
- [ ] Query history log with copy-to-clipboard
- [ ] Support for PostgreSQL and MySQL connections
- [ ] User authentication for multi-user deployments
- [ ] Dark/light mode toggle

---
