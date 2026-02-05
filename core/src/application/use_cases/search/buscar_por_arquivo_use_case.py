from application.dtos import DocumentDTO
from application.interfaces import DocumentTextExtractor


class BuscarPorArquivoUseCase:
    def __init__(self, extractor: DocumentTextExtractor) -> None:
        self._extractor = extractor

    def execute(self, filename: str, content: bytes) -> list[DocumentDTO]:
        text = self._extractor.extract(filename, content)
        if not text:
            return []
        return [DocumentDTO(doc_id="uploaded-1", text=text)]
