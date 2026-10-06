import os
import sys
import uuid
import json
import urllib.request
import pymupdf
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import text

# Add workspace root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8")
load_dotenv()

from app.ingestion.clean import clean_text
from app.ingestion.chunk import chunk_text
from app.ingestion.embed import embed_chunks
from app.memory.store import SessionLocal, engine
from app.memory.models import DocumentChunk, Base
from app.retrieval.retriever import retrieve

PDF_URL = "https://cdnm.heyzine.com/files/uploaded/c14349bd8777af9414f62c4bd44ae62f9456ce40.pdf"
LOCAL_PDF = Path("data/raw/camtech_pdfs/CamTech_Prospectus_Guide_2024_2025.pdf")
CHUNKS_JSONL = Path("data/processed/chunks.jsonl")


def ensure_download():
    LOCAL_PDF.parent.mkdir(parents=True, exist_ok=True)
    if not LOCAL_PDF.exists():
        print(f"Downloading flipbook PDF from {PDF_URL}...")
        req = urllib.request.Request(PDF_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req) as resp, open(LOCAL_PDF, "wb") as f:
            f.write(resp.read())
        print(f"Downloaded to {LOCAL_PDF} ({LOCAL_PDF.stat().st_size} bytes)")
    else:
        print(f"PDF already exists at {LOCAL_PDF} ({LOCAL_PDF.stat().st_size} bytes)")


def extract_and_chunk():
    doc = pymupdf.open(str(LOCAL_PDF))
    total_pages = len(doc)
    print(f"Extracting and chunking {total_pages} pages...")

    chunks = []
    for page_idx in range(total_pages):
        page_num = page_idx + 1
        page_text = doc[page_idx].get_text().strip()
        if not page_text or len(page_text) < 15:
            continue

        cleaned = clean_text(page_text)
        header = (
            f"Document: CamTech University Prospectus & Information Guide 2024/2025\n"
            f"Page: {page_num} of {total_pages}\n"
            f"Source URL: https://heyzine.com/flip-book/c14349bd87.html\n\n"
        )
        content = header + cleaned

        metadata = {
            "source_file": LOCAL_PDF.name,
            "source_url": "https://heyzine.com/flip-book/c14349bd87.html",
            "academic_year": "2024/2025",
            "doc_type": "pdf",
            "page": page_num,
            "title": "CamTech University Prospectus & Information Guide 2024/2025",
        }

        page_chunks = chunk_text(content, metadata, max_tokens=450, overlap=50)
        chunks.extend(page_chunks)

    print(f"Generated {len(chunks)} chunks from {total_pages} pages.")
    return chunks


def update_chunks_jsonl(new_chunks):
    CHUNKS_JSONL.parent.mkdir(parents=True, exist_ok=True)
    existing_lines = []
    if CHUNKS_JSONL.exists():
        with open(CHUNKS_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                src = data.get("metadata", {}).get("source_file")
                # Exclude old chunks of this exact file if any
                if src != LOCAL_PDF.name:
                    existing_lines.append(line.strip())

    print(f"Retained {len(existing_lines)} existing chunks from other documents.")

    with open(CHUNKS_JSONL, "w", encoding="utf-8") as f:
        for line in existing_lines:
            f.write(line + "\n")
        for c in new_chunks:
            f.write(json.dumps({"text": c["text"], "metadata": c["metadata"]}, ensure_ascii=False) + "\n")

    print(f"Updated {CHUNKS_JSONL} (now contains {len(existing_lines) + len(new_chunks)} total chunks).")


def store_in_database(embedded_chunks):
    print("Connecting to PostgreSQL to store new chunks...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # Delete any previous chunks for this file so ingestion is idempotent
        res = db.execute(
            text("DELETE FROM document_chunks WHERE metadata->>'source_file' = :src"),
            {"src": LOCAL_PDF.name}
        )
        db.commit()
        if res.rowcount:
            print(f"Cleaned up {res.rowcount} previous chunks for {LOCAL_PDF.name}")

        objects = []
        for c in embedded_chunks:
            doc = DocumentChunk(
                id=str(uuid.uuid4()),
                text=c["text"],
                metadata_=c["metadata"],
                embedding=c["embedding"],
            )
            objects.append(doc)

        db.bulk_save_objects(objects)
        db.commit()
        print(f"Successfully stored {len(objects)} chunks into PostgreSQL.")
        
        # Check total count in DB
        total_in_db = db.query(DocumentChunk).count()
        print(f"Total chunks now in database: {total_in_db}")
    finally:
        db.close()


def update_fees_json():
    fees_path = Path("data/structured/fees.json")
    fees_path.parent.mkdir(parents=True, exist_ok=True)
    
    fee_data = {
        "academic_year": "2024/2025",
        "source": "CamTech Prospectus & Information Guide 2024/2025 (Page 11-12)",
        "source_url": "https://heyzine.com/flip-book/c14349bd87.html",
        "undergraduate": {
            "administration_fee_per_year_usd": 200,
            "terms_per_year": 3,
            "faculties": [
                {
                    "faculty": "Faculty of Engineering",
                    "majors": [
                        "Cyber Security",
                        "Data Science and Artificial Intelligence Engineering",
                        "Robotics and Automation Engineering",
                        "Software Engineering"
                    ],
                    "fee_per_term_usd": 1350,
                    "fee_per_year_usd": 4000,
                    "total_4_years_usd": 16000
                },
                {
                    "faculty": "Faculty of Sustainable Built Environment",
                    "majors": [
                        "Architecture",
                        "Interior Design",
                        "Urban Planning",
                        "Industrial Energy Management"
                    ],
                    "fee_per_term_usd": 1350,
                    "fee_per_year_usd": 4000,
                    "total_4_years_usd": 16000
                },
                {
                    "faculty": "Faculty of Arts, Humanities and Social Sciences",
                    "majors": [
                        "Teaching English as a Second Language (TESOL)",
                        "English for Business and Commerce",
                        "Media and Communication Technology",
                        "Educational Technology"
                    ],
                    "fee_per_term_usd": 1184,
                    "fee_per_year_usd": 3500,
                    "total_4_years_usd": 14000
                },
                {
                    "faculty": "Faculty of Business and Management",
                    "majors": [
                        "Risk Management and Business Intelligence",
                        "Innovation and Entrepreneurship",
                        "Sports and Recreation Management",
                        "Manufacturing Management"
                    ],
                    "fee_per_term_usd": 1184,
                    "fee_per_year_usd": 3500,
                    "total_4_years_usd": 14000
                }
            ],
            "entrance_exams": [
                {"subject": "Mathematics", "duration_minutes": 90},
                {"subject": "English", "duration_minutes": 60},
                {"subject": "Interview", "duration_minutes": "Variable"}
            ]
        },
        "graduate": {
            "administration_fee_per_year_usd": 250,
            "application_fee_usd": 30,
            "contact": {
                "name": "Dr. May Thu",
                "role": "Assistant Dean of School of Graduate Studies",
                "email": "may.thu@camtech.edu.kh",
                "phone": "+85512699633"
            },
            "cambodian_students": {
                "masters_per_term_usd": 1550,
                "masters_per_year_usd": 4500,
                "doctoral_per_term_usd": 1700,
                "doctoral_per_year_usd": 5000
            },
            "international_students": {
                "masters_per_year_usd": 5000,
                "doctoral_per_year_usd": 6000
            },
            "programs": [
                "Environmental Technology",
                "Technology Management",
                "Technology Governance",
                "Data Science",
                "Artificial Intelligence",
                "Cyber Security",
                "Industrial Technology",
                "Agriculture Technology",
                "Education Technology",
                "Financial Technology",
                "Science and Technology Studies"
            ]
        },
        "scholarships": [
            {"type": "100% STEM Women", "coverage_percentage": 100, "conditions": "Maintain 3.0 GPA"},
            {"type": "Merit Scholarship", "coverage_percentage": 50, "conditions": "Top 10% in entrance exam"}
        ]
    }
    
    with open(fees_path, "w", encoding="utf-8") as f:
        json.dump(fee_data, f, indent=4, ensure_ascii=False)
    print(f"Updated {fees_path} with official 2024/2025 fee structure.")


def test_retrieval():
    print("\n--- Verifying Hybrid Retrieval with newly ingested data ---")
    test_queries = [
        "Who founded CamTech University?",
        "What are the opening hours and online catalog for the CamTech library?",
        "How much is the tuition fee for Engineering and what is the administration fee?",
        "Tell me about the student accommodation at Rung Reung Condo",
        "Who is the Assistant Dean of Graduate Studies and how can I contact them?"
    ]
    
    for q in test_queries:
        print(f"\nQuery: '{q}'")
        results = retrieve(q, top_k=2)
        for i, r in enumerate(results):
            src = r.get("metadata", {}).get("source_file", "unknown")
            page = r.get("metadata", {}).get("page", "N/A")
            snippet = r.get("text", "").replace("\n", " ")[:160]
            print(f"  Result {i+1} [{src}, Page {page}]: {snippet}...")


if __name__ == "__main__":
    ensure_download()
    chunks = extract_and_chunk()
    print("Embedding chunks with Cohere...")
    embedded = embed_chunks(chunks)
    update_chunks_jsonl(chunks)
    store_in_database(embedded)
    update_fees_json()
    test_retrieval()
    print("\nFlipbook ingestion completed successfully!")
