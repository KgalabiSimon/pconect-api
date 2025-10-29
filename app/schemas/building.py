from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum

class SpaceType(str, Enum):
    DESK = "DESK"
    OFFICE = "OFFICE"
    ROOM = "ROOM"

# --- Space Schemas ---
class SpaceBase(BaseModel):
    type: SpaceType
    quantity: int = Field(..., ge=0)

class SpaceCreate(SpaceBase):
    pass

class SpaceUpdate(BaseModel):
    quantity: Optional[int] = Field(None, ge=0)

class SpaceResponse(SpaceBase):
    id: UUID
    building_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Floor Schemas ---
class FloorBase(BaseModel):
    floor_index: int = Field(..., ge=1)

class FloorCreate(FloorBase):
    pass

class FloorUpdate(BaseModel):
    floor_index: Optional[int] = Field(None, ge=1)

class FloorResponse(FloorBase):
    id: UUID
    building_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Block Schemas ---
class BlockBase(BaseModel):
    block_label: str

class BlockCreate(BlockBase):
    pass

class BlockUpdate(BaseModel):
    block_label: Optional[str]

class BlockResponse(BlockBase):
    id: UUID
    building_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Building Schemas ---
class BuildingBase(BaseModel):
    building_code: str
    name: str
    address: str
    floors_count: int = Field(..., ge=0)
    blocks_count: int = Field(..., ge=0)

class BuildingCreate(BuildingBase):
    pass

class BuildingUpdate(BaseModel):
    name: Optional[str]
    address: Optional[str]
    floors_count: Optional[int] = Field(None, ge=0)
    blocks_count: Optional[int] = Field(None, ge=0)

class BuildingResponse(BuildingBase):
    id: UUID
    total_spaces: int
    created_at: datetime
    updated_at: datetime
    spaces: List[SpaceResponse] = []
    floors: List[FloorResponse] = []
    blocks: List[BlockResponse] = []

    class Config:
        orm_mode = True
