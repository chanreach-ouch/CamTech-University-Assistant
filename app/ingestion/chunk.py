import tiktoken
import re


def chunk_text(text, metadata, max_tokens=500, overlap=50):
    enc = tiktoken.get_encoding("cl100k_base")

    # Simple semantic split by paragraphs/headers first
    paragraphs = re.split(r"\n\s*\n", text)

    chunks = []
    current_chunk = []
    current_tokens = 0

    for p in paragraphs:
        p_tokens = len(enc.encode(p))
        if current_tokens + p_tokens > max_tokens and current_chunk:
            # Join current chunk, save it
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({"text": chunk_text, "metadata": metadata})
            # Start new chunk with overlap (last paragraph from previous)
            current_chunk = [current_chunk[-1]] if current_chunk else []
            current_tokens = len(enc.encode(current_chunk[0])) if current_chunk else 0

        current_chunk.append(p)
        current_tokens += p_tokens

    if current_chunk:
        chunk_text = "\n\n".join(current_chunk)
        chunks.append({"text": chunk_text, "metadata": metadata})

    return chunks
