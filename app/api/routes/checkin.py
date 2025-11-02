from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.db.models import User, CheckIn, CheckInStatus, UserType
from app.utils.qr import generate_qr_base64
from datetime import datetime, timedelta
from app.api.routes.auth import get_current_user, get_current_officer, get_current_admin
from app.db.models import SecurityOfficer
from pydantic import BaseModel
from app.schemas.checkin import CheckInOut

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

    # Check for existing active check-in (not checked out)
    active_checkin = db.query(CheckIn).filter(CheckIn.user_id == user.id, CheckIn.status != CheckInStatus.CHECKED_OUT).first()
    if active_checkin:
        raise HTTPException(status_code=400, detail="User already has an active check-in")

    # Allow check-in if last status is CHECKED_OUT or PENDING
    last_checkin = db.query(CheckIn).filter(CheckIn.user_id == user.id).order_by(CheckIn.check_in_time.desc()).first()
    if last_checkin and last_checkin.status == CheckInStatus.CHECKED_IN:
        raise HTTPException(status_code=400, detail="User is currently checked in and cannot check in again")
    if last_checkin and last_checkin.status not in [CheckInStatus.PENDING, CheckInStatus.CHECKED_OUT]:
        raise HTTPException(status_code=400, detail="Check-in is not pending or already processed")

    # Create a check-in record (assum, es CheckIn model exists)
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

@router.get("/", response_model=list[CheckInOut])
async def filter_checkins(
    user_id: UUID = None,
    visitor_id: UUID = None,
    building_id: UUID = None,
    floor: str = None,
    block: str = None,
    programme_id: UUID = None,
    status: CheckInStatus = None,
    user_type: UserType = None,
    start_date: datetime = None,
    end_date: datetime = None,
    db: Session = Depends(get_db),
    current_admin=Depends(get_current_admin)
):
    query = db.query(CheckIn)
    if user_id:
        query = query.filter(CheckIn.user_id == user_id)
    if visitor_id:
        query = query.filter(CheckIn.visitor_id == visitor_id)
    if building_id:
        query = query.filter(CheckIn.building_id == building_id)
    if floor:
        query = query.filter(CheckIn.floor == floor)
    if block:
        query = query.filter(CheckIn.block == block)
    if programme_id:
        query = query.join(User).filter(User.programme_id == programme_id)
    if status:
        query = query.filter(CheckIn.status == status)
    if user_type:
        query = query.filter(CheckIn.user_type == user_type)
    if start_date:
        query = query.filter(CheckIn.check_in_time >= start_date)
    if end_date:
        query = query.filter(CheckIn.check_in_time <= end_date)
    return query.all()
