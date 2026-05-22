"""Module 1 — CV extraction.

Owns:
    POST /extraction/cvs       -> upload a CV file (PDF/image), persist record
    GET  /extraction/cv/{cv_id} -> fetch a previously persisted record
"""

from typing import Annotated

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_extraction_service
from app.core.rate_limit import limiter
from app.models.user import User
from app.schema.response import CVExtractionResponse
from app.service.extraction.service import MAX_FILE_SIZE, ExtractionService

router = APIRouter(prefix="/extraction", tags=["extraction"])


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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {exc}",
        ) from exc


@router.get("/cv/{cv_id}")
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
