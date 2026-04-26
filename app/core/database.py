"""Async SQLAlchemy engine + session factory.

The engine is created lazily so the app can boot when PostgreSQL is not
reachable yet. Use ``get_db_session`` as a FastAPI dependency.

TODO:
    - Replace single shared engine with an organization-aware connection pool
      if each organization needs a separate database.
    - Add Alembic migration entrypoint hooks.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.settings import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    echo=_settings.database_echo,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session per request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
