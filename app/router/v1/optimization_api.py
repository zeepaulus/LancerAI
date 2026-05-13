"""Module 2 — CV analysis and document export.

MVP MOCK:
    Optimization + render endpoints return deterministic fake data.
    Replace with LangGraph pipeline + Jinja2/WeasyPrint when implementing.
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import (
    get_extraction_service,
    get_optimization_service,
    get_template_renderer,
)
from app.core.rate_limit import limiter
from app.models.user import User
from app.schema.request import OptimizationRequest, RenderTemplateRequest
from app.schema.response import CVOptimizationResponse, RenderedCVResponse
from app.service.extraction.service import ExtractionService
from app.service.optimization.service import OptimizationService
from app.service.optimization.template_renderer import CVTemplateRenderer

router = APIRouter(prefix="/optimization", tags=["optimization"])


async def _check_cv_ownership(
    service: ExtractionService,
    db: AsyncSession,
    cv_id: str,
    user_id: str,
) -> Any:
    """Verify cv_id belongs to user_id. Returns the CVRecord or raises 404."""
    cv = await service.get_cv(db, cv_id, user_id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )
    return cv


@router.post("/cvs/{cv_id}/optimizations")
@limiter.limit("100/minute")
async def analyze_cv(
    request: Request,
    cv_id: str,
    body: OptimizationRequest,
    service: Annotated[OptimizationService, Depends(get_optimization_service)],
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> CVOptimizationResponse:
    """Run the multi-agent CV analysis pipeline.

    MVP MOCK: checks ownership, returns deterministic optimized_data.
    TODO: replace with LangGraph retrieval/roast/rewrite/audit pipeline.
    """
    cv = await _check_cv_ownership(extraction, db, cv_id, user.id)

    # MVP MOCK: deterministic optimized data
    optimized_data: dict[str, Any] = {
        **(cv.extracted_data or {}),
        "_optimization_applied": True,
        "_target_job_title": body.target_job_title or "General",
        "_target_industry": body.target_industry,
        "_mode": body.mode,
    }

    # Persist optimized_data back to the record
    cv.optimized_data = optimized_data
    await db.flush()

    return CVOptimizationResponse(
        cv_id=cv_id,
        audit_score=72.5,
        optimized_data=optimized_data,
    )


@router.post("/cvs/{cv_id}/render")
@limiter.limit("100/minute")
async def render_template_cv(
    request: Request,
    cv_id: str,
    body: RenderTemplateRequest,
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    renderer: Annotated[CVTemplateRenderer, Depends(get_template_renderer)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> RenderedCVResponse:
    """Render the optimized CV into a named template (returns JSON).

    MVP MOCK: checks ownership, returns deterministic rendered data.
    TODO: replace with Jinja2 template rendering via CVTemplateRenderer.
    """
    cv = await _check_cv_ownership(extraction, db, cv_id, user.id)
    source = cv.optimized_data or cv.extracted_data or {}

    return RenderedCVResponse(
        template_name=body.template,
        rendered_data={
            "template": body.template,
            "sections": list(source.keys()),
            "content": source,
            "_mock": True,
        },
    )


@router.get("/cvs/{cv_id}/pdf")
@limiter.limit("100/minute")
async def render_template_pdf(
    request: Request,
    cv_id: str,
    template: str,
    renderer: Annotated[CVTemplateRenderer, Depends(get_template_renderer)],
    user: Annotated[User, Depends(get_current_user)],
) -> StreamingResponse:
    """Stream a downloadable PDF rendered from the optimized CV.

    TODO: Implement with WeasyPrint when template rendering is ready.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="PDF export is not implemented yet. Use /render for JSON preview.",
    )
