import json


def test_attacks(filepath: str):
    print(f"Loading attacks from {filepath}...")
    try:
        with open(filepath, "r") as f:
            attacks = [json.loads(line) for line in f]
    except FileNotFoundError:
        print(f"File {filepath} not found.")
        return []

    results = []
    for attack in attacks:
        print(f"Testing Attack: {attack['type']}")
        # Placeholder for actual attack guardrail logic
        blocked = True
        results.append(
            {"attack": attack["prompt"], "type": attack["type"], "blocked": blocked}
        )

    return results
