from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Optional[dict] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None


class AdminLogin(BaseModel):
    email: str
    password: str


class SecurityLogin(BaseModel):
    badge_number: str
    pin: str
