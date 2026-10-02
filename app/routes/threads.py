from fastapi import APIRouter, HTTPException
from app.memory.store import MemoryStore

router = APIRouter()
memory = MemoryStore()


@router.get("/threads/{thread_id}")
def get_thread(thread_id: str):
    history = memory.get_history(thread_id, limit=50)
    if not history:
        raise HTTPException(status_code=404, detail="Thread not found or empty")
    return {"thread_id": thread_id, "messages": history}
