import os

from application.interfaces import Embedder

from .gemini_embedder import GeminiEmbedder


def build_embedder_from_env() -> Embedder:
    provider = os.getenv("EMBEDDER_PROVIDER", "gemini").strip().lower()

    if provider == "gemini":
        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        model_name = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is required when EMBEDDER_PROVIDER=gemini")
        return GeminiEmbedder(api_key=api_key, model_name=model_name)

    raise ValueError(
        "Unsupported EMBEDDER_PROVIDER. Use 'gemini'. "
        f"Received: {provider!r}"
    )

