from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, timezone
from app.db.database import get_db
from app.db.models import CheckIn, User, SecurityOfficer, CheckInStatus
from pydantic import BaseModel
from app.api.routes.auth import get_current_user, get_current_officer

router = APIRouter(prefix="/api/v1/verify-qr")

class VerifyQRRequest(BaseModel):
    checkin_id: UUID
    officer_id: UUID

@router.post("/")
async def verify_qr_code(request: VerifyQRRequest, db: Session = Depends(get_db), current_officer: SecurityOfficer = Depends(get_current_officer)):
    """
    Verify a QR code by check-in ID. Fails if expired or not found. Tracks officer who scanned.
    """
    checkin_id = request.checkin_id
    officer_id = request.officer_id
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in record not found")
    if checkin.expires_at:
        now = datetime.now(timezone.utc)
        expires_at = checkin.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        if now > expires_at:
            raise HTTPException(status_code=400, detail="QR code has expired")
    if checkin.status not in [CheckInStatus.PENDING, CheckInStatus.CHECKED_OUT]:
        raise HTTPException(status_code=400, detail="Check-in is not pending or already processed")
    # Mark as checked in and track officer
    checkin.status = CheckInStatus.CHECKED_IN
    checkin.checked_out_by_officer = str(officer_id)
    db.commit()
    db.refresh(checkin)
    return {"message": "QR code is valid and user is now checked in", "user_id": str(checkin.user_id), "checkin_id": str(checkin.id), "verified_by": str(officer_id)}
