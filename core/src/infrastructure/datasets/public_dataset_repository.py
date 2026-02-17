from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetSummary:
    dataset_id: str
    name: str
    description: str
    document_count: int
    query_count: int


class PublicDatasetRepository:
    def __init__(self, data_path: Path | None = None) -> None:
        if data_path is None:
            data_path = Path(__file__).resolve().parents[3] / 'data' / 'public_datasets.json'
        self._data_path = data_path

    def list_datasets(self) -> list[DatasetSummary]:
        datasets = self._load().get('datasets', [])
        return [
            DatasetSummary(
                dataset_id=item['id'],
                name=item.get('name', item['id']),
                description=item.get('description', ''),
                document_count=len(item.get('documents', [])),
                query_count=len(item.get('queries', [])),
            )
            for item in datasets
        ]

    def get_dataset(self, dataset_id: str) -> dict[str, Any] | None:
        datasets = self._load().get('datasets', [])
        for item in datasets:
            if item.get('id') == dataset_id:
                return item
        return None

    def get_query(self, dataset_id: str, query_id: str) -> dict[str, Any] | None:
        dataset = self.get_dataset(dataset_id)
        if not dataset:
            return None
        for query in dataset.get('queries', []):
            if query.get('query_id') == query_id:
                return query
        return None

    @lru_cache(maxsize=1)
    def _load(self) -> dict[str, Any]:
        if not self._data_path.exists():
            return {'datasets': []}
        with self._data_path.open('r', encoding='utf-8') as handle:
            return json.load(handle)
