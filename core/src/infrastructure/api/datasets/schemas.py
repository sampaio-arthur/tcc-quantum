from typing import List

from pydantic import BaseModel


class DatasetSummaryOut(BaseModel):
    dataset_id: str
    name: str
    description: str
    document_count: int
    query_count: int


class DatasetQueryOut(BaseModel):
    query_id: str
    query: str
    relevant_count: int


class DatasetDocumentOut(BaseModel):
    doc_id: str


class DatasetDetailOut(BaseModel):
    dataset_id: str
    name: str
    description: str
    queries: List[DatasetQueryOut]
    documents: List[DatasetDocumentOut]
