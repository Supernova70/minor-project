"""Health check endpoint."""

from fastapi import APIRouter
from app.config import get_settings

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check():
    """System health check."""
    settings = get_settings()
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }
