from app.llm.factory import get_llm


def rewrite_query(history, latest_query):
    if not history:
        return latest_query

    q_lower = latest_query.lower()
    
    # Standalone queries that already name key subjects should NOT be rewritten
    standalone_keywords = [
        "camtech", "major", "scholarship", "tuition", "fee", 
        "admission", "program", "apply", "requirement", "entrance", "exam"
    ]
    if any(k in q_lower for k in standalone_keywords) and len(latest_query.split()) >= 4:
        return latest_query

    # If it's long, it's definitely standalone
    if len(latest_query.split()) > 10:
        return latest_query

    # For short follow-up questions, format history as context block
    hist_text = "\n".join([f"{m['role'].capitalize()}: {m['content'][:150]}" for m in history[-4:]])
    prompt = f"Given this recent conversation context:\n{hist_text}\n\nRewrite this follow-up question to be standalone: \"{latest_query}\"\nOnly return the rewritten question. Do not answer it."

    try:
        llm = get_llm()
        response = llm.generate(
            system="You are a query rewriting assistant. Given context and a follow-up question, return a clear, standalone search query. Never answer the question.",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        rewritten = response["text"].strip().strip('"').strip("'")

        # Sanity guard: discard if model hallucinated an answer or failed
        if not rewritten or "Error" in rewritten or "provided sources" in rewritten.lower() or len(rewritten) > 200:
            return latest_query

        return rewritten
    except Exception:
        return latest_query
