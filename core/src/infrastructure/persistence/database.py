import os
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg://tcc:tcc@db:5432/tcc')

engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from infrastructure.persistence import models  # noqa: F401

    if engine.dialect.name == 'postgresql':
        with engine.begin() as connection:
            connection.execute(text('CREATE EXTENSION IF NOT EXISTS vector'))

    Base.metadata.create_all(bind=engine)
