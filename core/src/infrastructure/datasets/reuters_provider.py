from __future__ import annotations

from dataclasses import dataclass

from domain.exceptions import ValidationError

try:
    import nltk
    from nltk.corpus import reuters
except Exception:  # pragma: no cover
    nltk = None
    reuters = None


@dataclass(slots=True)
class ReutersDatasetProvider:
    dataset_id: str = "reuters"
    max_docs: int | None = None
    max_queries: int | None = None

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
                reuters.fileids()
                return True
            except Exception:
                return False

    def _ensure_or_raise(self) -> None:
        if self._ensure():
            return
        raise ValidationError(
            "Reuters-21578 (NLTK) is unavailable. Install/download the NLTK Reuters corpus and retry."
        )

    def list_datasets(self) -> list[dict]:
        detail = self.get_dataset(self.dataset_id)
        return [detail] if detail else []

    def _limit(self, values: list[str], max_items: int | None) -> list[str]:
        return values if max_items is None else values[:max_items]

    def get_dataset(self, dataset_id: str) -> dict | None:
        if self._normalize_dataset_id(dataset_id) != self.dataset_id:
            return None
        self._ensure_or_raise()
        fileids = reuters.fileids()
        docs = self._limit(fileids, self.max_docs)
        categories = self._limit(reuters.categories(), self.max_queries)
        return {
            "dataset_id": "reuters",
            "name": "Reuters-21578 (NLTK)",
            "provider": "nltk.corpus.reuters",
            "source_url": "https://www.nltk.org/howto/corpus.html",
            "reference_urls": [
                "https://www.nltk.org/howto/corpus.html",
                "https://www.nltk.org/book/ch02.html",
                "http://kdd.ics.uci.edu/databases/reuters21578/reuters21578.html",
            ],
            "description": "Corpus Reuters-21578 via nltk.corpus.reuters (snapshot completo por padrao quando sem limites)",
            "subset": {"max_docs": self.max_docs, "max_queries": self.max_queries},
            "document_count": len(docs),
            "query_count": len(categories),
            "queries": [
                {"query_id": c, "query": c.replace("-", " "), "relevant_count": len(reuters.fileids(c))}
                for c in categories
            ],
            "documents": [{"doc_id": d} for d in docs[:50]],
        }

    def iter_documents(self, dataset_id: str):
        if self._normalize_dataset_id(dataset_id) != self.dataset_id:
            return iter(())
        self._ensure_or_raise()
        for fid in self._limit(reuters.fileids(), self.max_docs):
            yield {
                "doc_id": fid,
                "text": reuters.raw(fid),
                "metadata": {"categories": reuters.categories(fid)},
            }

    def iter_queries(self, dataset_id: str):
        if self._normalize_dataset_id(dataset_id) != self.dataset_id:
            return iter(())
        self._ensure_or_raise()
        for category in self._limit(reuters.categories(), self.max_queries):
            yield {
                "query_id": category,
                "query_text": category.replace("-", " "),
                "relevant_doc_ids": reuters.fileids(category),
            }
