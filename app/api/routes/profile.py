from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User
from app.schemas.users import UserResponse, UserProfileUpdate
from app.api.routes.auth import get_current_user

router = APIRouter()


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
