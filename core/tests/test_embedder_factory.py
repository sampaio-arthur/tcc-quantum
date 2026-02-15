from unittest.mock import patch

import pytest

from infrastructure.embeddings.factory import build_embedder_from_env


def test_build_embedder_from_env_gemini_default(monkeypatch):
    monkeypatch.delenv("EMBEDDER_PROVIDER", raising=False)
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.delenv("GEMINI_EMBEDDING_MODEL", raising=False)

    with patch("infrastructure.embeddings.factory.GeminiEmbedder") as gemini_cls:
        sentinel = object()
        gemini_cls.return_value = sentinel

        embedder = build_embedder_from_env()

        assert embedder is sentinel
        gemini_cls.assert_called_once_with(
            api_key="dummy-key",
            model_name="gemini-embedding-001",
        )


def test_build_embedder_from_env_gemini_requires_key(monkeypatch):
    monkeypatch.setenv("EMBEDDER_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    with pytest.raises(RuntimeError, match="GEMINI_API_KEY"):
        build_embedder_from_env()


def test_build_embedder_from_env_gemini(monkeypatch):
    monkeypatch.setenv("EMBEDDER_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "dummy-key")
    monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")

    with patch("infrastructure.embeddings.factory.GeminiEmbedder") as gemini_cls:
        sentinel = object()
        gemini_cls.return_value = sentinel

        embedder = build_embedder_from_env()

        assert embedder is sentinel
        gemini_cls.assert_called_once_with(
            api_key="dummy-key",
            model_name="gemini-embedding-001",
        )


def test_build_embedder_from_env_unsupported_provider(monkeypatch):
    monkeypatch.setenv("EMBEDDER_PROVIDER", "local")

    with pytest.raises(ValueError, match="Use 'gemini'"):
        build_embedder_from_env()

