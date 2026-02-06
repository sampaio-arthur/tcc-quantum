from fastapi import APIRouter, File, Form, UploadFile

from application.dtos import DocumentDTO, SearchFileRequestDTO, SearchRequestDTO
from application.services import SearchService
from application.use_cases import BuscarPorArquivoUseCase, RealizarBuscaUseCase
from infrastructure.api.search.file_reader import PdfTxtDocumentTextExtractor
from infrastructure.api.search.schemas import SearchRequest as SearchRequestSchema
from infrastructure.api.search.schemas import SearchResponse as SearchResponseSchema
from infrastructure.embeddings import LocalEmbedder
from infrastructure.quantum import SwapTestQuantumComparator

router = APIRouter(prefix="/search", tags=["search"])


def _build_service() -> SearchService:
    embedder = LocalEmbedder()
    comparator = SwapTestQuantumComparator()
    buscar_use_case = RealizarBuscaUseCase(embedder, comparator)
    buscar_por_arquivo_use_case = BuscarPorArquivoUseCase(PdfTxtDocumentTextExtractor())
    return SearchService(buscar_use_case, buscar_por_arquivo_use_case)


def _to_response_schema(response) -> SearchResponseSchema:
    return SearchResponseSchema(
        query=response.query,
        results=[
            {"doc_id": item.doc_id, "text": item.text, "score": item.score}
            for item in response.results
        ],
        answer=response.answer,
    )


@router.post("", response_model=SearchResponseSchema)
def search(payload: SearchRequestSchema) -> SearchResponseSchema:
    docs = [DocumentDTO(doc_id=f"doc-{i+1}", text=text) for i, text in enumerate(payload.documents)]
    service = _build_service()
    dto = SearchRequestDTO(query=payload.query, documents=docs)
    response = service.buscar_por_texto(dto)
    return _to_response_schema(response)


@router.post("/file", response_model=SearchResponseSchema)
def search_file(query: str = Form(...), file: UploadFile = File(...)) -> SearchResponseSchema:
    content = file.file.read()
    service = _build_service()
    dto = SearchFileRequestDTO(query=query, filename=file.filename or "", content=content)
    response = service.buscar_por_arquivo(dto)
    return _to_response_schema(response)
