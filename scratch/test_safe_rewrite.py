from dotenv import load_dotenv
load_dotenv()

def safe_rewrite(history, latest_query):
    if not history:
        return latest_query

    q_lower = latest_query.lower()
    standalone_keywords = ["camtech", "major", "scholarship", "tuition", "admission", "program", "apply", "requirement"]
    if any(k in q_lower for k in standalone_keywords) and len(latest_query.split()) >= 4:
        return latest_query

    if len(latest_query.split()) > 10:
        return latest_query

    hist_text = "\n".join([f"{m['role'].capitalize()}: {m['content'][:200]}" for m in history[-4:]])
    prompt = f"Given this recent conversation:\n{hist_text}\n\nRewrite this follow-up question to be standalone: \"{latest_query}\"\nOnly return the rewritten question. Do not answer it."

    try:
        from app.llm.factory import get_llm
        llm = get_llm()
        response = llm.generate(system="You are a query rewriting assistant.", messages=[{"role": "user", "content": prompt}], max_tokens=60)
        rewritten = response["text"].strip().strip('"').strip("'")
        if not rewritten or "Error" in rewritten or "provided sources" in rewritten.lower() or len(rewritten) > 200:
            return latest_query
        return rewritten
    except Exception:
        return latest_query

from app.memory.store import MemoryStore
mem = MemoryStore()
hist = mem.get_history("user-mwk5s")
q = "What majors and degree programs are offered at CamTech?"
print("Safe rewritten:", safe_rewrite(hist, q))
