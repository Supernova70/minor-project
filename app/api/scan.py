"""Scan API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.models.email import Email
from app.models.scan import Scan
from app.schemas.scan import ScanOut, ScanTriggerResponse, ScanListResponse
from app.services.scan_service import ScanService

router = APIRouter(prefix="/scans", tags=["Scans"])


@router.post("/{email_id}", response_model=ScanTriggerResponse)
async def trigger_scan(email_id: int, db: Session = Depends(get_db)):
    """
    Trigger a full analysis scan on an email.

    Runs the ML text analyzer (and future engines) on the email body,
    then computes a verdict with risk classification.
    """
    # Verify email exists
    email = db.query(Email).filter(Email.id == email_id).first()
    if not email:
        raise HTTPException(status_code=404, detail="Email not found")

    try:
        service = ScanService(db)
        scan = service.run_scan(email)
        return ScanTriggerResponse(
            status="success",
            scan_id=scan.id,
            email_id=email.id,
            verdict=scan.verdict.to_dict() if scan.verdict else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@router.get("", response_model=ScanListResponse)
async def list_scans(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    """List all scans with pagination."""
    total = db.query(Scan).count()
    scans = (
        db.query(Scan)
        .order_by(Scan.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return ScanListResponse(
        total=total,
        scans=[ScanOut(**s.to_dict()) for s in scans],
    )


@router.get("/{scan_id}", response_model=ScanOut)
async def get_scan(scan_id: int, db: Session = Depends(get_db)):
    """Get scan details including verdict."""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    return ScanOut(**scan.to_dict())
