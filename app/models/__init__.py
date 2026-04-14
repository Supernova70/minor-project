"""
Phishing Guard V2 — Database Models

Uses SQLAlchemy 2.0 declarative style with mapped_column.

All models are imported here so that:
  - Alembic can discover them via target_metadata = Base.metadata
  - SQLAlchemy resolves relationship() forward references correctly
  - app/main.py only needs to import this package
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


# Import all models — ORDER MATTERS for FK resolution
from app.models.email import Email, Attachment  # noqa: F401, E402
from app.models.scan import Scan, Verdict  # noqa: F401, E402
from app.models.fetch_state import FetchState  # noqa: F401, E402
from app.models.url_result import UrlResult  # noqa: F401, E402
