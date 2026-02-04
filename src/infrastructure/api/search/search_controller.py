from typing import List

from fastapi import APIRouter, File, Form, UploadFile

from application.services import SearchService
from application.use_cases import RealizarBuscaUseCase
from domain.entities import Document
from infrastructure.api.search.file_reader import parse_upload
from infrastructure.api.search.schemas import SearchRequest, SearchResponse, SearchResultOut
from infrastructure.embeddings import LocalEmbedder
from infrastructure.quantum import SwapTestQuantumComparator

router = APIRouter(prefix="/search", tags=["search"])


def _build_service() -> SearchService:
    embedder = LocalEmbedder()
    comparator = SwapTestQuantumComparator()
    use_case = RealizarBuscaUseCase(embedder, comparator)
    return SearchService(use_case)


def _map_results(query: str, results) -> SearchResponse:
    return SearchResponse(
        query=query,
        results=[
            SearchResultOut(
                doc_id=item.document.doc_id,
                text=item.document.text,
                score=item.score,
            )
            for item in results
        ],
    )


@router.post("", response_model=SearchResponse)
def search(payload: SearchRequest) -> SearchResponse:
    docs = [Document(doc_id=f"doc-{i+1}", text=text) for i, text in enumerate(payload.documents)]
    if not docs:
        return SearchResponse(query=payload.query, results=[])

    service = _build_service()
    results = service.buscar(payload.query, docs)
    return _map_results(payload.query, results)


@router.post("/file", response_model=SearchResponse)
def search_file(query: str = Form(...), file: UploadFile = File(...)) -> SearchResponse:
    text = parse_upload(file)
    if not text:
        return SearchResponse(query=query, results=[])

    docs = [Document(doc_id="uploaded-1", text=text)]
    service = _build_service()
    results = service.buscar(query, docs)
    return _map_results(query, results)
