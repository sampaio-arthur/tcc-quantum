import re

from application.dtos import DocumentDTO
from application.interfaces import DocumentTextExtractor


def _chunk_text(text: str, max_chars: int = 800, overlap: int = 150) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text).strip()
    if not cleaned:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    chunks: list[str] = []
    current = ""

    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        if len(current) + len(sentence) + 1 <= max_chars:
            current = f"{current} {sentence}".strip()
            continue
        if current:
            chunks.append(current)
        current = sentence

    if current:
        chunks.append(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped: list[str] = []
        for index, chunk in enumerate(chunks):
            if index == 0:
                overlapped.append(chunk)
                continue
            prefix = chunks[index - 1][-overlap:]
            overlapped.append(f"{prefix} {chunk}".strip())
        chunks = overlapped

    return chunks


class BuscarPorArquivoUseCase:
    def __init__(self, extractor: DocumentTextExtractor) -> None:
        self._extractor = extractor

    def execute(self, filename: str, content: bytes) -> list[DocumentDTO]:
        text = self._extractor.extract(filename, content)
        if not text:
            return []
        chunks = _chunk_text(text)
        if not chunks:
            return []
        return [
            DocumentDTO(doc_id=f"uploaded-{index + 1}", text=chunk)
            for index, chunk in enumerate(chunks)
        ]
