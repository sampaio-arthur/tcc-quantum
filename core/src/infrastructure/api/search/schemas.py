from typing import List, Optional

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    documents: List[str]
    mode: str = "classical"
    top_k: int = 5
    candidate_k: int = 20


class DatasetSearchRequest(BaseModel):
    dataset_id: str
    query_id: str
    mode: str = "compare"
    top_k: int = 5
    candidate_k: int = 20


class SearchResultOut(BaseModel):
    doc_id: str
    text: str
    score: float


class SearchMetricsOut(BaseModel):
    recall_at_k: Optional[float] = None
    mrr: Optional[float] = None
    ndcg_at_k: Optional[float] = None
    latency_ms: float
    k: int
    candidate_k: int
    has_labels: bool


class SearchResponseLite(BaseModel):
    results: List[SearchResultOut]
    answer: Optional[str] = None
    metrics: Optional[SearchMetricsOut] = None


class SearchComparisonOut(BaseModel):
    classical: SearchResponseLite
    quantum: SearchResponseLite


class SearchResponse(BaseModel):
    query: str
    mode: str
    results: List[SearchResultOut]
    answer: Optional[str] = None
    metrics: Optional[SearchMetricsOut] = None
    comparison: Optional[SearchComparisonOut] = None
