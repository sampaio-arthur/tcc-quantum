import math
from typing import Iterable, List

import httpx

from application.interfaces import Embedder


class GeminiEmbedder(Embedder):
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-embedding-001",
        timeout_seconds: float = 30.0,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for GeminiEmbedder")

        normalized_model = model_name.strip().removeprefix("models/")
        if normalized_model == "text-embedding-004":
            normalized_model = "gemini-embedding-001"

        self._api_key = api_key
        self._model_name = normalized_model
        self._timeout_seconds = timeout_seconds
        self._endpoints = [
            f"https://generativelanguage.googleapis.com/v1beta/models/{self._model_name}:embedContent",
            f"https://generativelanguage.googleapis.com/v1/models/{self._model_name}:embedContent",
        ]

    def embed_texts(self, texts: Iterable[str]) -> List[List[float]]:
        values = [text for text in texts]
        if not values:
            return []

        embeddings: List[List[float]] = []
        with httpx.Client(timeout=self._timeout_seconds) as client:
            for text in values:
                payload = {
                    "content": {
                        "parts": [{"text": text}],
                    }
                }
                data = self._post_with_fallback(client=client, payload=payload)

                vector = data.get("embedding", {}).get("values")
                if not vector:
                    raise RuntimeError("Gemini embedding response missing 'embedding.values'")

                embeddings.append(_normalize(vector))

        return embeddings

    def _post_with_fallback(self, client: httpx.Client, payload: dict) -> dict:
        last_response: httpx.Response | None = None

        for endpoint in self._endpoints:
            response = client.post(
                endpoint,
                params={"key": self._api_key},
                json=payload,
            )

            if response.status_code < 400:
                return response.json()

            last_response = response
            if response.status_code != 404:
                break

        assert last_response is not None
        raise RuntimeError(
            "Gemini embedding request failed "
            f"({last_response.status_code}): {last_response.text}"
        )


def _normalize(vector: List[float]) -> List[float]:
    norm = math.sqrt(sum(component * component for component in vector))
    if norm == 0:
        return vector
    return [component / norm for component in vector]

