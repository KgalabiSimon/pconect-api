from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.database import get_db
from app.db.models import Programme
from pydantic import BaseModel

class ProgrammeCreate(BaseModel):
    name: str

class ProgrammeUpdate(BaseModel):
    name: str

class ProgrammeOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True

router = APIRouter(prefix="/api/v1/programmes")

@router.get("/", response_model=list[ProgrammeOut])
def list_programmes(db: Session = Depends(get_db)):
    return db.query(Programme).all()

@router.post("/", response_model=ProgrammeOut, status_code=status.HTTP_201_CREATED)
def create_programme(data: ProgrammeCreate, db: Session = Depends(get_db)):
    if db.query(Programme).filter(Programme.name == data.name).first():
        raise HTTPException(status_code=400, detail="Programme already exists")
    programme = Programme(name=data.name)
    db.add(programme)
    db.commit()
    db.refresh(programme)
    return programme

@router.get("/{id}", response_model=ProgrammeOut)
def get_programme(id: UUID, db: Session = Depends(get_db)):
    programme = db.query(Programme).filter(Programme.id == id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    return programme

@router.put("/{id}", response_model=ProgrammeOut)
def update_programme(id: UUID, data: ProgrammeUpdate, db: Session = Depends(get_db)):
    programme = db.query(Programme).filter(Programme.id == id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    programme.name = data.name
    db.commit()
    db.refresh(programme)
    return programme

@router.delete("/{id}", response_model=dict)
def delete_programme(id: UUID, db: Session = Depends(get_db)):
    programme = db.query(Programme).filter(Programme.id == id).first()
    if not programme:
        raise HTTPException(status_code=404, detail="Programme not found")
    db.delete(programme)
    db.commit()
    return {"message": "Programme deleted", "id": str(id)}
