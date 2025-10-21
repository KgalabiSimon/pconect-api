# Check if user can access or modify another user's data
def can_access_user(token_payload: dict, user_id: str) -> bool:
    """Check if user can access another user's data"""
    if is_admin(token_payload):
        return True
    return token_payload.get("sub") == user_id

def can_modify_user(token_payload: dict, user_id: str) -> bool:
    """Check if user can modify another user's data"""
    if is_admin(token_payload):
        return True
    return token_payload.get("sub") == user_id
# Check if user is admin (for use in routes)
def is_admin(token_payload: dict) -> bool:
    """Check if user is an admin"""
    role = token_payload.get("role")
    return role == "admin" or role == "super_admin"
# Utility: Generate formatted IDs (USR-001, etc)
def generate_id(prefix: str, counter: int) -> str:
    """Generate formatted ID (e.g., USR-001, BK-123)"""
    return f"{prefix}-{counter:03d}"
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    ok = pwd_context.verify(plain_password, hashed_password)
    # optional: if you ever add legacy schemes later, you can rehash here
    return ok

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_access_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None
