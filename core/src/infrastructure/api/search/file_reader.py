import io

from fastapi import HTTPException
from pypdf import PdfReader

from application.interfaces import DocumentTextExtractor


class PdfTxtDocumentTextExtractor(DocumentTextExtractor):
    def extract(self, filename: str, content: bytes) -> str:
        if not content:
            raise HTTPException(status_code=400, detail="Arquivo vazio ou invalido")
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
        if not content.startswith(b"%PDF-"):
            raise HTTPException(status_code=400, detail="Arquivo nao e um PDF valido")
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = [page.extract_text() or "" for page in reader.pages]
            text = "\n".join(pages).strip()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="PDF invalido") from exc
        if not text:
            raise HTTPException(status_code=400, detail="PDF sem texto extraivel")
        return text
