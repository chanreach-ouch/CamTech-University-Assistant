from app.tools.tuition import get_tuition
from app.tools.scholarship import get_scholarship


def route_query(query: str):
    q_lower = query.lower()

    # Rule router
    if "tuition" in q_lower or "fee" in q_lower:
        # Very basic intent extraction
        if "architecture" in q_lower:
            return {
                "route": "tool",
                "tool": "tuition",
                "inputs": {"major": "Architecture"},
            }
        elif "cyber" in q_lower:
            return {
                "route": "tool",
                "tool": "tuition",
                "inputs": {"major": "Cyber Security"},
            }
        return {"route": "rag"}

    if "scholarship" in q_lower:
        if "women" in q_lower or "stem" in q_lower:
            return {
                "route": "tool",
                "tool": "scholarship",
                "inputs": {"type": "STEM Women"},
            }
        elif "merit" in q_lower:
            return {
                "route": "tool",
                "tool": "scholarship",
                "inputs": {"type": "Merit"},
            }
        return {"route": "rag"}

    return {"route": "rag"}
