import json
from app.retrieval.retriever import retrieve


def evaluate_hit_at_3():
    with open("eval/test_questions.jsonl", "r", encoding="utf-8") as f:
        questions = [json.loads(line) for line in f]

    hits = 0
    total = 0
    failures = []

    for q in questions:
        if q["type"] in ["not-covered", "attack", "follow-up"]:
            continue

        total += 1
        results = retrieve(q["question"], top_k=3)

        hit = False
        for r in results:
            if r["metadata"]["source_file"] == q["source_doc"]:
                hit = True
                break

        if hit:
            hits += 1
        else:
            failures.append(
                {
                    "question": q["question"],
                    "expected_doc": q["source_doc"],
                    "retrieved_docs": [r["metadata"]["source_file"] for r in results]
                    if results
                    else ["NONE"],
                }
            )

    hit_rate = hits / total if total > 0 else 0

    print(f"Hit@3: {hit_rate * 100:.2f}% ({hits}/{total})")
    if failures:
        print("Failures:")
        for f in failures:
            print(f)


if __name__ == "__main__":
    evaluate_hit_at_3()
