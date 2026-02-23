from __future__ import annotations

import os
from functools import lru_cache

from pydantic import BaseModel, Field

try:
    from pydantic_settings import BaseSettings, SettingsConfigDict
except Exception:  # pragma: no cover
    class BaseSettings(BaseModel):  # type: ignore
        def __init__(self, **data):
            env_values = {}
            model_fields = getattr(self.__class__, "model_fields", {})
            for field_name in model_fields:
                env_name = field_name.upper()
                raw = os.getenv(env_name)
                if raw is not None:
                    env_values[field_name] = raw
            env_values.update(data)
            super().__init__(**env_values)

    def SettingsConfigDict(**kwargs):  # type: ignore
        return kwargs


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "dev"
    app_name: str = "quantum-semantic-search"
    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173"])

    database_url: str = "sqlite:///./app.db"

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_minutes: int = 60 * 24 * 7

    embedding_dim: int = 384
    quantum_dim: int = 16
    quantum_n_qubits: int = 4
    classical_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    seed: int = 42

    password_reset_expire_minutes: int = 30

    require_auth_for_indexing: bool = True
    require_admin_for_indexing: bool = False


@lru_cache
def get_settings() -> Settings:
    return Settings()
