from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    building_id: Optional[str] = None
    programme: Optional[str] = None
    laptop_model: Optional[str] = None
    laptop_asset_number: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[str] = None


class UserProfile(UserBase):
    id: str  # changed from int to str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # for Pydantic v2

class UserResponse(UserProfile):
    pass  # removed role, as it's not present in User model

class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None