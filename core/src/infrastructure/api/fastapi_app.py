import os
import threading
import time

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from infrastructure.api.auth import router as auth_router
from infrastructure.api.search.search_controller import router as search_router
from infrastructure.api.chat import router as chat_router
from infrastructure.api.datasets import router as datasets_router
from infrastructure.persistence.database import init_db

app = FastAPI(title="Quantum Search TCC")

RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "120"))
RATE_LIMIT_WINDOW_SECONDS = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI, max_requests: int, window_seconds: int) -> None:
        super().__init__(app)
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._lock = threading.Lock()
        self._buckets: dict[str, tuple[float, int]] = {}

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client = request.client.host if request.client else "unknown"
        now = time.time()
        with self._lock:
            window_start, count = self._buckets.get(client, (now, 0))
            if now - window_start >= self._window_seconds:
                window_start = now
                count = 0
            count += 1
            self._buckets[client] = (window_start, count)
            allowed = count <= self._max_requests
            retry_after = max(1, int(self._window_seconds - (now - window_start)))

        if not allowed:
            return JSONResponse(
                {"detail": "Too many requests"},
                status_code=429,
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)

# CORS for frontend integration (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RateLimitMiddleware,
    max_requests=RATE_LIMIT_REQUESTS,
    window_seconds=RATE_LIMIT_WINDOW_SECONDS,
)

app.include_router(auth_router)
app.include_router(search_router)
app.include_router(chat_router)
app.include_router(datasets_router)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
