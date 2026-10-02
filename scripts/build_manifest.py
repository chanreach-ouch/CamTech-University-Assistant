import os
import re
from pathlib import Path
import json


def find_academic_year(text):
    # Looking for formats like 2023-2024, 2023/2024, or just a year if explicitly labeled "Academic Year 2023"
    match = re.search(
        r"(?:academic\s+year\s*|AY\s*)(20\d{2}(?:[-/]\d{2,4})?)", text, re.IGNORECASE
    )
    if match:
        return match.group(1)
    # Just look for year-year
    match2 = re.search(r"\b(202\d-202\d)\b", text)
    if match2:
        return match2.group(1)
    return "unknown — ask team to confirm"


def extract_source_url(text):
    match = re.search(r"Source:\s*(https?://[^\s]+)", text)
    return match.group(1) if match else "unknown"


def has_personal_data(text):
    # Very basic regex for individual emails/phones, excluding generic ones like info@, hr@, or standard office numbers if possible
    # We will just flag if we see an email that isn't info/contact/hr
    emails = re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)
    phones = re.findall(r"(?:\+855|0)\s*\d{2,3}\s*\d{3}\s*\d{3,4}", text)

    suspicious_emails = [
        e
        for e in emails
        if not any(
            g in e.lower() for g in ["info@", "contact@", "hr@", "admin@", "admission@"]
        )
    ]

    if (
        suspicious_emails or len(phones) > 3
    ):  # If there are many phones or non-generic emails
        return True
    return False


def check_boilerplate(text):
    # Check if file is just menu items
    lines = text.split("\n")
    short_lines = [l for l in lines if len(l.strip()) > 0 and len(l.strip()) < 30]
    if (
        len(lines) > 0
        and (len(short_lines) / len([l for l in lines if l.strip()])) > 0.8
    ):
        return True
    return False


def process_markdown(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception:
        return {"needs_review": True, "flags": ["encoding/read_error"]}

    words = len(text.split())
    flags = []

    if words < 50:
        flags.append("near-empty")

    if check_boilerplate(text):
        flags.append("menu-only-boilerplate")

    if has_personal_data(text):
        flags.append("contains_personal_data")

    year = find_academic_year(text)
    url = extract_source_url(text)

    return {
        "type": "Web (MD)",
        "count": f"{words} words",
        "url": url,
        "year": year,
        "needs_review": len(flags) > 0,
        "flags": flags,
    }


def process_pdf(file_path):
    # We don't have PyPDF2 installed by default, so we'll just check file size and return placeholders for pages
    size_kb = os.path.getsize(file_path) / 1024
    flags = []

    # We flag all PDFs for review to ensure tables/Khmer extracted correctly (since we haven't extracted them yet)
    flags.append("check_pdf_extraction")

    return {
        "type": "PDF",
        "count": f"~ {int(size_kb)} KB",
        "url": "local-file",
        "year": "unknown — ask team to confirm",
        "needs_review": True,
        "flags": flags,
    }


def main():
    base_dir = Path("data/raw")
    dirs_to_check = ["camtech_web", "camtech_pdfs", "manual"]

    manifest_rows = []

    for d in dirs_to_check:
        dir_path = base_dir / d
        if not dir_path.exists():
            continue

        for root, _, files in os.walk(dir_path):
            for file in files:
                file_path = Path(root) / file
                if file.endswith(".md"):
                    info = process_markdown(file_path)
                elif file.endswith(".pdf"):
                    info = process_pdf(file_path)
                else:
                    info = {
                        "type": "Other",
                        "count": "?",
                        "url": "N/A",
                        "year": "unknown — ask team to confirm",
                        "needs_review": True,
                        "flags": ["unknown format"],
                    }

                manifest_rows.append(
                    {
                        "filename": f"{d}/{file}",
                        "type": info["type"],
                        "count": info["count"],
                        "url": info["url"],
                        "year": info["year"],
                        "needs_review": info["needs_review"],
                        "flags": ", ".join(info["flags"]) if info["flags"] else "None",
                    }
                )

    # Generate Markdown
    manifest_rows.sort(key=lambda x: (x["needs_review"], x["filename"]), reverse=True)

    with open("docs/document_manifest.md", "w", encoding="utf-8") as f:
        f.write("# Document Manifest\n\n")
        f.write(
            "| Filename | Type | Size/Count | Source URL | Academic Year | Flags / Needs Review |\n"
        )
        f.write("|---|---|---|---|---|---|\n")

        for row in manifest_rows:
            review_flag = "⚠️ YES" if row["needs_review"] else "NO"
            f.write(
                f"| {row['filename']} | {row['type']} | {row['count']} | {row['url']} | {row['year']} | {review_flag} ({row['flags']}) |\n"
            )

    print(
        f"Manifest written to docs/document_manifest.md. Processed {len(manifest_rows)} files."
    )


if __name__ == "__main__":
    main()
