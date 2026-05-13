"""Async SQLAlchemy engine + session factory — lazy initialization.

Engine is created on first use so the app can boot when PostgreSQL is not
reachable yet, and test suites can override the DB URL via env vars before
any import triggers connection.
"""

from __future__ import annotations

import logging
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import get_settings

_logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_engine() -> AsyncEngine:
    """Create the engine once, lazily, after settings are available."""
    s = get_settings()

    engine_kwargs: dict[str, Any] = {
        "echo": s.database_echo,
        "pool_pre_ping": True,
    }

    if not s.database_url.startswith("sqlite"):
        engine_kwargs["pool_size"] = s.database_pool_size
        engine_kwargs["max_overflow"] = s.database_max_overflow

    return create_async_engine(s.database_url, **engine_kwargs)


def get_engine() -> AsyncEngine:
    """Public accessor for lifespan, migrations, scripts — same lazy singleton."""
    return _get_engine()


def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=_get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency — yields a per-request async DB session.

    TODO(transaction-policy): This dependency auto-commits after successful requests.
        Prefer migrating write paths to explicit ``session.commit()`` for clearer
        transaction boundaries once services are audited for partial-failure handling.
    """
    async with _get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            _logger.exception("DB session error — rolling back", exc_info=True)
            await session.rollback()
            raise
