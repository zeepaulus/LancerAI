"""Tests for get_current_user dependency — branch coverage."""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.providers.auth import get_current_user
from app.core.providers.repositories import get_user_repository
from app.core.security import create_access_token, hash_password
from app.core.settings import get_settings
from app.models.user import User, UserRole
from app.repository.relational_repository import RelationalRepository
from app.service.auth.service import AuthService


def _make_auth_service() -> AuthService:
    return AuthService(user_repository=get_user_repository(), settings=get_settings())


@pytest.fixture
def user_repo() -> RelationalRepository[User]:
    return get_user_repository()


class TestNoAuthHeader:
    @pytest.mark.asyncio
    async def test_raises_401(
        self,
        async_db_session: AsyncSession,
        user_repo: RelationalRepository[User],
    ) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=async_db_session, auth=_make_auth_service(), authorization=None)
        assert exc_info.value.status_code == 401


class TestAuthorizationFormat:
    @pytest.mark.asyncio
    async def test_non_bearer_raises_401(self, async_db_session: AsyncSession) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                db=async_db_session,
                auth=_make_auth_service(),
                authorization="Basic abc",
            )
        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_bearer_without_token_raises_401(self, async_db_session: AsyncSession) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(db=async_db_session, auth=_make_auth_service(), authorization="Bearer")
        assert exc_info.value.status_code == 401


class TestBearerInvalidToken:
    @pytest.mark.asyncio
    async def test_invalid_jwt_raises_401(self, async_db_session: AsyncSession) -> None:
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                db=async_db_session,
                auth=_make_auth_service(),
                authorization="Bearer not.a.valid.jwt",
            )
        assert exc_info.value.status_code == 401


class TestBearerValidToken:
    @pytest.mark.asyncio
    async def test_resolves_user(
        self,
        async_db_session: AsyncSession,
        user_repo: RelationalRepository[User],
    ) -> None:
        uid = "11111111-1111-1111-1111-111111111111"
        await user_repo.create(
            async_db_session,
            id=uid,
            tenant_id=uid,
            email="whoami@test.example",
            display_name="Who",
            password_hash=hash_password("password123"),
            role=UserRole.USER,
            is_active=True,
        )
        token = create_access_token(uid, uid, UserRole.USER.value)
        user = await get_current_user(
            db=async_db_session,
            auth=_make_auth_service(),
            authorization=f"Bearer {token}",
        )
        assert isinstance(user, User)
        assert user.id == uid
        assert user.email == "whoami@test.example"


class TestResolveTokenNotImplemented:
    """Valid JWT but ``resolve_token`` raises NotImplementedError.

    Since AuthService.resolve_token is fully implemented, the old 501 catch
    was dead code and has been removed.  If a subclass still raises
    NotImplementedError, it should propagate as-is (not be converted to 501).
    """

    @pytest.mark.asyncio
    async def test_propagates_not_implemented(self, async_db_session: AsyncSession) -> None:
        class StubAuth(AuthService):
            async def resolve_token(self, session: AsyncSession, token: str) -> User:
                raise NotImplementedError

        stub = StubAuth(user_repository=get_user_repository(), settings=get_settings())
        token = create_access_token(
            "22222222-2222-2222-2222-222222222222",
            "22222222-2222-2222-2222-222222222222",
            UserRole.USER.value,
        )
        with pytest.raises(NotImplementedError):
            await get_current_user(db=async_db_session, auth=stub, authorization=f"Bearer {token}")

