def filter_chunks(chunks):
    # This prevents injection inside a retrieved chunk.
    # In a real app, we might scan chunks for instructions masquerading as data.
    # For now, we just pass them through safely.
    safe_chunks = []
    for c in chunks:
        if "ignore all previous instructions" not in c["text"].lower():
            safe_chunks.append(c)
    return safe_chunks
