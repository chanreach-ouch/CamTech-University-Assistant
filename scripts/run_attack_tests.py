import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.evaluation.attack_runner import test_attacks

if __name__ == "__main__":
    print("Running attack resilience tests...")
    results = test_attacks("eval/attacks.jsonl")

    passed = sum(1 for r in results if r["blocked"])
    total = len(results)

    print(f"Blocked {passed}/{total} attacks.")
