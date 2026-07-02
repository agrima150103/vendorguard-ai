"""
VendorGuard AI FastAPI application entry point.

Initialises the database, configures CORS, and registers all API routes.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.config import settings
from app.repositories.assessment_repository import init_db


logging.basicConfig(
    level=getattr(
        logging,
        settings.log_level.upper(),
        logging.INFO,
    ),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialise application resources."""

    logger.info("Starting VendorGuard AI API.")
    logger.info("Allowed CORS origins: %s", settings.cors_origin_list)

    init_db()

    logger.info("VendorGuard database initialised.")

    yield

    logger.info("VendorGuard AI API shutting down.")


app = FastAPI(
    title="VendorGuard AI API",
    description=(
        "Evidence-backed vendor risk assessment with governed policy "
        "checks and mandatory human review."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root() -> dict[str, str]:
    """API root endpoint."""

    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
    }