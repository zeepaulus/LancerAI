"""Module 3 — Job matching."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_extraction_service, get_matching_service
from app.core.rate_limit import limiter
from app.models.user import User
from app.schema.request import JobMatchRequest
from app.schema.response import JobMatchResponse, JobRecommendationResponse
from app.service.extraction.service import ExtractionService
from app.service.matching.service import MatchingService

router = APIRouter(prefix="/jobs", tags=["job-matching"])


@router.post("/matches", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def match_cv_to_jd(
    request: Request,
    body: JobMatchRequest,
    service: Annotated[MatchingService, Depends(get_matching_service)],
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> JobMatchResponse:
    """Score a CV against a Job Description using Hybrid Scoring (frequency/position/semantic)."""
    cv = await extraction.get_cv(db, body.cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )
    try:
        result = await service.match_cv_to_jd(
            cv_data=cv.extracted_data or {},
            jd_text=getattr(body, "jd_text", "") or "",
            jd_url=getattr(body, "jd_url", "") or "",
        )
        try:
            await service.save_match_result(db, user_id=user.id, cv_id=body.cv_id, result=result)
        except Exception as _save_exc:
            import logging as _logging
            _logging.getLogger(__name__).warning("Failed to persist match scores: %s", _save_exc)
        return result
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Matching failed: {exc}",
        ) from exc


@router.get("/recommendations/{cv_id}")
@limiter.limit("30/minute")
async def get_recommendations(
    request: Request,
    cv_id: str,
    service: Annotated[MatchingService, Depends(get_matching_service)],
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
) -> list[JobRecommendationResponse]:
    """Return ranked job recommendations via vector similarity search."""
    cv = await extraction.get_cv(db, cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )
    return await service.get_recommendations(cv_data=cv.extracted_data or {}, limit=limit)
