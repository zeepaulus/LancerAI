"""Module 1 — CV extraction.

Owns:
    POST /extraction/cvs       -> upload a CV file (PDF/image), persist record
    GET  /extraction/cv/{cv_id} -> fetch a previously persisted record
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_extraction_service
from app.core.rate_limit import limiter
from app.models.cv_record import CVRecord
from app.models.user import User
from app.schema.request import CVExtractionUpdateRequest
from app.schema.response import CVExtractionResponse, CVRecordSummaryResponse
from app.service.extraction.service import MAX_FILE_SIZE, ExtractionService

router = APIRouter(prefix="/extraction", tags=["extraction"])
logger = logging.getLogger(__name__)


def _cv_summary_response(cv: CVRecord) -> CVRecordSummaryResponse:
    extracted = cv.extracted_data or {}
    personal_info = extracted.get("personal_info") or {}
    skills_matrix = extracted.get("skills_matrix") or {}
    skills_count = sum(
        len(skills_matrix.get(key) or [])
        for key in ("languages", "frameworks", "tools", "soft_skills")
    )
    has_analysis = bool(cv.audit_score is not None or cv.optimized_data or cv.status == "optimized")
    return CVRecordSummaryResponse(
        cv_id=cv.id,
        filename=cv.filename,
        status=cv.status,
        candidate_name=str(personal_info.get("name") or ""),
        audit_score=cv.audit_score,
        optimization_mode=cv.optimization_mode,
        has_analysis=has_analysis,
        skills_count=skills_count,
        experience_count=len(extracted.get("experience") or []),
        created_at=cv.created_at.isoformat() if cv.created_at else "",
    )


@router.get("/cvs")
@limiter.limit("60/minute")
async def list_cvs(
    request: Request,
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    limit: int = 50,
) -> list[CVRecordSummaryResponse]:
    """Return recent CV records owned by the authenticated user."""
    cvs = await service.list_user_cvs(db, user.id, limit=limit)
    return [_cv_summary_response(cv) for cv in cvs]


@router.post("/cvs", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_cv(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> CVExtractionResponse:
    """Upload and parse a CV file (PDF or image).

    - PDF: text layer extracted by PyMuPDF; scanned pages fall back to OCR.
    - Image: PaddleOCR (vi+en) extracts text directly.
    - LLM structures the raw text into the CVExtractionResponse schema.
    - Vector embedding stored in the configured vector DB.
    """
    allowed_types = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(allowed_types)}.",
        )

    # Read full file bytes (size validated inside the service)
    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"File exceeds the {MAX_FILE_SIZE:,}-byte (10 MB) limit.",
        )

    filename = file.filename or "upload"
    try:
        if file.content_type == "application/pdf":
            return await service.extract_from_pdf(file_bytes, filename, user.id, db)
        else:
            return await service.extract_from_image(file_bytes, filename, user.id, db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_413_CONTENT_TOO_LARGE, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("CV extraction failed for user_id=%s filename=%s", user.id, filename)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not analyze this CV. Please try another file or try again later.",
        ) from exc


@router.get("/cv/{cv_id}")
@router.get("/cvs/{cv_id}", include_in_schema=False)
@limiter.limit("100/minute")
async def get_cv(
    request: Request,
    cv_id: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> CVExtractionResponse:
    """Return a persisted CV record owned by the authenticated user."""
    cv = await service.get_cv(db, cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )
    return CVExtractionResponse(cv_id=cv.id, **cv.extracted_data)


@router.put("/cvs/{cv_id}")
@limiter.limit("30/minute")
async def update_cv_extraction(
    request: Request,
    cv_id: str,
    payload: CVExtractionUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    user: Annotated[User, Depends(get_current_user)],
) -> CVExtractionResponse:
    """Update user-reviewed extracted CV data before optimization."""
    updated = await service.update_extracted_data(
        db,
        cv_id,
        user.id,
        payload.model_dump(),
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )
    return updated
