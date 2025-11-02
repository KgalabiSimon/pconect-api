from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.db.models import Space, Building, SpaceType
from pydantic import BaseModel
from app.api.routes.auth import get_current_admin

router = APIRouter(prefix="/api/v1/spaces")

class SpaceCreate(BaseModel):
    building_id: UUID
    type: SpaceType
    quantity: int

class SpaceUpdate(BaseModel):
    type: SpaceType
    quantity: int

class SpaceOut(BaseModel):
    id: UUID
    building_id: UUID
    type: str
    quantity: int
    class Config:
        orm_mode = True

@router.get("/", response_model=list[SpaceOut])
def list_spaces(db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    return db.query(Space).all()

@router.post("/", response_model=SpaceOut, status_code=status.HTTP_201_CREATED)
def create_space(data: SpaceCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    building = db.query(Building).filter(Building.id == data.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    space = Space(**data.dict())
    db.add(space)
    db.commit()
    db.refresh(space)
    return space

@router.get("/{id}", response_model=SpaceOut)
def get_space(id: UUID, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    space = db.query(Space).filter(Space.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    return space

@router.put("/{id}", response_model=SpaceOut)
def update_space(id: UUID, data: SpaceUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    space = db.query(Space).filter(Space.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    for key, value in data.dict().items():
        setattr(space, key, value)
    db.commit()
    db.refresh(space)
    return space

@router.delete("/{id}", response_model=dict)
def delete_space(id: UUID, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    space = db.query(Space).filter(Space.id == id).first()
    if not space:
        raise HTTPException(status_code=404, detail="Space not found")
    db.delete(space)
    db.commit()
    return {"message": "Space deleted", "id": str(id)}
