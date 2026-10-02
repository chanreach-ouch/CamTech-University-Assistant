import os
import json
import uuid
from typing import List
from app.ingestion.extract import extract_all
from app.ingestion.clean import clean_text
from app.ingestion.chunk import chunk_text
from app.ingestion.embed import embed_chunks

from app.memory.store import SessionLocal, engine
from app.memory.models import DocumentChunk, Base
from sqlalchemy import text


def store_in_pgvector(chunks: List[dict]):
    # Ensure pgvector extension exists
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Optional: Clear old chunks
        db.query(DocumentChunk).delete()

        objects = []
        for c in chunks:
            doc = DocumentChunk(
                id=str(uuid.uuid4()),
                text=c["text"],
                metadata_=c["metadata"],
                embedding=c["embedding"],
            )
            objects.append(doc)

        db.bulk_save_objects(objects)
        db.commit()
        return len(objects)
    finally:
        db.close()


def run_pipeline(data_dir="data/raw"):
    print("1. Extracting data...")
    docs = extract_all(data_dir)
    print(f"   Extracted {len(docs)} documents.")

    print("2. Cleaning data...")
    for d in docs:
        d["text"] = clean_text(d["text"])

    print("3. Chunking data...")
    all_chunks = []
    for d in docs:
        metadata = {
            "source_file": d["source_file"],
            "source_url": d["source_url"],
            "academic_year": d["academic_year"],
            "doc_type": d["doc_type"],
        }
        file_chunks = chunk_text(d["text"], metadata)
        all_chunks.extend(file_chunks)
    print(f"   Generated {len(all_chunks)} chunks.")

    os.makedirs("data/processed", exist_ok=True)
    with open("data/processed/chunks.jsonl", "w", encoding="utf-8") as f:
        for c in all_chunks:
            f.write(json.dumps({"text": c["text"], "metadata": c["metadata"]}) + "\n")

    print("4. Embedding chunks (calls Cohere)...")
    try:
        embedded_chunks = embed_chunks(all_chunks)
    except Exception as e:
        print(f"Embedding failed: {e}")
        return False

    print("5. Storing in PostgreSQL (pgvector)...")
    try:
        stored_count = store_in_pgvector(embedded_chunks)
        print(f"   Stored {stored_count} vectors in PostgreSQL.")
    except Exception as e:
        print(f"PostgreSQL storage failed: {e}")
        return False

    print("Pipeline completed successfully.")

    with open("data/processed/stage_report.json", "w", encoding="utf-8") as f:
        json.dump(
            {"status": "success", "docs": len(docs), "chunks": len(all_chunks)}, f
        )

    return True
