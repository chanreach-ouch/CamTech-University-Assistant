from pydantic import BaseModel
from typing import Optional


class ChatRequest(BaseModel):
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    sources: Optional[list] = None
    tokens_used: int = 0
