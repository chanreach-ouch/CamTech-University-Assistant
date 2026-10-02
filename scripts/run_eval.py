import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.evaluation.llm_alone_vs_rag import run_llm_vs_rag_test
from app.evaluation.hitk import run_hitk_evaluation

if __name__ == "__main__":
    print("Starting full evaluation suite...")

    # 1. Run Hit@3
    test_cases = [
        {
            "query": "How much is Software Engineering?",
            "expected_source": "tuition_fees.md",
        }
    ]
    hitk_results = run_hitk_evaluation(test_cases)
    print(f"Hit@3 Score: {hitk_results['average_hit@3']}")

    # 2. Run LLM vs RAG
    questions = ["What are the scholarships available?"]
    run_llm_vs_rag_test(questions)

    print("Evaluation completed successfully.")
