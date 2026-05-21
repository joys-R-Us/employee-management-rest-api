from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

import os
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# Password hashing (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# --- JWT configuration ---

# If the app calls app.auth.loader.load_env() during startup, these will be read from .env.
# Otherwise they fall back to the defaults below.
SECRET_KEY = os.getenv("SECRET_KEY", "change-me")
ALGORITHM = os.getenv("ALGORITHM", "HS256")


ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2 scheme; token URL should point to your login endpoint.
# If your login endpoint differs, adjust tokenUrl accordingly.
# Your login endpoint is registered as POST /auth/login (see app/auth/route/auth.py)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Create a signed JWT.

    Expects `data` to contain at least identifiers your app needs (e.g. user_id, role).
    """

    expire = datetime.now(timezone.utc) + (
        expires_delta if expires_delta is not None else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode = dict(data)
    # jose validates `sub` as a string when decoding
    if "sub" in to_encode and to_encode["sub"] is not None:
        to_encode["sub"] = str(to_encode["sub"])

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def _get_payload_from_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from exc


def get_current_user(token: str = Depends(oauth2_scheme)) -> Any:
    """Decode JWT and return current user-like object.

    This function returns a simple object with `role` and any other claims found.
    If your project has a real User model, you can extend this to fetch from DB.
    """

    payload = _get_payload_from_token(token)

    role = payload.get("role")
    if role is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


    user_id = payload.get("sub") or payload.get("user_id") or payload.get("id")
    if user_id is not None:
        user_id = str(user_id)

    # Minimal user object compatible with get_current_admin(role-based dependency)
    return type("TokenUser", (), {"id": user_id, "role": role, "claims": payload})()


