from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.utils import create_access_token, verify_password


# These imports are expected to exist in the project.
# If your project uses different module paths, adjust accordingly.
from app.db.session import get_db  # type: ignore
from app import models  # type: ignore
from app.models import User  # type: ignore


router = APIRouter(prefix="/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Authenticate user and return JWT.

    Expects your users table/model to store:
      - username (or email) to locate the user
      - password_hash (hashed with app.auth.utils.verify_password)
      - role (e.g. "Admin")

    Adjust the field names in the user lookup if your model differs.
    """

    username = form_data.username
    password = form_data.password

    # Adjust these fields to match your actual SQLAlchemy model.
    user = None
    if hasattr(models, "User"):
        user = db.query(models.User).filter(models.User.username == username).first()  # type: ignore[attr-defined]
    else:
        # Fallback if your model lives in app.models.User
        user = db.query(User).filter(User.username == username).first()  # type: ignore[attr-defined]

    if not user:
        # Generic message to reduce user-enumeration risk
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )


    stored_hash = getattr(user, "password_hash", None)
    if not stored_hash:
        # Avoid leaking whether the username exists or whether password_hash is present.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not verify_password(password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    role = getattr(user, "role", None)
    if role is None:
        # Avoid leaking role presence/absence.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials",
        )


    user_id = getattr(user, "id", None) or getattr(user, "user_id", None)

    access_token = create_access_token({"sub": str(user_id) if user_id is not None else username, "role": role})

    return {"access_token": access_token, "token_type": "bearer"}

