from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.search.search_controller import router as search_router

app = FastAPI(title="Quantum Search TCC")

# CORS for frontend integration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
