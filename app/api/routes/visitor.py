from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.models import Visitor, User, Building, CheckIn, UserType, CheckInStatus
from app.db.database import get_db
from app.schemas.visitor import VisitorCreate, VisitorResponse, VisitorCheckIn, VisitorLogResponse
from app.api.routes.auth import get_current_admin, get_current_officer, get_token_payload

router = APIRouter(prefix="/api/v1/visitors", tags=["Visitors"])

@router.post("/register", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def register_visitor(visitor_data: VisitorCreate, db: Session = Depends(get_db)):
    """Register a new visitor"""
    new_visitor = Visitor(
        first_name=visitor_data.first_name,
        last_name=visitor_data.last_name,
        company=visitor_data.company,
        mobile=visitor_data.mobile,
        email=visitor_data.email,
        photo_url=visitor_data.photo_url,
        purpose=visitor_data.purpose,
        host_employee_id=visitor_data.host_employee_id,
        host_employee_name=visitor_data.host_employee_name,
        other_reason=visitor_data.other_reason,
        building_id=visitor_data.building_id,
        floor=visitor_data.floor,
        block=visitor_data.block,
        has_weapons=visitor_data.has_weapons,
        weapon_details=visitor_data.weapon_details,
        device_id=visitor_data.device_id
    )
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)

    return VisitorResponse(
        id=str(new_visitor.id),
        first_name=new_visitor.first_name,
        last_name=new_visitor.last_name,
        company=new_visitor.company,
        mobile=new_visitor.mobile,
        email=new_visitor.email,
        photo_url=new_visitor.photo_url,
        purpose=new_visitor.purpose,
        host_employee_id=str(new_visitor.host_employee_id) if new_visitor.host_employee_id else None,
        host_employee_name=new_visitor.host_employee_name,
        other_reason=new_visitor.other_reason,
        building_id=str(new_visitor.building_id) if new_visitor.building_id else None,
        floor=new_visitor.floor,
        block=new_visitor.block,
        registered_at=str(new_visitor.registered_at) if new_visitor.registered_at else None
    )

@router.post("/checkin", response_model=VisitorLogResponse)
async def check_in_visitor(checkin_data: VisitorCheckIn, db: Session = Depends(get_db)):
    """Visitor check-in (manual or QR)"""
    # TODO: Implement visitor check-in logic
    pass

@router.post("/checkout/{visitor_id}", response_model=VisitorLogResponse)
async def check_out_visitor(visitor_id: str, db: Session = Depends(get_db)):
    """Visitor check-out"""
    # TODO: Implement visitor check-out logic
    pass

@router.get("/logs", response_model=List[VisitorLogResponse])
async def get_visitor_logs(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    """Admin/Security: Get all visitor logs"""
    # TODO: Implement visitor log retrieval
    pass

@router.get("/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(visitor_id: str, db: Session = Depends(get_db)):
    """Get visitor details"""
    # TODO: Implement visitor detail retrieval
    pass
