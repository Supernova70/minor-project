"""API router aggregator — mounts all route modules."""

from fastapi import APIRouter

from app.api.health import router as health_router
from app.api.email import router as email_router
from app.api.scan import router as scan_router

api_router = APIRouter()

api_router.include_router(health_router)
api_router.include_router(email_router)
api_router.include_router(scan_router)
