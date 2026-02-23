from __future__ import annotations

import itertools
from dataclasses import dataclass

try:
    import nltk
    from nltk.corpus import reuters
except Exception:  # pragma: no cover
    nltk = None
    reuters = None


@dataclass(slots=True)
class ReutersDatasetProvider:
    dataset_id: str = "reuters"
    max_docs: int = 300
    max_queries: int = 20

    def _normalize_dataset_id(self, dataset_id: str) -> str:
        value = (dataset_id or "").strip().lower().replace("_", "-")
        aliases = {
            "reuters": "reuters",
            "reuters-21578": "reuters",
            "reuters21578": "reuters",
            "nltk-reuters": "reuters",
            "nltkreuters": "reuters",
            "nltk-corpus-reuters": "reuters",
        }
        return aliases.get(value, value)

    def _ensure(self) -> bool:
        if not nltk or not reuters:
            return False
        try:
            reuters.fileids()
            return True
        except LookupError:
            try:
                nltk.download("reuters", quiet=True)
                return True
            except Exception:
                return False

    def list_datasets(self) -> list[dict]:
        detail = self.get_dataset(self.dataset_id)
        return [detail] if detail else []

    def get_dataset(self, dataset_id: str) -> dict | None:
        if self._normalize_dataset_id(dataset_id) != self.dataset_id:
            return None
        if self._ensure():
            fileids = reuters.fileids()
            docs = fileids[: self.max_docs]
            categories = reuters.categories()[: self.max_queries]
            return {
                "dataset_id": "reuters",
                "name": "Reuters-21578 (NLTK)",
                "description": "Subset reproducível do corpus Reuters via nltk.corpus.reuters",
                "document_count": len(docs),
                "query_count": len(categories),
                "queries": [
                    {"query_id": c, "query": c.replace("-", " "), "relevant_count": len(reuters.fileids(c))}
                    for c in categories
                ],
                "documents": [{"doc_id": d} for d in docs[:50]],
            }
        fallback_docs = self._fallback_documents()
        return {
            "dataset_id": "reuters",
            "name": "Reuters-like fallback",
            "description": "Fallback local when NLTK Reuters is unavailable",
            "document_count": len(fallback_docs),
            "query_count": 3,
            "queries": [
                {"query_id": "trade", "query": "trade tariffs imports exports", "relevant_count": 2},
                {"query_id": "earnings", "query": "company earnings profit quarter", "relevant_count": 2},
                {"query_id": "energy", "query": "oil production prices opec", "relevant_count": 2},
            ],
            "documents": [{"doc_id": d["doc_id"]} for d in fallback_docs],
        }

    def iter_documents(self, dataset_id: str):
        if self._normalize_dataset_id(dataset_id) != self.dataset_id:
            return iter(())
        if self._ensure():
            for fid in reuters.fileids()[: self.max_docs]:
                yield {
                    "doc_id": fid,
                    "text": reuters.raw(fid),
                    "metadata": {"categories": reuters.categories(fid)},
                }
            return
        for item in self._fallback_documents():
            yield item

    def iter_queries(self, dataset_id: str):
        if self._normalize_dataset_id(dataset_id) != self.dataset_id:
            return iter(())
        if self._ensure():
            for category in reuters.categories()[: self.max_queries]:
                yield {
                    "query_id": category,
                    "query_text": category.replace("-", " "),
                    "relevant_doc_ids": reuters.fileids(category)[:20],
                }
            return
        yield from [
            {"query_id": "trade", "query_text": "trade tariffs imports exports", "relevant_doc_ids": ["fb-1", "fb-2"]},
            {"query_id": "earnings", "query_text": "company earnings profit quarter", "relevant_doc_ids": ["fb-3", "fb-4"]},
            {"query_id": "energy", "query_text": "oil production prices opec", "relevant_doc_ids": ["fb-5", "fb-6"]},
        ]

    def _fallback_documents(self) -> list[dict]:
        return [
            {"doc_id": "fb-1", "text": "Trade talks advanced as import tariffs were reduced across several sectors.", "metadata": {"categories": ["trade"]}},
            {"doc_id": "fb-2", "text": "Exports rose sharply after a new customs agreement boosted trade flows.", "metadata": {"categories": ["trade"]}},
            {"doc_id": "fb-3", "text": "The company posted stronger quarterly earnings and improved profit margins.", "metadata": {"categories": ["earnings"]}},
            {"doc_id": "fb-4", "text": "Analysts revised profit expectations after the firm reported record revenue.", "metadata": {"categories": ["earnings"]}},
            {"doc_id": "fb-5", "text": "Oil prices moved higher as OPEC discussed production cuts this month.", "metadata": {"categories": ["energy"]}},
            {"doc_id": "fb-6", "text": "Energy markets reacted to lower crude output and refinery maintenance.", "metadata": {"categories": ["energy"]}},
        ]
