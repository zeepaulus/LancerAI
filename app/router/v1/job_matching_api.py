"""Module 3 — Job matching.

MVP MOCK:
    Match endpoint returns deterministic fake scores within valid schema ranges.
    Replace with hybrid scoring (frequency/position/semantic) when implementing.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_extraction_service, get_matching_service
from app.core.rate_limit import limiter
from app.models.user import User
from app.schema.request import JobMatchRequest
from app.schema.response import JobMatchResponse, JobRecommendationResponse, SkillGap
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
    """Score a CV against a Job Description (URL or text).

    MVP MOCK: validates cv_id ownership, returns deterministic scores.
    TODO: replace with hybrid scoring (frequency/position/semantic).
    """
    # Ownership check
    cv = await extraction.get_cv(db, body.cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )

    # MVP MOCK: deterministic scores within valid range (0-100)
    return JobMatchResponse(
        overall_score=68.5,
        frequency_score=55.0,
        position_score=72.0,
        semantic_score=78.5,
        improvement_feedback=(
            "MVP MOCK: Consider adding cloud certifications and quantifying project impacts. "
            "TODO: replace with real LLM feedback."
        ),
        missing_skills=[
            SkillGap(
                skill_name="Kubernetes",
                impact_level="critical",
                reason="Required by 80% of similar roles.",
            ),
            SkillGap(
                skill_name="CI/CD Pipeline Design",
                impact_level="important",
                reason="Mentioned in JD requirements section.",
            ),
        ],
    )


@router.get("/recommendations/{cv_id}")
@limiter.limit("100/minute")
async def get_recommendations(
    request: Request,
    cv_id: str,
    service: Annotated[MatchingService, Depends(get_matching_service)],
    user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
    offset: int = 0,
) -> list[JobRecommendationResponse]:
    """Return ranked job recommendations for the given CV.

    TODO: implement vector similarity search over job_listings collection.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GET /jobs/recommendations/{cv_id} is not implemented yet.",
    )
