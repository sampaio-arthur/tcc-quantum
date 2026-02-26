from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.routers.api_router import compat_router, router
from infrastructure.config import get_settings
from infrastructure.db.session import init_db


def create_app() -> FastAPI:
    settings = get_settings()
    if settings.embedding_dim != 384:
        raise RuntimeError("embedding_dim must match documents.embedding_vector dimension (current model column: 384).")
    if settings.quantum_dim != 2 ** settings.quantum_n_qubits:
        raise RuntimeError("quantum_dim must match 2**quantum_n_qubits for deterministic quantum encoder.")
    init_db(settings)

    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    app.include_router(compat_router)
    return app


app = create_app()
