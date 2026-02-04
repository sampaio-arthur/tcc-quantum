from fastapi import HTTPException, UploadFile
from pypdf import PdfReader


def _read_txt(file: UploadFile) -> str:
    content = file.file.read()
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("latin-1")


def _read_pdf(file: UploadFile) -> str:
    reader = PdfReader(file.file)
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages).strip()


def parse_upload(file: UploadFile) -> str:
    filename = (file.filename or "").lower()
    if filename.endswith(".txt"):
        return _read_txt(file)
    if filename.endswith(".pdf"):
        return _read_pdf(file)
    raise HTTPException(status_code=400, detail="Unsupported file type. Use .txt or .pdf")
