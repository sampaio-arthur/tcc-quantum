import io

from fastapi import HTTPException
from pypdf import PdfReader

from application.interfaces import DocumentTextExtractor


class PdfTxtDocumentTextExtractor(DocumentTextExtractor):
    def extract(self, filename: str, content: bytes) -> str:
        name = (filename or "").lower()
        if name.endswith(".txt"):
            return self._read_txt(content)
        if name.endswith(".pdf"):
            return self._read_pdf(content)
        raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt or .pdf")

    @staticmethod
    def _read_txt(content: bytes) -> str:
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            return content.decode("latin-1")

    @staticmethod
    def _read_pdf(content: bytes) -> str:
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(pages).strip()
