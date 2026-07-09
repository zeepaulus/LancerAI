"""Auth: register, login, current user."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_auth_service
from app.core.rate_limit import limiter
from app.models.user import User
from app.schema.request import AuthLoginRequest, AuthSignupRequest, PasswordChangeRequest, UserProfileUpdateRequest
from app.schema.response import AuthTokenResponse, UserProfileResponse
from app.service.auth.service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def signup(
    request: Request,
    payload: AuthSignupRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserProfileResponse:
    """Create a new account and return basic user info."""
    user = await auth.signup(
        db,
        payload.email,
        payload.password,
        payload.display_name,
        tenant_id=payload.tenant_id,
    )
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        tenant_id=user.tenant_id,
        role=user.role.value,
    )


@router.post("/login")
@limiter.limit("100/minute")
async def login(
    request: Request,
    payload: AuthLoginRequest,
    auth: Annotated[AuthService, Depends(get_auth_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> AuthTokenResponse:
    """Verify credentials and return ``{access_token, token_type}``."""
    token = await auth.login(db, payload.identifier, payload.password)
    return AuthTokenResponse(access_token=token)


@router.get("/me")
@limiter.limit("100/minute")
async def me(request: Request, current_user: Annotated[User, Depends(get_current_user)]) -> UserProfileResponse:
    """Return the calling user's profile."""
    return UserProfileResponse(
        id=current_user.id,
        email=current_user.email,
        display_name=current_user.display_name,
        tenant_id=current_user.tenant_id,
        role=current_user.role.value,  # serialize enum as plain string
    )


@router.patch("/me")
@limiter.limit("30/minute")
async def update_me(
    request: Request,
    payload: UserProfileUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserProfileResponse:
    """Update the current user's visible profile information."""
    user = await auth.update_profile(db, current_user, display_name=payload.display_name)
    return UserProfileResponse(
        id=user.id,
        email=user.email,
        display_name=user.display_name,
        tenant_id=user.tenant_id,
        role=user.role.value,
    )


@router.put("/password")
@limiter.limit("10/minute")
async def change_password(
    request: Request,
    payload: PasswordChangeRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> dict[str, str]:
    """Change the current user's password."""
    await auth.change_password(
        db,
        current_user,
        current_password=payload.current_password,
        new_password=payload.new_password,
    )
    return {"status": "success"}
