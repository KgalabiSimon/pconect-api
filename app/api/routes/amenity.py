from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List

from app.db.models import Amenity, Space
from app.db.database import get_db
from app.schemas.amenity import AmenityCreate, AmenityUpdate, AmenityOut
from app.api.routes.auth import get_current_admin

router = APIRouter(prefix="/amenities", tags=["amenities"])

@router.post("/", response_model=AmenityOut, status_code=status.HTTP_201_CREATED)
def create_amenity(data: AmenityCreate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    amenity = Amenity(**data.dict())
    db.add(amenity)
    db.commit()
    db.refresh(amenity)
    return amenity

@router.get("/", response_model=List[AmenityOut])
def list_amenities(db: Session = Depends(get_db)):
    return db.query(Amenity).all()

@router.get("/{id}", response_model=AmenityOut)
def get_amenity(id: UUID, db: Session = Depends(get_db)):
    return db.query(Amenity).filter(Amenity.id == id).first()

@router.put("/{id}", response_model=AmenityOut)
def update_amenity(id: UUID, data: AmenityUpdate, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    amenity = db.query(Amenity).filter(Amenity.id == id).first()
    if not amenity:
        return None
    for key, value in data.dict(exclude_unset=True).items():
        setattr(amenity, key, value)
    db.commit()
    db.refresh(amenity)
    return amenity

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_amenity(id: UUID, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    amenity = db.query(Amenity).filter(Amenity.id == id).first()
    if amenity:
        db.delete(amenity)
        db.commit()
    return None

@router.post("/{amenity_id}/spaces/{space_id}", status_code=status.HTTP_200_OK)
def add_amenity_to_space(amenity_id: UUID, space_id: UUID, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
    space = db.query(Space).filter(Space.id == space_id).first()
    if not amenity or not space:
        return None
    space.amenities.append(amenity)
    db.commit()
    return {"message": "Amenity added to space."}

@router.delete("/{amenity_id}/spaces/{space_id}", status_code=status.HTTP_200_OK)
def remove_amenity_from_space(amenity_id: UUID, space_id: UUID, db: Session = Depends(get_db), current_admin=Depends(get_current_admin)):
    amenity = db.query(Amenity).filter(Amenity.id == amenity_id).first()
    space = db.query(Space).filter(Space.id == space_id).first()
    if not amenity or not space:
        return None
    if amenity in space.amenities:
        space.amenities.remove(amenity)
        db.commit()
    return {"message": "Amenity removed from space."}
