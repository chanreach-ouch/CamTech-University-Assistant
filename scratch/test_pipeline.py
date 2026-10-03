from dotenv import load_dotenv
load_dotenv()
from app.memory.store import MemoryStore
from app.memory.rewrite import rewrite_query
from app.router.router import route_query
from app.retrieval.retriever import retrieve
from app.llm.prompts import GROUNDING_PROMPT
from app.llm.factory import get_llm
from app.guardrails.output_check import check_output

mem = MemoryStore()
hist = mem.get_history("user-mwk5s")
print("History length:", len(hist))

query = rewrite_query(hist, "What majors and degree programs are offered at CamTech?")
print("Rewritten query:", query)

docs = retrieve(query, top_k=5)
print("Docs count:", len(docs))

sources_text = ""
for d in docs:
    meta = d.get("metadata", {})
    source = meta.get("source_file", meta.get("source", "unknown"))
    year = meta.get("academic_year", meta.get("year", "unknown"))
    sources_text += f"\n[Doc: {source}, Year: {year}]\n{d['text']}\n"

sys_prompt = GROUNDING_PROMPT.format(sources=sources_text)
llm = get_llm()
llm_res = llm.generate(sys_prompt, [{"role": "user", "content": query}])
print("\n--- LLM RAW ---")
print(llm_res["text"])

out_guard = check_output(llm_res["text"])
print("\n--- OUTPUT GUARD ---")
print(out_guard)
