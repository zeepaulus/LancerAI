"""Alembic environment configuration.

Configured for async SQLAlchemy with asyncpg.
Reads database URL from app.core.settings (respects .env file).
Auto-detects all ORM models via app.models.base.Base.
"""

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

# ---------------------------------------------------------------------------
# Alembic Config object — access to values in alembic.ini
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# Import ALL models so Alembic can detect schema changes via autogenerate.
# Each model MUST be imported here (or transitively) to be detected.
# ---------------------------------------------------------------------------
from app.models import (  # noqa: F401, E402
    cv_record,
    interview_session,
    interview_transcript,
    job_listing,
    job_match_result,
    user,
)
from app.models.base import Base  # noqa: E402

target_metadata = Base.metadata

# ---------------------------------------------------------------------------
# Get DB URL from app settings (honours .env file)
# ---------------------------------------------------------------------------
from app.core.settings import get_settings  # noqa: E402

_settings = get_settings()


def get_url() -> str:
    return _settings.database_url


# ---------------------------------------------------------------------------
# Offline migrations (no live DB connection required)
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    """Run migrations without a live database connection.

    Useful for generating SQL scripts for review before applying.
    """
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online migrations (connects to the live DB)
# ---------------------------------------------------------------------------
def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations."""
    connectable = create_async_engine(get_url(), poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Entry point for online migrations."""
    asyncio.run(run_async_migrations())


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
