"""
Phishing Guard V2 — Dependency Injection

Provides database sessions and service instances via FastAPI's Depends().
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import get_settings

settings = get_settings()

engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Yield a database session, auto-close on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
