"""Auth dependency — resolves the current authenticated user per request."""

from __future__ import annotations

from typing import Annotated, Any

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.services import get_auth_service
from app.core.security import decode_access_token
from app.models.user import User
from app.service.auth.service import AuthService


def validate_ws_token(token: str | None) -> dict[str, Any]:
    """Validate a WebSocket payload token. Raises on missing or invalid token."""
    if not token:
        raise ValueError("No token provided")
    return decode_access_token(token)


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Resolve the authenticated user for every protected endpoint.

    - Missing Authorization → 401.
    - Non-Bearer or malformed Bearer → 401.
    - Invalid/expired JWT or unknown/inactive user → 401.
    """
    auth_hdr = (authorization or "").strip()
    if auth_hdr:
        parts = auth_hdr.split()
        if len(parts) >= 2 and parts[0].lower() == "bearer":
            token = parts[1].strip()
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Bearer token missing.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            try:
                decode_access_token(token)
            except jwt.ExpiredSignatureError as exc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc
            except jwt.InvalidTokenError as exc:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token.",
                    headers={"WWW-Authenticate": "Bearer"},
                ) from exc
            return await auth.resolve_token(db, token)

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header. Expected: Bearer <token>.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required. Provide a valid Bearer token.",
        headers={"WWW-Authenticate": "Bearer"},
    )
