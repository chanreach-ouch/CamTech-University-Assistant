def calculate_hitk(retrieved_docs, target_doc_ids, k=3):
    """
    Calculates if the target document is within the top k retrieved documents.
    """
    top_k = retrieved_docs[:k]
    for doc in top_k:
        if doc.get("metadata", {}).get("source_file") in target_doc_ids:
            return 1
    return 0


def run_hitk_evaluation(test_cases):
    results = []
    total_score = 0

    for case in test_cases:
        query = case["query"]
        target = case["expected_source"]
        # Placeholder for actual retrieval logic
        retrieved = [{"metadata": {"source_file": "placeholder"}}]

        score = calculate_hitk(retrieved, [target])
        total_score += score
        results.append({"query": query, "hit@3": score})

    return {"average_hit@3": total_score / max(1, len(test_cases)), "results": results}
