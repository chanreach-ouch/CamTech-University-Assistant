# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Stack
FastAPI backend (Python), PostgreSQL with pgvector (Docker), and HTML/CSS/JavaScript floating widget embedded on the mirrored CamTech University WordPress site.

## Users
Primary users are prospective university applicants, enrolled students, and academic evaluators/teachers reviewing the project. They require immediate, reliable, and grounded answers regarding degree programs, scholarships, tuition fees, application steps, and campus life.

## Product Purpose
Deliver an intelligent, reliable AI assistant for CamTech University that answers user questions with strict grounding in official university materials, preventing hallucinations, blocking malicious prompt injection attacks, and providing an intuitive embedded conversational interface.

## Positioning
Unlike generic chatbots or hallucinating LLMs, CamTech University Assistant uses a production-grade RAG pipeline with dense vector search (Cohere + pgvector), strict input/output guardrails, fallback routing, and transparent source attribution, ensuring high academic integrity and factual compliance.

## Operating Context
Operates as a floating widget overlay on the mirrored CamTech University website (`http://localhost:8000/`) and standalone REST API endpoints (`/api/chat`, `/api/health`, `/api/threads/{thread_id}`). Used during web browsing sessions on both desktop and mobile devices.

## Capabilities and Constraints
- Real-time conversational AI chat powered by Groq LLM (`qwen/qwen3.8-27b`).
- Dense vector retrieval via Cohere embeddings (`embed-multilingual-v3.0`) over 1,412 indexed university document chunks in PostgreSQL.
- Structured tool lookups for specific fees and scholarships from `fees.json`.
- Keyword-based input guardrails to intercept prompt injections, jailbreaks, and harmful inputs.
- Multi-turn conversational memory with session thread persistence.
- Client-side markdown rendering with `marked.js` and responsive widget styles.
- Constraints: PostgreSQL on custom port 5433 via Docker; relies on Groq and Cohere API availability.

## Brand Commitments
- Deep navy primary brand color (`#1a365d` / `#0056b3`) and clean white/neutral surfaces reflecting CamTech University's institutional identity.
- Clean typography (`Segoe UI`, `Roboto`, `Helvetica`, `Arial`, sans-serif) with clear hierarchy and readable line spacing.
- Courteous, academic, and helpful voice that answers directly without robotic preamble.

## Evidence on Hand
- Raw data: Scraped markdown files from `camtech.edu.kh` (`data/raw/camtech_web/`), official university PDFs (`data/raw/camtech_pdfs/`), and structured fees data (`data/structured/fees.json`).
- Live database: PostgreSQL with 1,412 vectors in `document_chunks`.
- Evaluation results: `docs/attack_test_results.md` (3/5 attacks blocked) and `docs/llm_alone_vs_rag_results.md`.

## Product Principles
1. **Factual Grounding Over Speculation:** Always prioritize verified institutional documents; decline politely if information is missing rather than inventing facts.
2. **Seamless Institutional Aesthetic:** The conversational interface must look and feel like an official, integral part of CamTech University's digital presence.
3. **Transparent Provenance:** Present clean, deduplicated source references for factual claims without cluttering reading flow.
4. **Resilient & Guarded:** Defend against malicious prompting and jailbreaks while remaining forgiving of natural user typos and varied phrasing.
