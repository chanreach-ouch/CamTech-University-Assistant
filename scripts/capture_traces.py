import json
import time


def capture_trace(query, context, response, latency_ms):
    trace = {
        "timestamp": time.time(),
        "query": query,
        "context_chunks_used": len(context),
        "latency_ms": latency_ms,
        "response": response,
    }
    with open("logs/trace.jsonl", "a") as f:
        f.write(json.dumps(trace) + "\n")


if __name__ == "__main__":
    print("Trace capturing module initialized.")
