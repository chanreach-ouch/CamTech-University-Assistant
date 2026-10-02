from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.memory.models import Base, Thread, Message
import uuid

engine = create_engine(settings.DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MemoryStore:
    def __init__(self):
        pass

    def add_message(self, thread_id: str, role: str, content: str):
        db = SessionLocal()
        try:
            # Check if thread exists, create if not
            thread = db.query(Thread).filter(Thread.id == thread_id).first()
            if not thread:
                thread = Thread(id=thread_id)
                db.add(thread)

            msg = Message(thread_id=thread_id, role=role, content=content)
            db.add(msg)
            db.commit()
        finally:
            db.close()

    def get_history(self, thread_id: str, limit: int = 6):
        db = SessionLocal()
        try:
            messages = (
                db.query(Message)
                .filter(Message.thread_id == thread_id)
                .order_by(Message.created_at.desc())
                .limit(limit)
                .all()
            )
            return [{"role": m.role, "content": m.content} for m in reversed(messages)]
        finally:
            db.close()
