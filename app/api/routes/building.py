from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db import models
from app.schemas.building import (
    BuildingCreate, BuildingUpdate, BuildingResponse,
    SpaceCreate, SpaceUpdate, SpaceResponse,
    FloorCreate, FloorUpdate, FloorResponse,
    BlockCreate, BlockUpdate, BlockResponse
)
from app.db.database import get_db

router = APIRouter(prefix="/api/v1/buildings", tags=["Buildings"])

# --- Building Endpoints ---
@router.post("/", response_model=BuildingResponse, status_code=status.HTTP_201_CREATED)
def create_building(data: BuildingCreate, db: Session = Depends(get_db)):
    if db.query(models.Building).filter_by(building_code=data.building_code).first():
        raise HTTPException(status_code=400, detail="Building code already exists")
    building = models.Building(**data.dict())
    db.add(building)
    db.commit()
    db.refresh(building)
    return building

@router.get("/", response_model=List[BuildingResponse])
def list_buildings(db: Session = Depends(get_db)):
    return db.query(models.Building).all()

@router.get("/{building_id}", response_model=BuildingResponse)
def get_building(building_id: UUID, db: Session = Depends(get_db)):
    building = db.query(models.Building).filter_by(id=building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    return building

@router.put("/{building_id}", response_model=BuildingResponse)
def update_building(building_id: UUID, data: BuildingUpdate, db: Session = Depends(get_db)):
    building = db.query(models.Building).filter_by(id=building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(building, k, v)
    db.commit()
    db.refresh(building)
    return building

@router.delete("/{building_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_building(building_id: UUID, db: Session = Depends(get_db)):
    building = db.query(models.Building).filter_by(id=building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    db.delete(building)
    db.commit()
    return

# --- Space Endpoints ---
@router.post("/{building_id}/spaces", response_model=SpaceResponse, status_code=status.HTTP_201_CREATED)
def create_space(building_id: UUID, data: SpaceCreate, db: Session = Depends(get_db)):
    # Enforce unique (building_id, type)
    if db.query(models.Space).filter_by(building_id=building_id, type=data.type).first():
        raise HTTPException(status_code=400, detail="Space type already exists for this building")
    space = models.Space(building_id=building_id, **data.dict())
    db.add(space)
    db.commit()
    db.refresh(space)
    return space

@router.get("/{building_id}/spaces", response_model=List[SpaceResponse])
def list_spaces(building_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Space).filter_by(building_id=building_id).all()

@router.put("/spaces/{space_id}", response_model=SpaceResponse)
def update_space(space_id: UUID, data: SpaceUpdate, db: Session = Depends(get_db)):
    space = db.query(models.Space).filter_by(id=space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(space, k, v)
    db.commit()
    db.refresh(space)
    return space

@router.delete("/spaces/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(space_id: UUID, db: Session = Depends(get_db)):
    space = db.query(models.Space).filter_by(id=space_id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    db.delete(space)
    db.commit()
    return

# --- Floor Endpoints ---
@router.post("/{building_id}/floors", response_model=FloorResponse, status_code=status.HTTP_201_CREATED)
def create_floor(building_id: UUID, data: FloorCreate, db: Session = Depends(get_db)):
    # Enforce unique (building_id, floor_index)
    if db.query(models.Floor).filter_by(building_id=building_id, floor_index=data.floor_index).first():
        raise HTTPException(status_code=400, detail="Floor index already exists for this building")
    floor = models.Floor(building_id=building_id, **data.dict())
    db.add(floor)
    db.commit()
    db.refresh(floor)
    return floor

@router.get("/{building_id}/floors", response_model=List[FloorResponse])
def list_floors(building_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Floor).filter_by(building_id=building_id).all()

@router.put("/floors/{floor_id}", response_model=FloorResponse)
def update_floor(floor_id: UUID, data: FloorUpdate, db: Session = Depends(get_db)):
    floor = db.query(models.Floor).filter_by(id=floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(floor, k, v)
    db.commit()
    db.refresh(floor)
    return floor

@router.delete("/floors/{floor_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_floor(floor_id: UUID, db: Session = Depends(get_db)):
    floor = db.query(models.Floor).filter_by(id=floor_id).first()
    if not floor:
        raise HTTPException(status_code=404, detail="Floor not found")
    db.delete(floor)
    db.commit()
    return

# --- Block Endpoints ---
@router.post("/{building_id}/blocks", response_model=BlockResponse, status_code=status.HTTP_201_CREATED)
def create_block(building_id: UUID, data: BlockCreate, db: Session = Depends(get_db)):
    # Enforce unique (building_id, block_label)
    if db.query(models.Block).filter_by(building_id=building_id, block_label=data.block_label).first():
        raise HTTPException(status_code=400, detail="Block label already exists for this building")
    block = models.Block(building_id=building_id, **data.dict())
    db.add(block)
    db.commit()
    db.refresh(block)
    return block

@router.get("/{building_id}/blocks", response_model=List[BlockResponse])
def list_blocks(building_id: UUID, db: Session = Depends(get_db)):
    return db.query(models.Block).filter_by(building_id=building_id).all()

@router.put("/blocks/{block_id}", response_model=BlockResponse)
def update_block(block_id: UUID, data: BlockUpdate, db: Session = Depends(get_db)):
    block = db.query(models.Block).filter_by(id=block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(block, k, v)
    db.commit()
    db.refresh(block)
    return block

@router.delete("/blocks/{block_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(block_id: UUID, db: Session = Depends(get_db)):
    block = db.query(models.Block).filter_by(id=block_id).first()
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    db.delete(block)
    db.commit()
    return
