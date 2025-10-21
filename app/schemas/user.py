from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    phone: Optional[str] = None
    building_id: Optional[str] = None
    programme: Optional[str] = None
    laptop_model: Optional[str] = None
    laptop_asset_number: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)
    photo_url: Optional[str] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    building_id: Optional[str] = None
    programme: Optional[str] = None
    laptop_model: Optional[str] = None
    laptop_asset_number: Optional[str] = None
    photo_url: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    photo_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode for Pydantic V2


class UserProfileUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    laptop_model: Optional[str] = None
    laptop_asset_number: Optional[str] = None
    photo_url: Optional[str] = None


# Password Reset
class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)
