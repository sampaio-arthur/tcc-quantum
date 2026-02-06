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
class SearchResponseDTO:
    query: str
    results: List[SearchResultDTO]
    answer: Optional[str] = None
