from app.llm.factory import get_llm
from app.llm.prompts import REWRITE_PROMPT


def rewrite_query(history, latest_query):
    if not history:
        return latest_query

    # Heuristic: if it's very short, it's likely a follow-up
    if len(latest_query.split()) > 10:
        # If it's long, probably standalone, save an LLM call
        return latest_query

    llm = get_llm()
    messages = history.copy()
    messages.append({"role": "user", "content": latest_query})

    response = llm.generate(system=REWRITE_PROMPT, messages=messages, max_tokens=100)
    rewritten = response["text"].strip()

    # If the LLM failed or abstained, just use original
    if not rewritten or "Error" in rewritten:
        return latest_query

    return rewritten
