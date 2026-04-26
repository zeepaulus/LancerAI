"""Auth: register, login, current user."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_auth_service, get_current_user
from app.models.user import User
from app.schema.request import AuthLoginRequest, AuthSignupRequest
from app.service.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup")
async def signup(
    payload: AuthSignupRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Create a new account and return basic user info.

    TODO: call ``auth.signup`` and return ``{user_id, email, display_name}``.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="POST /auth/signup is not implemented yet.",
    )


@router.post("/login")
async def login(
    payload: AuthLoginRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, Any]:
    """Verify credentials and return ``{access_token, token_type}``.

    TODO: call ``auth.login`` and return the JWT.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="POST /auth/login is not implemented yet.",
    )


@router.get("/me")
async def me(current_user: Annotated[User, Depends(get_current_user)]) -> dict[str, Any]:
    """Return the calling user's profile."""
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "tenant_id": getattr(current_user, "tenant_id", None),
        "role": current_user.role,
    }
