import re


def check_output(text: str):
    # Check if the output leaked rules
    if "<sources>" in text or "<tool_result>" in text:
        return {
            "safe": False,
            "text": "I can only provide information about CamTech University based on official documents.",
        }

    # Check if the output abstained
    if "The provided sources do not cover this question" in text:
        return {"safe": True, "text": text}

    # In a full implementation, we'd check if all facts actually have a citation
    # For this demo, we just ensure it doesn't look like a system prompt leak

    return {"safe": True, "text": text}
