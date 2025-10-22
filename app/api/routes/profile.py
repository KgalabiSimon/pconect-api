from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserResponse, UserProfileUpdate
from app.api.routes.auth import get_current_user

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/profile")

class PasswordChangeRequest(BaseModel):
    new_password: str
    confirm_password: str

@router.post("/reset-password")
async def reset_password(
    data: PasswordChangeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    from app.core.security import get_password_hash
    if data.new_password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    current_user.hashed_password = get_password_hash(data.new_password)
    db.commit()
    db.refresh(current_user)
    return {"message": "Password updated successfully"}
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserResponse, UserProfileUpdate
from app.api.routes.auth import get_current_user

router = APIRouter(prefix="/api/v1/profile")


@router.put("/", response_model=UserResponse)
async def update_profile(
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """PUT /api/v1/profile - Update current user's own profile (self only)"""

    # Update fields - users can only update their own profile
    # Limited to safe fields
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(current_user, field, value)

    db.commit()
    db.refresh(current_user)

    return current_user
