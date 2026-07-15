"""Module 3 — Job matching."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_extraction_service, get_matching_service
from app.core.rate_limit import limiter
from app.models.job_listing import JobListing
from app.models.user import User
from app.schema.request import JobMatchRequest
from app.schema.response import JobListingResponse, JobMatchResponse, JobRecommendationResponse
from app.service.extraction.service import ExtractionService
from app.service.matching.service import MatchingService

router = APIRouter(prefix="/jobs", tags=["job-matching"])


def _job_listing_response(job: JobListing) -> JobListingResponse:
    requirements = job.requirements or {}
    skills = requirements.get("skills") or requirements.get("tags") or []
    return JobListingResponse(
        job_id=job.id,
        title=job.title,
        company=job.company or "",
        location=job.location or "",
        salary_range=job.salary_range or "",
        source=job.source or "",
        source_url=job.source_url or "",
        description=(job.description or "")[:4000],
        requirements=requirements,
        skills=skills,
        experience_level=job.experience_level,
        job_type=job.job_type,
        crawled_at=job.crawled_at.isoformat() if job.crawled_at else "",
        updated_at=job.updated_at.isoformat() if job.updated_at else "",
    )


@router.get("/listings")
@limiter.limit("30/minute")
async def list_job_listings(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    source: str | None = None,
    q: str | None = None,
    location: str | None = None,
    level: str | None = None,
    limit: int = 50,
) -> list[JobListingResponse]:
    """Return active crawled job listings for frontend job matching."""
    safe_limit = max(1, min(limit, 100))
    stmt = select(JobListing).where(JobListing.is_active.is_(True))
    if source:
        stmt = stmt.where(JobListing.source == source)
    if location:
        stmt = stmt.where(JobListing.location.ilike(f"%{location}%"))
    if level:
        stmt = stmt.where(JobListing.experience_level.ilike(f"%{level}%"))
    if q:
        pattern = f"%{q}%"
        stmt = stmt.where(
            or_(
                JobListing.title.ilike(pattern),
                JobListing.company.ilike(pattern),
                JobListing.description.ilike(pattern),
            )
        )
    stmt = stmt.order_by(JobListing.updated_at.desc().nullslast(), JobListing.crawled_at.desc()).limit(safe_limit)
    result = await db.execute(stmt)
    return [_job_listing_response(job) for job in result.scalars().all()]


@router.get("/listings/{job_id}")
@limiter.limit("60/minute")
async def get_job_listing(
    request: Request,
    job_id: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> JobListingResponse:
    """Return one active crawled job listing."""
    result = await db.execute(select(JobListing).where(JobListing.id == job_id, JobListing.is_active.is_(True)))
    job = result.scalars().first()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job listing not found.")
    return _job_listing_response(job)


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
        await service.save_match_result(db, user_id=user.id, cv_id=body.cv_id, result=result)
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
