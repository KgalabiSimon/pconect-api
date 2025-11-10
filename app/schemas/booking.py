from pydantic import BaseModel
from uuid import UUID
from typing import Optional
from datetime import datetime, time
from app.db.models import SpaceType, CheckInStatus

class BookingCreate(BaseModel):
    user_id: UUID
    building_id: UUID
    floor: int
    space_type: SpaceType
    booking_date: datetime
    start_time: time
    end_time: time

class BookingOut(BaseModel):
    id: UUID
    user_id: UUID
    space_id: UUID
    booking_date: datetime
    start_time: time
    end_time: time
    status: CheckInStatus
    qr_code_url: Optional[str] = None

    class Config:
        orm_mode = True
