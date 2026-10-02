import logging
import time

logging.basicConfig(
    filename="docs/traces.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


class Tracer:
    def __init__(self, trace_id: str):
        self.trace_id = trace_id
        self.spans = []

    def start_span(self, name: str):
        span = {"name": name, "start": time.time()}
        self.spans.append(span)
        logging.info(f"Trace {self.trace_id} | STARTED: {name}")

    def end_span(self, name: str, data: dict = None):
        for s in reversed(self.spans):
            if s["name"] == name:
                duration = time.time() - s["start"]
                log_msg = (
                    f"Trace {self.trace_id} | ENDED: {name} | Duration: {duration:.4f}s"
                )
                if data:
                    log_msg += f" | Data: {data}"
                logging.info(log_msg)
                return
