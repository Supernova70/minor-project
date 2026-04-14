"""FetchState ORM model — tracks last-fetched IMAP UID per mailbox."""

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base


class FetchState(Base):
    """
    Tracks the highest UID successfully fetched and stored for each mailbox.

    On each fetch call the email service reads last_uid, searches for
    UIDs > last_uid (incremental), then updates last_uid after storing.
    This eliminates full-inbox scans and the deduplication thrash caused
    by IMAP sequence number drift.
    """

    __tablename__ = "fetch_state"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    mailbox: Mapped[str] = mapped_column(String(256), default="INBOX", unique=True)
    last_uid: Mapped[int] = mapped_column(Integer, default=0)
    last_fetched_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime, nullable=True
    )
