from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from infrastructure.api.auth import router as auth_router
from infrastructure.api.search.search_controller_pg import router as search_router
from infrastructure.api.chat import router as chat_router
from infrastructure.api.datasets import router as datasets_router
from infrastructure.api.benchmarks import router as benchmarks_router
from infrastructure.persistence.database import init_db

@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Quantum Search TCC", lifespan=lifespan)

# CORS for frontend integration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(datasets_router)
app.include_router(benchmarks_router)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


