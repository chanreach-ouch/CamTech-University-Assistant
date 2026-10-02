from app.retrieval.pgvector_store import PgVectorStore
from app.retrieval.bm25 import BM25Retriever


def retrieve(query: str, top_k: int = 3):
    dense_store = PgVectorStore()
    bm25_store = BM25Retriever()

    try:
        dense_results = dense_store.search(query, top_k=top_k * 2)
    except Exception:
        dense_results = []

    bm25_results = bm25_store.search(query, top_k=top_k * 2)

    # Reciprocal Rank Fusion
    rrf_scores = {}
    docs_by_text = {}

    for rank, doc in enumerate(dense_results):
        text = doc["text"]
        if text not in rrf_scores:
            rrf_scores[text] = 0
            docs_by_text[text] = doc
        rrf_scores[text] += 1 / (60 + rank + 1)

    for rank, doc in enumerate(bm25_results):
        text = doc["text"]
        if text not in rrf_scores:
            rrf_scores[text] = 0
            docs_by_text[text] = doc
        rrf_scores[text] += 1 / (60 + rank + 1)

    # Sort by RRF score
    sorted_texts = sorted(rrf_scores.keys(), key=lambda t: rrf_scores[t], reverse=True)

    final_results = [docs_by_text[t] for t in sorted_texts[:top_k]]
    return final_results
