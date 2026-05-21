"""Authentication/authorization helpers.

This module provides dependency(s) to protect routes by role.
"""

from fastapi import Depends, HTTPException, status


# NOTE:
# Your project likely defines `User` and `get_current_user` elsewhere.
# We import them lazily via try/except so this file can still be analyzed
# by type checkers without hard-coding your app structure.

from app.auth.utils import get_current_user


try:
    # Update the import path below to match your project.
    from app.models import User  # type: ignore
except Exception:  # pragma: no cover
    class User:  # type: ignore
        role: str


def get_current_admin(current_user: "User" = Depends(get_current_user)):
    """Dependency that allows only users with role == 'Admin'."""
    if current_user.role != "Admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to perform this action",
        )
    return current_user

