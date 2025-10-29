from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None
    
    building_id: Optional[UUID] = None
    laptop_model: Optional[str] = None
    laptop_asset_number: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool = True
    programme_id: Optional[UUID] = None

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
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # for Pydantic v2

class UserResponse(UserProfile):
    pass

class UserProfileUpdate(BaseModel):
    id: UUID
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None