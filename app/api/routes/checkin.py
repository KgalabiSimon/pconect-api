from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.db.models import User, CheckIn, CheckInStatus
from app.utils.qr import generate_qr_base64
from datetime import datetime, timedelta
from app.api.routes.auth import get_current_user, get_current_officer
from app.db.models import SecurityOfficer
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/checkin")

class CheckoutRequest(BaseModel):
    checkin_id: UUID

@router.post("/", status_code=status.HTTP_201_CREATED)
async def check_in_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Check in a user and return a QR code for security verification.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Create a check-in record (assumes CheckIn model exists)
    checkin = CheckIn(
        user_id=user.id,
        check_in_time=datetime.utcnow(),
        status=CheckInStatus.PENDING,
        expires_at=datetime.utcnow() + timedelta(days=1)
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)

    # Generate QR code with check-in ID (or token)
    qr_data = str(checkin.id)
    qr_code_base64 = generate_qr_base64(qr_data)

    return {
        "message": "Check-in successful. Present this QR code to security.",
        "qr_code_base64": qr_code_base64,
        "checkin_id": str(checkin.id)
    }

@router.post("/checkout", status_code=status.HTTP_200_OK)
async def check_out_user(
    request: CheckoutRequest,
    db: Session = Depends(get_db),
    current_officer: SecurityOfficer = Depends(get_current_officer)
):
    """
    Officer checks out a user by check-in ID.
    """
    checkin_id = request.checkin_id
    checkin = db.query(CheckIn).filter(CheckIn.id == checkin_id).first()
    if not checkin:
        raise HTTPException(status_code=404, detail="Check-in record not found")
    if checkin.status != CheckInStatus.CHECKED_IN:
        raise HTTPException(status_code=400, detail="User is not currently checked in")
    checkin.status = CheckInStatus.CHECKED_OUT
    checkin.check_out_time = datetime.utcnow()
    checkin.checked_out_by_officer = str(current_officer.id)
    db.commit()
    db.refresh(checkin)
    return {"message": "User checked out successfully", "checkin_id": str(checkin.id), "checked_out_by": str(current_officer.id)}
