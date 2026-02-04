from application.interfaces import DocumentTextExtractor


class LerArquivoUseCase:
    def __init__(self, extractor: DocumentTextExtractor) -> None:
        self._extractor = extractor

    def execute(self, filename: str, content: bytes) -> str:
        return self._extractor.extract(filename, content)
