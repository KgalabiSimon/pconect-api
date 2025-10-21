from pydantic import BaseModel, EmailStr
from typing import Optional

class AdminCreate(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    role: Optional[str] = "admin"
    is_active: bool = True
