from dataclasses import dataclass
from typing import List, Optional

from application.dtos.common import DocumentDTO


@dataclass(frozen=True)
class SearchRequestDTO:
    query: str
    documents: List[DocumentDTO]


@dataclass(frozen=True)
class SearchFileRequestDTO:
    query: str
    filename: str
    content: bytes


@dataclass(frozen=True)
class SearchResultDTO:
    doc_id: str
    text: str
    score: float


@dataclass(frozen=True)
class SearchMetricsDTO:
    recall_at_k: Optional[float]
    mrr: Optional[float]
    ndcg_at_k: Optional[float]
    latency_ms: float
    k: int
    candidate_k: int
    has_labels: bool


@dataclass(frozen=True)
class SearchResponseLiteDTO:
    results: List[SearchResultDTO]
    answer: Optional[str] = None
    metrics: Optional[SearchMetricsDTO] = None


@dataclass(frozen=True)
class SearchComparisonDTO:
    classical: SearchResponseLiteDTO
    quantum: SearchResponseLiteDTO


@dataclass(frozen=True)
class SearchResponseDTO:
    query: str
    mode: str
    results: List[SearchResultDTO]
    answer: Optional[str] = None
    metrics: Optional[SearchMetricsDTO] = None
    comparison: Optional[SearchComparisonDTO] = None
