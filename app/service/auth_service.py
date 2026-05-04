"""Authentication service.

Owns the user lifecycle for the SaaS surface: signup, login, token resolution.
Routers depend on this service via ``get_auth_service`` so they don't touch
``security`` or ``RelationalRepository`` directly.

TODO:
    - Implement ``signup`` (validate email uniqueness, hash password,
      provision tenant_id, persist via ``user_repository``).
    - Implement ``login`` (verify password, issue JWT via ``security``).
    - Implement ``resolve_token`` (decode JWT, fetch user from DB).
    - Add password reset / email verification flows when needed.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.settings import Settings
from app.models.user import User
from app.repository.relational_repository import RelationalRepository


class AuthService:
    """User registration / login / JWT resolution."""

    def __init__(self, user_repository: RelationalRepository, settings: Settings) -> None:
        self._users = user_repository
        self._settings = settings

    async def signup(
        self,
        session: AsyncSession,
        email: str,
        password: str,
        display_name: str,
    ) -> User:
        """Create a new user + tenant and return the persisted record."""
        raise NotImplementedError("AuthService.signup is not implemented yet.")

    async def login(self, session: AsyncSession, email: str, password: str) -> str:
        """Verify credentials and return a signed access token."""
        raise NotImplementedError("AuthService.login is not implemented yet.")

    async def resolve_token(self, session: AsyncSession, token: str) -> User:
        """Decode ``token`` and return the matching active User."""
        raise NotImplementedError("AuthService.resolve_token is not implemented yet.")
