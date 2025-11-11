from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import uuid

from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserResponse, UserUpdate, UserProfileUpdate, UserCreate
from app.api.routes.auth import get_current_user, get_current_admin, get_token_payload
from app.core.security import get_password_hash, generate_id, can_access_user, can_modify_user

router = APIRouter(prefix="/api/v1/users")


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, le=1000),
    building_id: Optional[str] = None,
    programme_id: Optional[UUID] = Query(None),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """GET /api/v1/users - Get all users with optional filters (admin only)"""

    query = db.query(User).filter(User.is_active == True)

    if building_id:
        query = query.filter(User.building_id == building_id)

    if programme_id:
        query = query.filter(User.programme_id == programme_id)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (User.first_name.ilike(search_term)) |
            (User.last_name.ilike(search_term)) |
            (User.email.ilike(search_term)) |
            (User.phone.ilike(search_term))
        )

    users = query.offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """POST /api/v1/users - Create a new user (admin only)"""

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # # Generate user ID
    # last_user = db.query(User).order_by(User.id.desc()).first()
    # if last_user:
    #     last_num = int(last_user.id.split("-")[1])
    #     user_id = generate_id("USR", last_num + 1)
    # else:
    #     user_id = generate_id("USR", 1)

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        id=str(uuid.uuid4()),
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        phone=user_data.phone,
        building_id=user_data.building_id,
        programme_id=user_data.programme_id,
        laptop_model=user_data.laptop_model,
        laptop_asset_number=user_data.laptop_asset_number,
        photo_url=user_data.photo_url
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/search", response_model=List[UserResponse])
async def search_users(
    q: str = Query(..., min_length=2),
    limit: int = Query(10, le=50),
    db: Session = Depends(get_db)
):
    """Search users by name for autocomplete (used in visitor kiosk)"""

    search_term = f"%{q}%"
    users = db.query(User).filter(
        (User.first_name.ilike(search_term)) |
        (User.last_name.ilike(search_term))
    ).filter(User.is_active == True).limit(limit).all()

    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_token_payload)
):
    """GET /api/v1/users/{id} - Get user by ID (self/admin/security)"""

    # Check if user has permission to access this user's data
    if not can_access_user(token_payload, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this user"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    token_payload: dict = Depends(get_token_payload)
):
    """PUT /api/v1/users/{id} - Update user (self limited / admin full)"""

    # Check if user has permission to modify this user's data
    if not can_modify_user(token_payload, user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Update fields
    # If user is updating themselves (not admin), limit what they can change
    update_data = user_update.model_dump(exclude_unset=True)

    # Check if this is self-update (not admin)
    from app.core.security import is_admin
    if not is_admin(token_payload) and token_payload.get("sub") == user_id:
        # Users can only update these fields themselves
        allowed_fields = {"first_name", "last_name", "phone", "laptop_model", "laptop_asset_number", "photo_url"}
        update_data = {k: v for k, v in update_data.items() if k in allowed_fields}

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)

    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """DELETE /api/v1/users/{id} - Delete user (admin only)"""

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()

    return {"message": "User deleted successfully"}


@router.delete("/")
async def delete_user_by_query(
    user_id: str = Query(..., description="User id to delete"),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """DELETE /api/v1/users/?user_id=... - Convenience wrapper to accept query param for delete."""
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    user.is_active = False
    db.commit()

    return {"message": "User deleted successfully"}


@router.get("/stats/count")
async def get_user_count(
    building_id: Optional[str] = None,
    programme: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get user count with optional filters"""

    query = db.query(User).filter(User.is_active == True)

    if building_id:
        query = query.filter(User.building_id == building_id)

    if programme:
        query = query.filter(User.programme == programme)

    count = query.count()

    return {"count": count}
