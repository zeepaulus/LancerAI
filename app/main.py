"""Ứng dụng FastAPI LancerAI — entry point."""

from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.core.database import get_engine
from app.core.lifespan import lifespan
from app.core.logger import get_logger
from app.core.rate_limit import limiter
from app.core.settings import get_settings
from app.router.v1 import (
    auth_api,
    extraction_api,
    interview_api,
    job_matching_api,
    optimization_api,
)

logger = get_logger(__name__)
_settings = get_settings()

if _settings.app_env == "production" and not _settings.allowed_origins:
    logger.critical(
        "[CORS] allowed_origins is empty in production — cross-origin browser clients cannot call this API."
    )

app = FastAPI(
    title="LancerAI API",
    description=(
        "Trợ lý sự nghiệp: trích xuất & tối ưu CV, khớp việc làm, phỏng vấn giọng nói (PCM / STT / LLM / TTS)."
    ),
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(NotImplementedError)
async def _not_implemented_handler(_request: Request, exc: NotImplementedError) -> JSONResponse:
    detail = str(exc) or "Feature not implemented yet." if _settings.app_debug else "Feature not implemented yet."
    return JSONResponse(status_code=501, content={"detail": detail})


@app.get("/", tags=["system"])
async def root() -> dict[str, Any]:
    """Banner dịch vụ & danh sách bề mặt API công khai."""
    return {
        "service": "LancerAI",
        "version": app.version,
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "ready": "/ready",
        "api_prefix": "/api/v1",
        "endpoints": [
            "POST /api/v1/auth/signup",
            "POST /api/v1/auth/login",
            "GET  /api/v1/auth/me",
            "POST /api/v1/extraction/cvs",
            "GET  /api/v1/extraction/cv/{cv_id}",
            "POST /api/v1/optimization/cvs/{cv_id}/optimizations",
            "POST /api/v1/optimization/cvs/{cv_id}/render",
            "GET  /api/v1/optimization/cvs/{cv_id}/pdf",
            "POST /api/v1/jobs/matches",
            "GET  /api/v1/jobs/recommendations/{cv_id}",
            "POST /api/v1/interview/sessions",
            "GET  /api/v1/interview/sessions/{session_id}/report",
            "WS   /api/v1/interview/ws",
        ],
    }


@app.get("/health", tags=["system"])
async def health() -> dict[str, Any]:
    return {"status": "healthy", "env": _settings.app_env}


@app.get("/ready", tags=["system"])
async def ready() -> dict[str, Any]:
    """Readiness: verifies primary database connectivity (SELECT 1)."""
    try:
        async with get_engine().connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        logger.exception("Readiness check failed: database unreachable")
        raise HTTPException(
            status_code=503,
            detail={
                "status": "not_ready",
                "checks": {"database": f"error: {exc!s}"},
            },
        ) from exc
    return {"status": "ready", "checks": {"database": "ok"}}


app.include_router(auth_api.router, prefix="/api/v1")
app.include_router(extraction_api.router, prefix="/api/v1")
app.include_router(optimization_api.router, prefix="/api/v1")
app.include_router(job_matching_api.router, prefix="/api/v1")
app.include_router(interview_api.router, prefix="/api/v1")
