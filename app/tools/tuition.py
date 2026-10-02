import json


def get_tuition(major: str) -> str:
    try:
        with open("data/structured/fees.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return "Tuition data unavailable."

    for item in data.get("tuition", []):
        if major.lower() in item["major"].lower():
            return f"The tuition fee for {item['major']} is {item['fee_per_year']} {item['currency']} per year."

    return "Tuition information for that major is not in our database."
