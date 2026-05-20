"""
VentureLens AI — Simple Bearer Token Auth
Set VENTURELENS_API_KEY in .env to enable auth.
If the env var is not set, auth is disabled (dev mode).
"""

import os
from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

_security = HTTPBearer(auto_error=False)

def get_api_key() -> str | None:
    return os.getenv("VENTURELENS_API_KEY")


async def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Security(_security),
):
    """
    Dependency — inject into any route to require Bearer auth.
    Skipped automatically if VENTURELENS_API_KEY is not set (local dev).
    """
    api_key = get_api_key()
    if not api_key:
        return   # Auth disabled in dev mode

    if credentials is None or credentials.credentials != api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key.",
            headers={"WWW-Authenticate": "Bearer"},
        )