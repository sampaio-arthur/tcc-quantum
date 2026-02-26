from __future__ import annotations

import os
from functools import lru_cache
from urllib.parse import quote_plus

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

    database_url: str = ""
    db_scheme: str = "postgresql+psycopg"
    db_host: str = "db"
    db_port: int = 5432
    db_name: str = "tcc"
    db_user: str = "tcc"
    db_password: str = "tcc"

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

    def __init__(self, **data):
        super().__init__(**data)

        # Backward-compatible resolution:
        # 1) explicit DATABASE_URL (if non-empty)
        # 2) fragmented DB_* variables (if any were provided)
        # 3) sqlite local default
        fields_set = set(getattr(self, "model_fields_set", set()) or getattr(self, "__fields_set__", set()))
        has_db_parts_configured = bool(fields_set & {"db_scheme", "db_host", "db_port", "db_name", "db_user", "db_password"})

        if (self.database_url or "").strip():
            resolved_database_url = self.database_url
        elif has_db_parts_configured:
            user = quote_plus(self.db_user)
            password = quote_plus(self.db_password)
            resolved_database_url = f"{self.db_scheme}://{user}:{password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:
            resolved_database_url = "sqlite:///./app.db"

        self.database_url = resolved_database_url
        if self.app_env.lower() not in {"dev", "development", "test"} and self.jwt_secret.strip() == "change-me":
            raise ValueError("JWT_SECRET must be configured in non-development environments.")


@lru_cache
def get_settings() -> Settings:
    return Settings()
