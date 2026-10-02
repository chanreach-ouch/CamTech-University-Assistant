import cohere
import os
from typing import List


def embed_chunks(chunks: List[dict]) -> List[dict]:
    api_key = os.getenv("COHERE_API_KEY")
    if not api_key or api_key == "your-cohere-key-here":
        raise ValueError("COHERE_API_KEY is missing or invalid. Please set it in .env")

    co = cohere.Client(api_key)

    texts = [c["text"] for c in chunks]

    # Cohere has a limit on batch size, let's batch by 90 (limit is often 96)
    batch_size = 90
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        while True:
            try:
                response = co.embed(
                    texts=batch, model="embed-multilingual-v3.0", input_type="search_document"
                )
                embeddings.extend(response.embeddings)
                import time
                time.sleep(2) # Give a small buffer between normal requests too
                break
            except Exception as e:
                if "429" in str(e) or "rate limit" in str(e).lower() or "too many requests" in str(e).lower():
                    print(f"Rate limit hit at batch {i}. Sleeping for 60 seconds...")
                    import time
                    time.sleep(60)
                else:
                    raise e

    for chunk, emb in zip(chunks, embeddings):
        chunk["embedding"] = emb

    return chunks
