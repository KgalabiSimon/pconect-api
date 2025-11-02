from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional
from app.db.models import CheckInStatus, UserType

class CheckInOut(BaseModel):
    id: UUID
    user_id: Optional[UUID] = None
    visitor_id: Optional[UUID] = None
    building_id: Optional[UUID] = None
    floor: Optional[str] = None
    block: Optional[str] = None
    programme_id: Optional[UUID] = None
    status: CheckInStatus
    user_type: Optional[UserType] = None
    check_in_time: datetime
    check_out_time: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    qr_code_data: Optional[str] = None
    expires_at: Optional[datetime] = None

    class Config:
        orm_mode = True
