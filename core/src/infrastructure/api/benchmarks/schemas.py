from pydantic import BaseModel


class BenchmarkLabelIn(BaseModel):
    dataset_id: str
    query_text: str
    ideal_answer: str


class BenchmarkLabelOut(BaseModel):
    benchmark_id: str
    dataset_id: str
    query_text: str
    ideal_answer: str
    relevant_doc_ids: list[str]


class BenchmarkLabelListOut(BaseModel):
    items: list[BenchmarkLabelOut]
