# Optimization Log

- **Embedding Speed**: Switched from sequential API calls to batched embedding (batch size 90) via Cohere.
- **Retrieval Quality**: Implemented Reciprocal Rank Fusion (RRF) to merge BM25 keyword search results with pgvector dense search results.
- **LLM Speed**: Migrated from OpenAI/Gemini to Groq for generation, decreasing TTFT (Time To First Token) from ~800ms to ~150ms.
