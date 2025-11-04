from pydantic import BaseModel, EmailStr
from typing import Optional

class VisitorCreate(BaseModel):
    first_name: str
    last_name: str
    company: Optional[str] = None
    mobile: str
    email: Optional[EmailStr] = None
    photo_url: Optional[str] = None
    purpose: str
    host_employee_id: Optional[str] = None
    host_employee_name: Optional[str] = None
    other_reason: Optional[str] = None
    building_id: Optional[str] = None
    floor: Optional[str] = None
    block: Optional[str] = None
    has_weapons: Optional[bool] = False
    weapon_details: Optional[str] = None
    device_id: Optional[str] = None

class VisitorResponse(BaseModel):
    id: str
    first_name: str
    last_name: str
    company: Optional[str]
    mobile: str
    email: Optional[EmailStr]
    photo_url: Optional[str]
    purpose: str
    host_employee_id: Optional[str]
    host_employee_name: Optional[str]
    other_reason: Optional[str]
    building_id: Optional[str]
    floor: Optional[str]
    block: Optional[str]
    registered_at: Optional[str]

class VisitorCheckIn(BaseModel):
    visitor_id: str
    building_id: Optional[str] = None
    floor: Optional[str] = None
    block: Optional[str] = None
    device_id: Optional[str] = None
    qr_code_data: Optional[str] = None

class VisitorLogResponse(BaseModel):
    visitor_id: str
    check_in_time: Optional[str]
    check_out_time: Optional[str]
    status: str
    building_id: Optional[str]
    floor: Optional[str]
    block: Optional[str]
    host_employee_id: Optional[str]
    host_employee_name: Optional[str]
