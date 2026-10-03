import uuid
from fastapi import APIRouter, HTTPException
from app.schemas import ChatRequest, ChatResponse
from app.memory.store import MemoryStore
from app.memory.rewrite import rewrite_query
from app.guardrails.input_guard import check_input
from app.guardrails.output_check import check_output
from app.router.router import route_query
from app.retrieval.retriever import retrieve
from app.llm.factory import get_llm
from app.llm.prompts import GROUNDING_PROMPT, TOOL_PROMPT
from app.trace.tracer import Tracer
from app.tools.tuition import get_tuition
from app.tools.scholarship import get_scholarship

router = APIRouter()
memory = MemoryStore()


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    tracer = Tracer(trace_id=str(uuid.uuid4()))
    tracer.start_span("total_request")

    # 1. Input Guardrail
    tracer.start_span("input_guard")
    guard_res = check_input(req.message)
    tracer.end_span("input_guard", guard_res)
    if not guard_res["safe"]:
        return ChatResponse(response=f"I cannot answer that: {guard_res['reason']}")

    # 2. Memory & Rewrite
    tracer.start_span("memory_rewrite")
    history = memory.get_history(req.thread_id)
    query = rewrite_query(history, req.message)
    memory.add_message(req.thread_id, "user", req.message)
    tracer.end_span("memory_rewrite", {"original": req.message, "rewritten": query})

    # 3. Router
    tracer.start_span("router")
    route_info = route_query(query)
    tracer.end_span("router", route_info)

    llm = get_llm()
    tokens = 0
    sources = []

    if route_info["route"] == "tool":
        # Tool execution
        tracer.start_span("tool_execution")
        if route_info["tool"] == "tuition":
            tool_res = get_tuition(route_info["inputs"]["major"])
        elif route_info["tool"] == "scholarship":
            tool_res = get_scholarship(route_info["inputs"]["type"])
        else:
            tool_res = "Tool not found."
        tracer.end_span("tool_execution", {"result": tool_res})

        # LLM Synthesis
        sys_prompt = TOOL_PROMPT.format(tool_result=tool_res)
        llm_res = llm.generate(sys_prompt, [{"role": "user", "content": query}])
        raw_output = llm_res["text"]
        tokens = llm_res["tokens_in"] + llm_res["tokens_out"]
    else:
        # RAG Pipeline
        tracer.start_span("retrieval")
        docs = retrieve(query, top_k=3)
        # Assuming chunk_filter logic is done inside retriever or here
        sources = [d.get("metadata", {}).get("source_file", d.get("metadata", {}).get("source", "unknown")) for d in docs]

        sources_text = ""
        for d in docs:
            meta = d.get("metadata", {})
            source = meta.get("source_file", meta.get("source", "unknown"))
            year = meta.get("academic_year", meta.get("year", "unknown"))
            sources_text += f"\n[Doc: {source}, Year: {year}]\n{d['text']}\n"

        tracer.end_span("retrieval", {"num_docs": len(docs)})

        tracer.start_span("llm_generation")
        sys_prompt = GROUNDING_PROMPT.format(sources=sources_text)
        llm_res = llm.generate(sys_prompt, [{"role": "user", "content": query}])
        raw_output = llm_res["text"]
        tokens = llm_res["tokens_in"] + llm_res["tokens_out"]
        tracer.end_span("llm_generation", {"tokens": tokens})

    # Output Guardrail
    tracer.start_span("output_guard")
    out_guard = check_output(raw_output)
    final_output = out_guard["text"]
    tracer.end_span("output_guard", {"safe": out_guard["safe"]})

    # Save Assistant message
    memory.add_message(req.thread_id, "assistant", final_output)

    tracer.end_span("total_request")

    return ChatResponse(
        response=final_output, sources=sources if sources else None, tokens_used=tokens
    )
