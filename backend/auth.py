"""
VentureLens AI — JWT Authentication
- Passwords hashed with bcrypt
- JWT access tokens (24h expiry)
- User data isolated per user_id
Install: pip install python-jose[cryptography] passlib[bcrypt]
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

logger = logging.getLogger("VentureLens.Auth")

# ── Config ─────────────────────────────────────────────────────────────────────
SECRET_KEY  = os.getenv("JWT_SECRET_KEY", "venturelens-dev-secret-change-in-production")
ALGORITHM   = "HS256"
TOKEN_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login", auto_error=False)


# ── Pydantic models ────────────────────────────────────────────────────────────
class UserCreate(BaseModel):
    email:    str
    password: str
    name:     str = ""

class UserLogin(BaseModel):
    email:    str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    user_id:      int
    email:        str
    name:         str

class CurrentUser(BaseModel):
    id:    int
    email: str
    name:  str


# ── Password helpers ───────────────────────────────────────────────────────────
def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT helpers ────────────────────────────────────────────────────────────────
def create_access_token(user_id: int, email: str) -> str:
    payload = {
        "sub":   str(user_id),
        "email": email,
        "exp":   datetime.utcnow() + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


# ── FastAPI dependency ─────────────────────────────────────────────────────────
async def get_current_user(token: Optional[str] = Depends(oauth2_scheme)) -> CurrentUser:
    """Inject into any route that requires authentication."""
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Please log in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(token)
    user_id = int(payload.get("sub", 0))
    email   = payload.get("email", "")

    # Load user from DB to get name and confirm still exists
    from services.db import get_user_by_id
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found.")

    return CurrentUser(id=user_id, email=email, name=user.get("name", ""))


# ── Optional auth (for public endpoints that can be enhanced if logged in) ─────
async def optional_user(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[CurrentUser]:
    if not token:
        return None
    try:
        return await get_current_user(token)
    except HTTPException:
        return None