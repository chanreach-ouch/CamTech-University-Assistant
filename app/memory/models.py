from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import declarative_base
from pgvector.sqlalchemy import Vector
import datetime

Base = declarative_base()


class Thread(Base):
    __tablename__ = "threads"

    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    thread_id = Column(String, index=True)
    role = Column(String)  # 'user', 'assistant', 'system'
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True)
    text = Column(Text)
    metadata_ = Column("metadata", JSON)
    embedding = Column(Vector(1024))  # Cohere multilingual-v3 has 1024 dims
