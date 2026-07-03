"""
VendorGuard AI FastAPI application entry point.

Initialises the database, configures CORS, and exposes health/readiness
endpoints for local testing and Cloud Run deployment.
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api.routes import router
from app.config import settings
from app.repositories.assessment_repository import engine, init_db


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
    logger.info(
        "Database type: %s",
        "postgresql" if settings.using_postgres else "sqlite",
    )

    init_db()

    logger.info("VendorGuard database initialised.")

    yield

    logger.info("VendorGuard AI API shutting down.")


app = FastAPI(
    title="VendorGuard AI API",
    description=(
        "Evidence-backed vendor risk assessment with governed policy "
        "checks, Gemini-assisted reasoning, deterministic fallback, "
        "and mandatory human review."
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


@app.get("/health")
def health() -> dict[str, str]:
    """
    Lightweight health endpoint.

    Use this to confirm that the API process is running.
    """

    return {
        "status": "healthy",
        "service": "vendorguard-api",
    }


@app.get("/readiness")
def readiness() -> dict[str, object]:
    """
    Readiness endpoint.

    Use this before deployment to confirm that the app can reach the
    configured database and that key runtime settings are loaded.
    """

    with engine.connect() as connection:
        database_check = connection.execute(
            text("select 1"),
        ).scalar_one()

    return {
        "status": "ready",
        "service": "vendorguard-api",
        "database": "postgresql" if settings.using_postgres else "sqlite",
        "database_check": database_check,
        "gemini_key_configured": bool(settings.gemini_api_key.strip()),
        "gemini_model": settings.gemini_model,
        "sample_data_exists": settings.resolved_sample_data_path.exists(),
        "cors_origins": settings.cors_origin_list,
    }