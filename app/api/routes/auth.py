from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
from app.db.database import get_db
from app.db.models import User, AdminUser, SecurityOfficer
from app.schemas.auth import Token, AdminLogin, SecurityLogin, UserLogin, PasswordResetRequest
from app.schemas.users import UserCreate, UserResponse
from app.schemas.admin import AdminCreate
from app.schemas.security import SecurityRegister

router = APIRouter(prefix="/api/v1/auth")

# Security officer registration endpoint
@router.post("/security/register", status_code=status.HTTP_201_CREATED)
async def register_security_officer(officer_data: SecurityRegister, db: Session = Depends(get_db)):
    """Register a new security officer"""
    # Check if badge number already exists
    existing = db.query(SecurityOfficer).filter(SecurityOfficer.badge_number == officer_data.badge_number).first()
    if existing:
        raise HTTPException(status_code=400, detail="Badge number already registered")

    import uuid
    from app.core.security import get_password_hash
    hashed_pin = get_password_hash(officer_data.pin)

    new_officer = SecurityOfficer(
        id=str(uuid.uuid4()),
        badge_number=officer_data.badge_number,
        hashed_pin=hashed_pin,
        first_name=officer_data.first_name,
        last_name=officer_data.last_name,
        is_active=officer_data.is_active
    )
    db.add(new_officer)
    db.commit()
    db.refresh(new_officer)
    return {
        "id": new_officer.id,
        "badge_number": new_officer.badge_number,
        "first_name": new_officer.first_name,
        "last_name": new_officer.last_name,
        "is_active": new_officer.is_active
    }




# Admin registration endpoint
@router.post("/admin/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_admin(admin_data: AdminCreate, db: Session = Depends(get_db)):
    """Register a new admin user (admin creation)"""

    # Check if email already exists
    existing_admin = db.query(AdminUser).filter(AdminUser.email == admin_data.email).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered as admin"
        )

    import uuid
    # Create new admin
    hashed_password = get_password_hash(admin_data.password)

    new_admin = AdminUser(
        id=str(uuid.uuid4()),
        email=admin_data.email,
        hashed_password=hashed_password,
        first_name=admin_data.first_name,
        last_name=admin_data.last_name,
        role=admin_data.role,
        is_active=admin_data.is_active
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    # Return as UserResponse for consistency (id, email, etc.)
    from app.schemas.users import UserResponse
    return UserResponse.from_orm(new_admin)
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
    generate_id,
    is_admin
)
from app.core.config import settings
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: str = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Get current authenticated admin from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    # Check if role is admin
    if not is_admin(payload):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    admin_id: str = payload.get("sub")
    if admin_id is None:
        raise credentials_exception

    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if admin is None:
        raise credentials_exception

    return admin


async def get_token_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Get token payload without database query"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    return payload


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user (self-registration)"""

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    import uuid
    # Generate custom user code (optional, if you want to keep USR-001 style)
    last_user = db.query(User).order_by(User.id.desc()).first()
    if last_user and hasattr(last_user, 'user_code') and last_user.user_code:
        last_num = int(last_user.user_code.split("-")[1])
        user_code = generate_id("USR", last_num + 1)
    else:
        user_code = generate_id("USR", 1)

    # Create new user
    hashed_password = get_password_hash(user_data.password)

    new_user = User(
        id=str(uuid.uuid4()),
  # You must add this column to your model/migration
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

    from app.schemas.users import UserResponse
    return UserResponse.from_orm(new_user)


@router.post("/login", response_model=Token)
async def login_user(user_data: UserLogin, db: Session = Depends(get_db)):
    """Login user with email/password and return JWT token"""

    # Find user by email
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": "user"},
        expires_delta=access_token_expires
    )

    from app.schemas.users import UserResponse
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(user).model_dump()
    }


@router.post("/admin/login", response_model=Token)
async def login_admin(admin_data: AdminLogin, db: Session = Depends(get_db)):
    """Admin login"""

    admin = db.query(AdminUser).filter(AdminUser.email == admin_data.email).first()

    if not admin or not verify_password(admin_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(admin.id), "email": admin.email, "role": admin.role}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(admin).model_dump()
    }


@router.post("/security/login", response_model=Token)
async def login_security(security_data: SecurityLogin, db: Session = Depends(get_db)):
    """Security officer login"""

    officer = db.query(SecurityOfficer).filter(
        SecurityOfficer.badge_number == security_data.badge_number
    ).first()

    if not officer or not verify_password(security_data.pin, officer.hashed_pin):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect badge number or PIN"
        )

    if not officer.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Security officer account is inactive"
        )

    # Create access token
    access_token = create_access_token(
        data={"sub": str(officer.id), "badge": officer.badge_number, "role": "security"}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": officer.id,
            "badge_number": officer.badge_number,
            "first_name": officer.first_name,
            "last_name": officer.last_name
        }
    }


@router.post("/password-reset/request")
async def request_password_reset(
    reset_request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset (sends email in production)"""

    user = db.query(User).filter(User.email == reset_request.email).first()

    if not user:
        # Don't reveal if email exists or not
        return {"message": "If the email exists, a password reset link has been sent"}

    # In production, generate reset token and send email
    # For now, just return success message

    return {"message": "Password reset link has been sent to your email"}



@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile"""
    return current_user