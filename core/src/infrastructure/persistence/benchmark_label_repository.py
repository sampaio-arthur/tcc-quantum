from dataclasses import dataclass
import re

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from infrastructure.persistence.models import BenchmarkGroundTruth


@dataclass(frozen=True)
class BenchmarkLabelDTO:
    benchmark_id: str
    dataset_id: str
    query_text: str
    ideal_answer: str
    relevant_doc_ids: list[str]


def _normalize_query(text: str) -> str:
    lowered = text.strip().lower()
    lowered = re.sub(r'[^a-z0-9\s]', '', lowered)
    return re.sub(r'\s+', ' ', lowered).strip()


class BenchmarkLabelRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def list_labels(self, dataset_id: str) -> list[BenchmarkLabelDTO]:
        rows = (
            self._db.execute(
                select(BenchmarkGroundTruth)
                .where(BenchmarkGroundTruth.dataset_id == dataset_id)
                .order_by(BenchmarkGroundTruth.created_at.desc())
            )
            .scalars()
            .all()
        )
        return [self._to_dto(row) for row in rows]

    def find_by_benchmark_id(self, dataset_id: str, benchmark_id: str) -> BenchmarkLabelDTO | None:
        if not benchmark_id.isdigit():
            return None

        row = (
            self._db.execute(
                select(BenchmarkGroundTruth)
                .where(BenchmarkGroundTruth.dataset_id == dataset_id)
                .where(BenchmarkGroundTruth.id == int(benchmark_id))
            )
            .scalars()
            .first()
        )
        if not row:
            return None
        return self._to_dto(row)

    def find_by_query_text(self, dataset_id: str, query_text: str) -> BenchmarkLabelDTO | None:
        normalized = _normalize_query(query_text)
        if not normalized:
            return None

        row = (
            self._db.execute(
                select(BenchmarkGroundTruth)
                .where(BenchmarkGroundTruth.dataset_id == dataset_id)
                .where(BenchmarkGroundTruth.query_key == normalized)
            )
            .scalars()
            .first()
        )
        if not row:
            return None
        return self._to_dto(row)

    def upsert_label(
        self,
        dataset_id: str,
        query_text: str,
        ideal_answer: str,
        relevant_doc_ids: list[str],
    ) -> BenchmarkLabelDTO:
        normalized = _normalize_query(query_text)
        if not normalized:
            raise ValueError('Query vazia para gabarito')

        existing = (
            self._db.execute(
                select(BenchmarkGroundTruth)
                .where(BenchmarkGroundTruth.dataset_id == dataset_id)
                .where(BenchmarkGroundTruth.query_key == normalized)
            )
            .scalars()
            .first()
        )

        doc_ids = [item.strip() for item in relevant_doc_ids if item and item.strip()]

        if existing:
            existing.query_text = query_text.strip()
            existing.ideal_answer = ideal_answer.strip()
            existing.relevant_doc_ids = doc_ids
            row = existing
        else:
            row = BenchmarkGroundTruth(
                dataset_id=dataset_id,
                query_key=normalized,
                query_text=query_text.strip(),
                ideal_answer=ideal_answer.strip(),
                relevant_doc_ids=doc_ids,
            )
            self._db.add(row)

        self._db.commit()
        self._db.refresh(row)
        return self._to_dto(row)

    def delete_label(self, dataset_id: str, benchmark_id: str) -> bool:
        if not benchmark_id.isdigit():
            return False

        result = self._db.execute(
            delete(BenchmarkGroundTruth)
            .where(BenchmarkGroundTruth.dataset_id == dataset_id)
            .where(BenchmarkGroundTruth.id == int(benchmark_id))
        )
        self._db.commit()
        return result.rowcount > 0

    @staticmethod
    def _to_dto(row: BenchmarkGroundTruth) -> BenchmarkLabelDTO:
        return BenchmarkLabelDTO(
            benchmark_id=str(row.id),
            dataset_id=row.dataset_id,
            query_text=row.query_text,
            ideal_answer=row.ideal_answer,
            relevant_doc_ids=list(row.relevant_doc_ids or []),
        )
