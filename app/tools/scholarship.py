import json


def get_scholarship(scholarship_type: str) -> str:
    try:
        with open("data/structured/fees.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Scholarship data unavailable."

    for item in data.get("scholarships", []):
        if scholarship_type.lower() in item["type"].lower():
            return f"The {item['type']} scholarship covers {item['coverage_percentage']}% of tuition. Conditions: {item['conditions']}."

    return "Scholarship information for that type is not in our database."
