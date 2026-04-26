"""FastAPI application lifespan.

Currently logs startup / shutdown only. Add database, Redis, or model warm-up
here as those subsystems are connected (see TODO.md).
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.logger import get_logger
from app.core.settings import settings

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup / shutdown hooks.

    TODO (when implementing):
        - Verify database connectivity (SELECT 1) and bootstrap default tenants.
        - Pre-warm singleton connectors (LLM HTTP client, STT model, TTS engine).
        - Wire Redis / Celery health check.
        - Close all resources on shutdown.
    """
    logger.info("[startup] env=%s debug=%s", settings.app_env, settings.app_debug)
    yield
    logger.info("[shutdown] application stopped")
