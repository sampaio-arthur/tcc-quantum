from typing import List

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    documents: List[str]


class SearchResultOut(BaseModel):
    doc_id: str
    text: str
    score: float


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultOut]
