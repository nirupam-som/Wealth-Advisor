# 🏦 AI Wealth Advisor

> Your AI-Powered Personal Finance Copilot

AI Wealth Advisor analyzes your expenses, investments, and financial goals to generate
AI-powered recommendations using Google Gemini and LangChain.

## ✨ Features

- **📤 Upload Bank Statements** — CSV upload with automatic parsing
- **🏷️ Smart Categorization** — LLM-powered spending categorization
- **📊 Financial Dashboard** — Interactive charts and spending analytics
- **🎯 Goal-Based Planning** — Set, track, and manage financial goals
- **💡 AI Insights** — Personalized savings and investment recommendations
- **💬 Financial Chatbot** — Conversational AI financial assistant
- **📈 Risk Scoring** — Portfolio risk analysis and recommendations

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit |
| Backend | FastAPI |
| LLM | Google Gemini (via LangChain) |
| Database | SQLite |
| Vector DB | ChromaDB |
| Data Analytics | Pandas |
| Charts | Plotly |

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Google Gemini API Key ([Get one free](https://aistudio.google.com/))

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd ai-wealth-advisor
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate  # Windows
   # source venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   copy .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

5. **Start the Backend:**
   ```bash
   uvicorn backend.main:app --reload --port 8000
   ```

6. **Start the Frontend (in a new terminal):**
   ```bash
   streamlit run frontend/app.py --server.port 8501
   ```

7. **Open your browser:**
   - Frontend: http://localhost:8501
   - API Docs: http://localhost:8000/docs

### Quick Test
A sample bank statement CSV is provided at `data/sample_statement.csv` for testing.

## 📁 Project Structure

```
ai-wealth-advisor/
├── backend/
│   ├── main.py              # FastAPI entry point
│   ├── config.py             # Settings & environment
│   ├── database.py           # SQLite + SQLAlchemy
│   ├── models.py             # Database models
│   ├── schemas.py            # Pydantic schemas
│   ├── routers/              # API endpoints
│   │   ├── upload.py
│   │   ├── transactions.py
│   │   ├── goals.py
│   │   ├── chat.py
│   │   └── insights.py
│   └── services/             # Business logic
│       ├── file_storage.py
│       └── llm_service.py
├── frontend/
│   ├── app.py                # Streamlit main app
│   └── pages/
│       ├── 1_Dashboard.py
│       ├── 2_Upload.py
│       ├── 3_Goals.py
│       ├── 4_Insights.py
│       └── 5_Chat.py
├── data/
│   └── sample_statement.csv
├── storage/uploads/          # Uploaded files (auto-created)
├── requirements.txt
├── .env.example
└── README.md
```

## 📋 Development Phases

- **Phase 1** ✅ Foundation & Project Setup
- **Phase 2** 🔜 Data Ingestion & Analytics
- **Phase 3** 🔜 AI Insights & RAG Setup
- **Phase 4** 🔜 Frontend Polish
- **Phase 5** 🔜 Finalization & Deliverables

## 📄 License

This project is for educational purposes.
