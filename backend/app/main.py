from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.repositories.assessment_repository import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialise local persistence when the API starts."""
    init_db()
    yield


app = FastAPI(
    title="VendorGuard AI API",
    description="Human-governed vendor assessment API.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "name": "VendorGuard AI",
        "status": "running",
        "documentation": "/docs",
    }