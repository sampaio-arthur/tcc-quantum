from application.dtos import DocumentDTO, SearchResponseDTO, SearchResultDTO
from domain.entities import Document


def document_dto_to_entity(dto: DocumentDTO) -> Document:
    return Document(doc_id=dto.doc_id, text=dto.text)


def document_entity_to_dto(entity: Document) -> DocumentDTO:
    return DocumentDTO(doc_id=entity.doc_id, text=entity.text)


def result_entity_to_dto(query: str, results, answer: str | None = None) -> SearchResponseDTO:
    return SearchResponseDTO(
        query=query,
        results=[
            SearchResultDTO(doc_id=item.document.doc_id, text=item.document.text, score=item.score)
            for item in results
        ],
        answer=answer,
    )
