"""FastAPI application lifespan."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import get_logger
from app.core.settings import get_settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    s = get_settings()
    logger.info("[startup] env=%s debug=%s", s.app_env, s.app_debug)

    if not s.app_debug and not s.allowed_origins:
        logger.warning("[CORS] allowed_origins is empty — all cross-origin requests will be rejected.")

    strict_db_startup = s.app_env in ("production", "staging")

    from sqlalchemy import text

    from app.core.database import get_engine

    try:
        async with get_engine().begin() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("[startup] database connection OK")
    except Exception as e:
        logger.error("[startup] database connection FAILED: %s", e)
        if strict_db_startup:
            raise RuntimeError(
                "Database unreachable during startup — refusing to boot in "
                f"app_env={s.app_env!r}. Fix DATABASE_URL connectivity."
            ) from e

    try:
        from app.core.providers.connectors import get_vector_repository

        await asyncio.get_running_loop().run_in_executor(None, get_vector_repository)
        logger.info("[startup] vector repository warmed up")
    except Exception as e:
        logger.warning("[startup] vector repository warm-up failed: %s", e)

    yield
    logger.info("[shutdown] application stopped")
