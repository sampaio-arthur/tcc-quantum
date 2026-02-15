from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.persistence.database import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversations = relationship('Conversation', back_populates='user', cascade='all, delete-orphan')


class Conversation(Base):
    __tablename__ = 'conversations'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True, nullable=False)
    title: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='conversations')
    messages = relationship('Message', back_populates='conversation', cascade='all, delete-orphan')


class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey('conversations.id'), index=True, nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    conversation = relationship('Conversation', back_populates='messages')


class SearchRun(Base):
    __tablename__ = 'search_runs'

    id: Mapped[int] = mapped_column(primary_key=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    top_k: Mapped[int] = mapped_column(Integer, nullable=False)
    candidate_k: Mapped[int] = mapped_column(Integer, nullable=False)
    embedder_provider: Mapped[str] = mapped_column(String(64), nullable=False)
    embedder_model: Mapped[str] = mapped_column(String(128), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vectors = relationship('SearchVectorRecord', back_populates='run', cascade='all, delete-orphan')


class SearchVectorRecord(Base):
    __tablename__ = 'search_vector_records'

    id: Mapped[int] = mapped_column(primary_key=True)
    run_id: Mapped[int] = mapped_column(ForeignKey('search_runs.id'), index=True, nullable=False)
    kind: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    doc_id: Mapped[str | None] = mapped_column(String(255), index=True)
    score: Mapped[float | None] = mapped_column(Float)
    vector: Mapped[list[float] | None] = mapped_column(Vector(64))
    payload: Mapped[dict | None] = mapped_column(JSON)
    text_excerpt: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    run = relationship('SearchRun', back_populates='vectors')
