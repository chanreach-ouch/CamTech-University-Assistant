# CamTech University Assistant

An AI-powered RAG (Retrieval-Augmented Generation) assistant for CamTech University, designed to help students find information about admissions, tuition, scholarships, and academic rules.

## Setup & Architecture Guides
- **Teammate Overview & Code Guide:** See [TEAMMATE_GUIDE.md](TEAMMATE_GUIDE.md) for a complete explanation of `/app`, `/data`, `/frontend`, and the Hybrid RAG flow.
- **In-Depth Technical Architecture:** See [PROJECT_EXPLANATION.md](PROJECT_EXPLANATION.md) for deep engineering rationale and system breakdowns.
- **Runtime & Setup Guide:** See [RUNNING.md](RUNNING.md) for step-by-step setup, startup scripts, and evaluation benchmarks.

Quick start:
1. Copy `.env.example` to `.env` and fill in your API keys (`GROQ_API_KEY` for LLM, `COHERE_API_KEY` for embeddings).
2. Start the PostgreSQL vector database using Docker:
   ```bash
   docker compose up -d
   ```
3. Activate the virtual environment:
   ```bash
   .venv\Scripts\activate
   ```
4. Start the FastAPI backend server:
   ```bash
   uvicorn app.main:app --port 8000 --reload
   ```
5. Open your browser and navigate to `http://localhost:8000/` to use the chatbot on the mirrored site.

## Architecture
- **Vector Database**: PostgreSQL with `pgvector`
- **LLM**: Groq (primary) and Google Gemini (fallback)
- **Embeddings**: Cohere (`embed-multilingual-v3.0`)
- **Memory**: PostgreSQL (conversation threads)
- **Frontend**: Custom HTML/JS widget embedded in the university's mirrored site
