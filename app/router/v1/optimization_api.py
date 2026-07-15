"""Module 2 — CV analysis and document export."""

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
    """Run the multi-agent CV analysis pipeline (retrieval → roast → rewrite → audit)."""
    await _check_cv_ownership(extraction, db, cv_id, user.id)
    try:
        return await service.analyze_cv(
            cv_id=cv_id,
            user_id=user.id,
            session=db,
            target_job_title=body.target_job_title or "",
            target_industry=body.target_industry,
            mode=body.mode,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Optimization pipeline failed: {exc}",
        ) from exc


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
    """Render the optimized CV into a named template (returns JSON)."""
    cv = await _check_cv_ownership(extraction, db, cv_id, user.id)
    source = cv.optimized_data or cv.extracted_data or {}
    try:
        rendered = await renderer.render_cv(source, body.template)
        return RenderedCVResponse(template_name=body.template, rendered_data=rendered)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Render failed: {exc}",
        ) from exc


@router.get("/cvs/{cv_id}/pdf")
@limiter.limit("10/minute")
async def render_template_pdf(
    request: Request,
    cv_id: str,
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    renderer: Annotated[CVTemplateRenderer, Depends(get_template_renderer)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    template: str = "harvard",
) -> StreamingResponse:
    """Stream a downloadable PDF rendered from the optimized CV."""
    cv = await _check_cv_ownership(extraction, db, cv_id, user.id)
    source = cv.optimized_data or cv.extracted_data or {}
    try:
        pdf_bytes = await renderer.render_pdf(source, template)
        media_type = "application/pdf" if pdf_bytes[:4] == b"%PDF" else "application/json"
        filename = f"cv_{cv_id[:8]}_{template}.{'pdf' if media_type == 'application/pdf' else 'json'}"
        import io

        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF render failed: {exc}",
        ) from exc
