from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.db.database import get_db
from app.db.models import CheckIn

router = APIRouter(prefix="/api/v1/verify-qr")

@router.post("/")
async def verify_qr_code(checkin_id: UUID, officer_id: UUID, db: Session = Depends(get_db)):
    """
    Verify a QR code by check-in ID. Fails if expired or not found. Tracks officer who scanned.
    """
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in record not found")
    if checkin.expires_at and datetime.utcnow() > checkin.expires_at:
        raise HTTPException(status_code=400, detail="QR code has expired")
    if checkin.status != "pending":
        raise HTTPException(status_code=400, detail="Check-in is not pending or already processed")
    # Mark as checked in and track officer
    checkin.status = "checked_in"
    checkin.checked_out_by_officer = str(officer_id)
    db.commit()
    db.refresh(checkin)
    return {"message": "QR code is valid and user is now checked in", "user_id": str(checkin.user_id), "checkin_id": str(checkin.id), "verified_by": str(officer_id)}
