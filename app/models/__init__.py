"""
Phishing Guard V2 — Database Models

Uses SQLAlchemy 2.0 declarative style with mapped_column.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass
