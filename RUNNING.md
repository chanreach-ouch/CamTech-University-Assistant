# How to Run the CamTech University Assistant

A complete step-by-step guide to setup, run, and evaluate the CamTech University Assistant RAG application.

---

## 1. Prerequisites

Ensure you have the following installed on your system:
- **Python 3.11+**
- **Docker Desktop** (must be running for PostgreSQL + pgvector)
- **Git**

---

## 2. Environment Setup

### A. Clone & Virtual Environment
If not already activated, open your terminal in the project root:

**Windows PowerShell:**
```powershell
# Create venv if not already created
python -m venv .venv

# Activate virtual environment
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

---

### B. Environment Variables (`.env`)
Create or verify the `.env` file in the root directory:

```env
LLM_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
DATABASE_URL=postgresql://user:pass@localhost:5433/university_assistant
```

* **LLM Provider:** Groq (`qwen/qwen3.8-27b`)
* **Embeddings:** Cohere (`embed-multilingual-v3.0`)
* **Vector DB:** PostgreSQL with `pgvector` on port `5433`

---

## 3. Starting the Database

Make sure **Docker Desktop** is running, then start the PostgreSQL + pgvector container:

```bash
docker compose up -d
```

### Verify Database Status:
```bash
docker ps
```
You should see a container named `camtechuniversityassistant-postgres-1` (or similar) mapped to port `5433:5432` with status `Up`.

---

## 4. (Optional) Ingestion & Embedding Pipeline

> **Note:** The database is already pre-loaded with **1,412 chunks**. You only need to run this if you wipe the database or add new documents to `data/raw/`.

```bash
# Ingest and embed all university PDFs, web markdowns, and structured fees
python -m app.ingestion.run_ingest
```

---

## 5. Starting the Backend Server

Start the FastAPI application with Uvicorn:

```bash
uvicorn app.main:app --port 8000 --reload
```

When started, you will see:
```text
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000
```

---

## 6. Accessing the Application

### 🌐 Frontend Website & Chatbot Widget
Open your browser and navigate to:
```text
http://127.0.0.1:8000/
```
* The mirrored CamTech University website will load with full assets (logos, faculty cards, and styles).
* Click the **speech bubble button** in the bottom-right corner to open the **CamTech University Inquiry Desk**.
* Use the directory buttons (Majors, Scholarships, Admissions, Tuition) or type custom questions.

---

### 📖 Interactive API Documentation (Swagger)
You can test the backend endpoints directly:
```text
http://127.0.0.1:8000/docs
```
Key endpoints:
- `POST /api/chat`: Send user message and receive grounded RAG answers with citations and token counts.
- `GET /api/health`: Check API status.
- `GET /api/threads/{thread_id}`: Retrieve multi-turn conversation history.

---

## 7. Running Evaluations & Benchmarks

To run the automated security guardrail tests and LLM-alone vs. RAG accuracy comparisons:

```bash
python scripts/run_full_eval.py
```

Results are saved automatically to:
- [`docs/attack_test_results.md`](docs/attack_test_results.md): Guardrail injection benchmark (Jailbreak, System Prompt Leak, Academic Dishonesty).
- [`docs/llm_alone_vs_rag_results.md`](docs/llm_alone_vs_rag_results.md): Grounded RAG accuracy vs. raw LLM baseline.

---

## 8. Troubleshooting

| Issue | Solution |
|---|---|
| **`connection to server at "localhost", port 5433 failed`** | Docker Desktop is not running. Launch Docker Desktop and run `docker compose up -d`. |
| **`WinError 10048 (port 8000 in use)`** | Another server instance is running. Stop previous Python tasks or change port: `uvicorn app.main:app --port 8001`. |
| **Browser not showing latest widget styles** | Hard-refresh your browser (`Ctrl + F5`) to bypass cached CSS. |
| **`GROQ_API_KEY missing`** | Ensure `.env` exists in the project root with a valid Groq API key. |
