from pydantic import BaseModel
from uuid import UUID
from typing import Optional

class AmenityCreate(BaseModel):
    name: str
    description: Optional[str] = None

class AmenityUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class AmenityOut(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True
