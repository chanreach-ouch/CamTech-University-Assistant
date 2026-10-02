import re


def check_input(query: str):
    # Direct injection or system prompt leak checks
    suspicious = [
        "ignore all previous instructions",
        "system prompt",
        "you are a",
        "forget",
        "bypass",
    ]

    query_lower = query.lower()
    for s in suspicious:
        if s in query_lower:
            return {"safe": False, "reason": "Potential prompt injection detected."}

    # Basic check for off-topic / harmful
    harmful = ["hack", "kill", "bomb", "destroy"]
    for h in harmful:
        if h in query_lower:
            return {"safe": False, "reason": "Harmful content detected."}

    return {"safe": True}
