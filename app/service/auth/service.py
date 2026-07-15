"""Authentication service.

Owns the user lifecycle for the SaaS surface: signup, login, token resolution.
Routers depend on this service via ``get_auth_service`` so they don't touch
``security`` or ``RelationalRepository`` directly.
"""

from __future__ import annotations

import uuid

import jwt
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.core.settings import Settings
from app.models.user import User, UserRole
from app.repository.relational_repository import RelationalRepository


class AuthService:
    """User registration / login / JWT resolution."""

    def __init__(self, user_repository: RelationalRepository[User], settings: Settings) -> None:
        self._users = user_repository
        self._settings = settings

    async def signup(
        self,
        session: AsyncSession,
        email: str,
        password: str,
        display_name: str,
        *,
        tenant_id: str | None = None,
    ) -> User:
        """Create a new user and return the persisted record."""
        email_norm = email.lower().strip()
        display_name_norm = display_name.strip()
        
        if not display_name_norm:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Display name is required.",
            )

        existing_email = await self._users.filter_by(session, email=email_norm, limit=1)
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered.",
            )

        existing_name = await self._users.filter_by(session, display_name=display_name_norm, limit=1)
        if existing_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Display name already registered.",
            )

        user_id = str(uuid.uuid4())
        # Security: ignore client-provided tenant_id until organization/invite
        # flow is implemented. Each user is their own tenant for now.
        # TODO: support tenant_id when invite/organization flow exists.
        tenant = user_id
        pwd_hash = hash_password(password)

        try:
            return await self._users.create(
                session,
                id=user_id,
                tenant_id=tenant,
                email=email_norm,
                display_name=display_name_norm,
                password_hash=pwd_hash,
                role=UserRole.USER,
                is_active=True,
            )
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email or display name already registered.",
            ) from None

    async def login(self, session: AsyncSession, identifier: str, password: str) -> str:
        """Verify credentials and return a signed access token."""
        ident_norm = identifier.lower().strip()
        if "@" in ident_norm:
            rows = await self._users.filter_by(session, email=ident_norm, limit=1)
        else:
            rows = await self._users.filter_by(session, display_name=identifier.strip(), limit=1)
        user = rows[0] if rows else None

        if user is None or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return create_access_token(user.id, user.tenant_id, user.role.value)

    async def update_profile(
        self,
        session: AsyncSession,
        user: User,
        *,
        display_name: str,
    ) -> User:
        """Update mutable profile fields for the current user."""
        cleaned_name = display_name.strip()
        if not cleaned_name:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Display name is required.",
            )

        updated = await self._users.update(session, user.id, display_name=cleaned_name)
        if updated is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        await session.commit()
        await session.refresh(updated)
        return updated

    async def change_password(
        self,
        session: AsyncSession,
        user: User,
        *,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change password after verifying the existing credential."""
        if not verify_password(current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect.",
            )
        if current_password == new_password:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="New password must be different from the current password.",
            )

        await self._users.update(session, user.id, password_hash=hash_password(new_password))
        await session.commit()

    async def resolve_token(self, session: AsyncSession, token: str) -> User:
        """Decode ``token`` and return the matching active User."""
        try:
            payload = decode_access_token(token)
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

        sub = payload.get("sub")
        if sub is None or sub == "":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        user = await self._users.get_by_id(session, str(sub))
        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user
