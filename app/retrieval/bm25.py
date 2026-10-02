import json
from rank_bm25 import BM25Okapi


class BM25Retriever:
    def __init__(self, data_file="data/processed/chunks.jsonl"):
        self.docs = []
        self.tokenized_corpus = []

        try:
            with open(data_file, "r", encoding="utf-8") as f:
                for line in f:
                    doc = json.loads(line)
                    self.docs.append(doc)
                    self.tokenized_corpus.append(doc["text"].lower().split())
        except FileNotFoundError:
            pass  # Handle empty safely for tests

        if self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)
        else:
            self.bm25 = None

    def search(self, query: str, top_k: int = 3):
        if not self.bm25:
            return []

        tokenized_query = query.lower().split()
        doc_scores = self.bm25.get_scores(tokenized_query)

        # Get top k indices
        top_indices = sorted(
            range(len(doc_scores)), key=lambda i: doc_scores[i], reverse=True
        )[:top_k]

        out = []
        for i in top_indices:
            if doc_scores[i] > 0:
                d = self.docs[i]
                out.append(
                    {
                        "text": d["text"],
                        "metadata": d["metadata"],
                        "score": doc_scores[i],
                    }
                )
        return out
