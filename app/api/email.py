"""Email API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.email import Email
from app.schemas.email import (
    EmailOut,
    EmailDetailOut,
    FetchEmailsResponse,
    EmailListResponse,
)
from app.services.email_service import EmailService

router = APIRouter(prefix="/emails", tags=["Emails"])


@router.post("/fetch", response_model=FetchEmailsResponse)
async def fetch_emails(
    limit: int = Query(20, ge=1, le=100, description="Max emails to fetch"),
    db: Session = Depends(get_db),
):
    """
    Fetch recent emails from the configured IMAP inbox.

    Connects to the email server, downloads recent messages,
    parses them, and stores them in the database.
    """
    try:
        service = EmailService(db)
        new_count, total_fetched = service.fetch_and_store(limit=limit)
        return FetchEmailsResponse(
            status="success",
            new_emails=new_count,
            total_fetched=total_fetched,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Email fetch failed: {str(e)}")


@router.get("", response_model=EmailListResponse)
async def list_emails(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List all fetched emails with pagination."""
    total = db.query(Email).count()
    emails = (
        db.query(Email)
        .order_by(Email.fetched_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return EmailListResponse(
        total=total,
        emails=[EmailOut(**e.to_dict()) for e in emails],
    )


@router.get("/{email_id}", response_model=EmailDetailOut)
async def get_email(email_id: int, db: Session = Depends(get_db)):
    """Get full email details by ID."""
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    data = email.to_dict()
    data["body_text"] = email.body_text
    data["body_html"] = email.body_html
    data["attachments"] = [att.to_dict() for att in email.attachments]
    return EmailDetailOut(**data)
