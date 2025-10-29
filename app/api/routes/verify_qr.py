from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime
from app.db.database import get_db
from app.db.models import CheckIn

router = APIRouter(prefix="/api/v1/verify-qr")

@router.post("/")
async def verify_qr_code(checkin_id: UUID, db: Session = Depends(get_db)):
    """
    Verify a QR code by check-in ID. Fails if expired or not found.
    """
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in record not found")
    if checkin.expires_at and datetime.utcnow() > checkin.expires_at:
        raise HTTPException(status_code=400, detail="QR code has expired")
    if checkin.status != "checked_in":
        raise HTTPException(status_code=400, detail="User is not currently checked in")
    return {"message": "QR code is valid", "user_id": str(checkin.user_id), "checkin_id": str(checkin.id)}
