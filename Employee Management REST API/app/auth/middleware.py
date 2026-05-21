from __future__ import annotations

from typing import Callable

from fastapi import HTTPException, Request
from jose import JWTError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.auth import utils


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Protects all endpoints except the explicitly allowed paths.

    Expects: Authorization: Bearer <token>
    Validates using the same JWT config as app.auth.utils.
    """

    def __init__(
        self,
        app,
        *,
        excluded_paths: list[str] | None = None,
    ):
        super().__init__(app)
        self.excluded_paths = excluded_paths or ["/auth/login", "/auth/register"]

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        # Skip auth for excluded routes
        if path in self.excluded_paths:
            return await call_next(request)

        # Require Bearer token
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.lower().startswith("bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
            )

        token = auth_header.split(" ", 1)[1].strip()
        try:
            payload = utils._get_payload_from_token(token)
        except HTTPException as exc:
            # Keep responses generic to avoid token-validation detail leaks.
            return JSONResponse(status_code=exc.status_code, content={"detail": "Could not validate credentials"})

        except JWTError:
            return JSONResponse(status_code=401, content={"detail": "Could not validate credentials"})

        # Attach claims so downstream dependencies can reuse if needed
        request.state.jwt_payload = payload

        return await call_next(request)

