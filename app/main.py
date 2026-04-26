"""Ứng dụng FastAPI LancerAI — entry point."""

from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.lifespan import lifespan
from app.core.settings import settings
from app.router.v1 import (
    auth_api,
    extraction_api,
    interview_api,
    job_matching_api,
    optimization_api,
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
    allow_origins=["*"] if settings.app_debug else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["system"])
async def root() -> dict[str, Any]:
    """Banner dịch vụ & danh sách bề mặt API công khai."""
    return {
        "service": "LancerAI",
        "version": app.version,
        "status": "ok",
        "docs": "/docs",
        "health": "/health",
        "api_prefix": "/api/v1",
        "endpoints": [
            "POST /api/v1/auth/signup",
            "POST /api/v1/auth/login",
            "GET  /api/v1/auth/me",
            "POST /api/v1/extraction/upload",
            "GET  /api/v1/extraction/cv/{cv_id}",
            "POST /api/v1/optimization/analyze",
            "POST /api/v1/optimization/render_template",
            "GET  /api/v1/optimization/render_template_pdf",
            "POST /api/v1/jobs/match",
            "GET  /api/v1/jobs/recommendations/{cv_id}",
            "POST /api/v1/interview/sessions",
            "GET  /api/v1/interview/sessions/{session_id}/report",
            "WS   /api/v1/interview/ws",
        ],
    }


@app.get("/health", tags=["system"])
async def health() -> dict[str, Any]:
    return {"status": "healthy", "env": settings.app_env}


app.include_router(auth_api.router, prefix="/api/v1")
app.include_router(extraction_api.router, prefix="/api/v1")
app.include_router(optimization_api.router, prefix="/api/v1")
app.include_router(job_matching_api.router, prefix="/api/v1")
app.include_router(interview_api.router, prefix="/api/v1")
