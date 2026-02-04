from fastapi import FastAPI

from infrastructure.api.search.search_controller import router as search_router

app = FastAPI(title="Quantum Search TCC")

app.include_router(search_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
