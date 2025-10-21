from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_id(prefix: str, counter: int) -> str:
    """Generate formatted ID (e.g., USR-001, BK-123)"""
    return f"{prefix}-{counter:03d}"


def is_admin(token_payload: dict) -> bool:
    """Check if user is an admin"""
    role = token_payload.get("role")
    return role == "admin" or role == "super_admin"


def is_security(token_payload: dict) -> bool:
    """Check if user is a security officer"""
    return token_payload.get("role") == "security"


def can_access_user(token_payload: dict, user_id: str) -> bool:
    """Check if user can access another user's data"""
    # Admin can access anyone
    if is_admin(token_payload):
        return True

    # Security can access anyone
    if is_security(token_payload):
        return True

    # Users can only access their own data
    return token_payload.get("sub") == user_id


def can_modify_user(token_payload: dict, user_id: str) -> bool:
    """Check if user can modify another user's data"""
    # Admin can modify anyone
    if is_admin(token_payload):
        return True

    # Users can only modify their own data
    return token_payload.get("sub") == user_id
