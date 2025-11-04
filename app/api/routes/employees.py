from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.models import User
from app.db.database import get_db
from app.schemas.users import UserResponse

router = APIRouter(prefix="/employees", tags=["Employees"])

@router.get("/", response_model=List[UserResponse])
async def list_employees(db: Session = Depends(get_db)):
    """Get all employees (users)"""
    employees = db.query(User).all()
    return [UserResponse(
        id=str(emp.id),
        email=emp.email,
        first_name=emp.first_name,
        last_name=emp.last_name,
        phone=emp.phone,
        building_id=str(emp.building_id) if emp.building_id else None,
        programme_id=str(emp.programme_id) if hasattr(emp, 'programme_id') and emp.programme_id else None,
        laptop_model=emp.laptop_model,
        laptop_asset_number=emp.laptop_asset_number,
        photo_url=emp.photo_url,
        is_active=emp.is_active
    ) for emp in employees]
