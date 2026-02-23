from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.config import Settings, get_settings
from infrastructure.db.models import Base

_engine = None
_SessionLocal = None


def get_engine(settings: Settings | None = None):
    global _engine
    if _engine is None:
        cfg = settings or get_settings()
        connect_args = {"check_same_thread": False} if cfg.database_url.startswith("sqlite") else {}
        _engine = create_engine(cfg.database_url, future=True, pool_pre_ping=True, connect_args=connect_args)
    return _engine


def get_session_factory(settings: Settings | None = None):
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(settings), autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)
    return _SessionLocal


def init_db(settings: Settings | None = None) -> None:
    engine = get_engine(settings)
    if engine.dialect.name == "postgresql":
        with engine.begin() as conn:
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)


def db_session() -> Generator[Session, None, None]:
    session = get_session_factory()()
    try:
        yield session
    finally:
        session.close()
