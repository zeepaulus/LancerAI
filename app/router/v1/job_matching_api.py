"""Module 3 — Job matching."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_current_user, get_matching_service
from app.models.user import User
from app.schema.request import JobMatchRequest
from app.service.matching_service import MatchingService

router = APIRouter(prefix="/jobs", tags=["job-matching"])


@router.post("/match")
async def match_cv_to_jd(
    body: JobMatchRequest,
    service: Annotated[MatchingService, Depends(get_matching_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Score a CV against a Job Description (URL or text)."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="POST /jobs/match is not implemented yet.",
    )


@router.get("/recommendations/{cv_id}")
async def get_recommendations(
    cv_id: str,
    service: Annotated[MatchingService, Depends(get_matching_service)],
    user: Annotated[User, Depends(get_current_user)],
    limit: int = 10,
) -> dict[str, Any]:
    """Return ranked job recommendations for the given CV."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GET /jobs/recommendations/{cv_id} is not implemented yet.",
    )
