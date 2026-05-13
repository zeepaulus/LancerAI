"""conftest.py — Shared pytest fixtures.

Sets test env vars BEFORE any app import so Settings validation passes.
Provides:
- async_db_session: per-test in-memory SQLite session (no PostgreSQL needed)
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path

# Must be set before any app module is imported.
os.environ.setdefault("APP_ENV", "test")
# Force a strong test secret so developer shells cannot override with a weak key.
os.environ["AUTH_SECRET_KEY"] = "test-secret-key-for-ci-only-32chars!!"
os.environ.setdefault("AUTH_ALLOW_WEAK_SECRET", "true")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("NEO4J_PASSWORD", "test-neo4j-pw")
# Avoid Chroma HttpClient to an unreachable server when developer .env points at localhost:8001.
_chroma_test_dir = Path(__file__).resolve().parent / ".chromadb_pytest_data"
os.environ["VECTOR_DB_HOST"] = str(_chroma_test_dir)

import pytest_asyncio  # noqa: E402
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine  # noqa: E402

from app.models import (  # noqa: E402, F401 — ensure all tables are registered
    cv_record,
    interview_session,
    interview_transcript,
    job_listing,
    job_match_result,
    user,
)
from app.models.base import Base  # noqa: E402

_TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Fresh in-memory SQLite session per test function."""
    engine = create_async_engine(_TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()
