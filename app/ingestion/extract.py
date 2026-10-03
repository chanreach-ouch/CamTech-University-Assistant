import re
from pathlib import Path
import os


def extract_markdown(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract source URL and year if present
    source_url = "unknown"
    year = "unknown"

    match_url = re.search(r"Source:\s*(https?://[^\s]+)", content)
    if match_url:
        source_url = match_url.group(1)
        content = content[: match_url.start()]  # Remove footer

    match_year = re.search(
        r"(?:academic\s+year\s*|AY\s*)(20\d{2}(?:[-/]\d{2,4})?)", content, re.IGNORECASE
    )
    if match_year:
        year = match_year.group(1)
    else:
        match_year2 = re.search(r"\b(202\d-202\d)\b", content)
        if match_year2:
            year = match_year2.group(1)

    return {
        "text": content,
        "source_file": file_path.name,
        "source_url": source_url,
        "academic_year": year,
        "doc_type": "web",
    }


def extract_pdf(file_path):
    try:
        import pymupdf as fitz  # PyMuPDF (replaces deprecated fitz import)

        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
    except Exception as e:
        text = f"Error extracting PDF: {e}"

    return {
        "text": text,
        "source_file": file_path.name,
        "source_url": "local-pdf",
        "academic_year": "unknown",
        "doc_type": "pdf",
    }


def extract_all(data_dir):
    data_dir = Path(data_dir)
    docs = []

    for root, _, files in os.walk(data_dir):
        for file in files:
            file_path = Path(root) / file
            if file.endswith(".md"):
                docs.append(extract_markdown(file_path))
            elif file.endswith(".pdf"):
                docs.append(extract_pdf(file_path))
    return docs
