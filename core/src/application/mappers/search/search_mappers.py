from typing import Iterable

from application.dtos import DocumentDTO, SearchResultDTO
from domain.entities import Document


def document_dto_to_entity(dto: DocumentDTO) -> Document:
    return Document(doc_id=dto.doc_id, text=dto.text)


def document_entity_to_dto(entity: Document) -> DocumentDTO:
    return DocumentDTO(doc_id=entity.doc_id, text=entity.text)


def results_to_dtos(results: Iterable) -> list[SearchResultDTO]:
    return [
        SearchResultDTO(doc_id=item.document.doc_id, text=item.document.text, score=item.score)
        for item in results
    ]
