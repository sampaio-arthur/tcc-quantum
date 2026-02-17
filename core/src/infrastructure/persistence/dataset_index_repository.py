import math
from dataclasses import dataclass
from typing import Iterable

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from application.dtos import DocumentDTO
from infrastructure.persistence.models import DatasetDocumentIndex


@dataclass(frozen=True)
class IndexedDocument:
    doc_id: str
    text: str
    embedding: list[float]


def _normalize(values: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [value / norm for value in values]


def _project_vector(values: list[float], dim: int = 64) -> list[float]:
    if not values:
        return [0.0] * dim

    projected = values[:dim]
    if len(projected) < dim:
        projected = projected + ([0.0] * (dim - len(projected)))
    return _normalize(projected)


def _to_float_list(values: Iterable[float]) -> list[float]:
    return [float(value) for value in values]


class DatasetIndexRepository:
    def __init__(self, db: Session, provider: str, model: str) -> None:
        self._db = db
        self._provider = provider
        self._model = model

    def get_documents(self, dataset_id: str) -> list[IndexedDocument]:
        stmt = (
            select(DatasetDocumentIndex)
            .where(DatasetDocumentIndex.dataset_id == dataset_id)
            .where(DatasetDocumentIndex.embedder_provider == self._provider)
            .where(DatasetDocumentIndex.embedder_model == self._model)
            .order_by(DatasetDocumentIndex.id.asc())
        )
        rows = self._db.execute(stmt).scalars().all()

        documents: list[IndexedDocument] = []
        for row in rows:
            payload = row.payload or {}
            embedding = payload.get('full_vector')
            if not isinstance(embedding, list):
                continue
            documents.append(
                IndexedDocument(
                    doc_id=row.doc_id,
                    text=row.text,
                    embedding=_to_float_list(embedding),
                )
            )
        return documents

    def count_documents(self, dataset_id: str) -> int:
        return len(self.get_documents(dataset_id))

    def replace_documents(
        self,
        dataset_id: str,
        documents: list[DocumentDTO],
        embeddings: list[list[float]],
    ) -> int:
        if len(documents) != len(embeddings):
            raise ValueError('Documents and embeddings must have the same size')

        self._db.execute(
            delete(DatasetDocumentIndex)
            .where(DatasetDocumentIndex.dataset_id == dataset_id)
            .where(DatasetDocumentIndex.embedder_provider == self._provider)
            .where(DatasetDocumentIndex.embedder_model == self._model)
        )

        for doc, vector in zip(documents, embeddings):
            float_vector = _to_float_list(vector)
            self._db.add(
                DatasetDocumentIndex(
                    dataset_id=dataset_id,
                    doc_id=doc.doc_id,
                    text=doc.text,
                    vector=_project_vector(float_vector),
                    payload={
                        'full_vector': float_vector,
                        'dimension': len(float_vector),
                    },
                    embedder_provider=self._provider,
                    embedder_model=self._model,
                )
            )

        self._db.commit()
        return len(documents)
