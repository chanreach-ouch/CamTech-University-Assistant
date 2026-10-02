from app.memory.store import SessionLocal
from app.memory.models import DocumentChunk
import cohere
import os


class PgVectorStore:
    def __init__(self):
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key or api_key == "your-cohere-key-here":
            self.co = None
        else:
            self.co = cohere.Client(api_key)

    def search(self, query: str, top_k: int = 3):
        if not self.co:
            return [
                {
                    "text": "Error: COHERE_API_KEY missing, cannot search dense vector.",
                    "metadata": {},
                }
            ]

        emb = self.co.embed(
            texts=[query], model="embed-multilingual-v3.0", input_type="search_query"
        ).embeddings[0]

        db = SessionLocal()
        try:
            # Query using L2 distance (cosine distance operator is <=>)
            results = (
                db.query(DocumentChunk)
                .order_by(DocumentChunk.embedding.cosine_distance(emb))
                .limit(top_k)
                .all()
            )

            out = []
            for r in results:
                # We calculate a pseudo-score since pgvector orders by distance (smaller is better)
                out.append(
                    {
                        "text": r.text,
                        "metadata": r.metadata_,
                        "score": 1.0,  # placeholder
                    }
                )
            return out
        except Exception as e:
            return [{"text": f"Error querying pgvector: {e}", "metadata": {}}]
        finally:
            db.close()
