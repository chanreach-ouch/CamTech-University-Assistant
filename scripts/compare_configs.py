import json
import time
from app.llm.groq_client import GroqClient
from app.llm.gemini_client import GeminiClient
from app.llm.prompts import GROUNDING_PROMPT
from app.retrieval.retriever import retrieve


def evaluate_configs():
    with open("eval/test_questions.jsonl", "r", encoding="utf-8") as f:
        questions = [
            json.loads(line) for line in f if json.loads(line)["type"] == "single-fact"
        ]

    groq = GroqClient()
    gemini = GeminiClient()

    results = {
        "groq": {"time": 0, "correct_approx": 0},
        "gemini": {"time": 0, "correct_approx": 0},
    }

    print("Running comparisons (Groq vs Gemini) on single-fact questions...")

    for q in questions[:5]:  # just run 5 for speed
        docs = retrieve(q["question"], top_k=3)
        sources_text = "\n".join([d["text"] for d in docs])
        sys_prompt = GROUNDING_PROMPT.format(sources=sources_text)

        # Groq
        t0 = time.time()
        g_res = groq.generate(sys_prompt, [{"role": "user", "content": q["question"]}])
        t1 = time.time()
        results["groq"]["time"] += t1 - t0
        # simplistic check
        if len(g_res["text"]) > 10 and "do not cover" not in g_res["text"]:
            results["groq"]["correct_approx"] += 1

        # Gemini
        t0 = time.time()
        gem_res = gemini.generate(
            sys_prompt, [{"role": "user", "content": q["question"]}]
        )
        t1 = time.time()
        results["gemini"]["time"] += t1 - t0
        if len(gem_res["text"]) > 10 and "do not cover" not in gem_res["text"]:
            results["gemini"]["correct_approx"] += 1

    print("Results:")
    print(
        f"Groq: Time={results['groq']['time']:.2f}s, Success Approx={results['groq']['correct_approx']}/5"
    )
    print(
        f"Gemini: Time={results['gemini']['time']:.2f}s, Success Approx={results['gemini']['correct_approx']}/5"
    )


if __name__ == "__main__":
    evaluate_configs()
