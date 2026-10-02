import re


def clean_text(text):
    # PostgreSQL cannot store NUL bytes
    text = text.replace("\x00", "")

    # Remove large blocks of empty lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove common boilerplate lines that are just navigation menus
    lines = text.split("\n")
    cleaned_lines = []

    boilerplate_keywords = [
        "Library",
        "Events/News",
        "Jobs",
        "Contact",
        "Campus Life",
        "Alumni Association",
        "Search for:",
    ]

    in_boilerplate = False
    for line in lines:
        if line.strip() in boilerplate_keywords:
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)
