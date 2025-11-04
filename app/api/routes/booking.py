
from app.api.routes.auth import get_current_admin
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, time
from app.db.database import get_db
from app.db.models import Booking, Space, Building, CheckInStatus, User, SpaceType, BookingStatus
from app.utils.qr import generate_qr_base64
from app.api.routes.auth import get_current_user
from pydantic import BaseModel
from app.schemas.booking import BookingCreate, BookingOut

router = APIRouter(prefix="/api/v1/booking", tags=["Booking"])

@router.get("/", response_model=list[BookingOut])

async def list_bookings(
    user_id: UUID = None,
    building_id: UUID = None,
    space_type: SpaceType = None,
    booking_date: datetime = None,
    status: CheckInStatus = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Booking)
    if user_id:
        query = query.filter(Booking.user_id == user_id)
    if building_id:
        query = query.join(Space).filter(Space.building_id == building_id)
    if space_type:
        query = query.join(Space).filter(Space.type == space_type)
    if booking_date:
        query = query.filter(Booking.booking_date == booking_date)
    if status:
        query = query.filter(Booking.status == status)
    return query.all()

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_booking(
    booking_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(booking)
    db.commit()
    return None

@router.put("/{booking_id}", response_model=BookingOut)

async def update_booking(
    booking_id: UUID,
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    # Update fields
    booking.user_id = data.user_id
    booking.booking_date = data.booking_date
    booking.start_time = data.start_time
    booking.end_time = data.end_time
    # Update space if building/floor/type changed
    space = db.query(Space).filter(
        Space.building_id == data.building_id,
        Space.type == data.space_type
    ).first()
    if not space:
        raise HTTPException(status_code=404, detail=f"No {data.space_type.value} available in building/floor")
    booking.space_id = space.id
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/admin", response_model=list[BookingOut])
async def admin_list_bookings(
    user_id: UUID = None,
    building_id: UUID = None,
    space_type: SpaceType = None,
    booking_date: datetime = None,
    status: CheckInStatus = None,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Admin-only endpoint to view and filter bookings.
    """
    query = db.query(Booking)
    if user_id:
        query = query.filter(Booking.user_id == user_id)
    if building_id:
        query = query.join(Space).filter(Space.building_id == building_id)
    if space_type:
        query = query.join(Space).filter(Space.type == space_type)
    if booking_date:
        query = query.filter(Booking.booking_date == booking_date)
    if status:
        query = query.filter(Booking.status == status)
    return query.all()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check building exists
    building = db.query(Building).filter(Building.id == data.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail="Building not found")
    # Find available space of requested type and floor
    space = db.query(Space).filter(
        Space.building_id == data.building_id,
        Space.type == data.space_type
    ).first()
    if not space:
        raise HTTPException(status_code=404, detail=f"No {data.space_type.value} available in building/floor")
    # Check for overlapping bookings
    overlapping = db.query(Booking).filter(
        Booking.space_id == space.id,
        Booking.booking_date == data.booking_date,
        Booking.start_time < data.end_time,
        Booking.end_time > data.start_time,
        Booking.status == CheckInStatus.PENDING
    ).first()
    if overlapping:
        raise HTTPException(status_code=400, detail="Space is already booked for the selected time")
    # Create booking
    booking = Booking(
        user_id=data.user_id,
        space_id=space.id,
        booking_date=data.booking_date,
        start_time=data.start_time,
        end_time=data.end_time,
        status=CheckInStatus.PENDING
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return {
        "message": "Booking successful.",
        "booking_id": str(booking.id)
    }


@router.get("/availability", status_code=200)
async def check_space_availability(
    building_id: UUID,
    space_type: SpaceType,
    booking_date: datetime,
    start_time: time,
    end_time: time,
    db: Session = Depends(get_db)
):
    """
    Check if a space of the given type is available in the building for the specified date and time range.
    """
    # Find the space
    space = db.query(Space).filter(
        Space.building_id == building_id,
        Space.type == space_type
    ).first()
    if not space:
        return {"available": False, "reason": f"No {space_type.value} found in building."}

    # Check for overlapping bookings
    overlapping = db.query(Booking).filter(
        Booking.space_id == space.id,
        Booking.booking_date == booking_date,
        Booking.start_time < end_time,
        Booking.end_time > start_time,
        Booking.status.in_([BookingStatus.CONFIRMED, BookingStatus.PENDING])
    ).first()
    if overlapping:
        return {"available": False, "reason": "Space is already booked for the selected time."}

    return {"available": True, "space_id": str(space.id)}