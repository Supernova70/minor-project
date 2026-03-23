"""
Phishing Guard V2 — Application Factory

Creates and configures the FastAPI application.
"""

import logging

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.config import get_settings
from app.api.router import api_router
from app.models import Base
from app.dependencies import engine

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    settings = get_settings()
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Create tables if they don't exist (Alembic handles migrations in prod)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified")

    yield

    logger.info("Shutting down")


def create_app() -> FastAPI:
    """Build and return the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Email phishing detection system with ML-based analysis",
        lifespan=lifespan,
    )

    # Mount API routes
    app.include_router(api_router)

    return app


# Create the app instance (used by uvicorn)
app = create_app()
