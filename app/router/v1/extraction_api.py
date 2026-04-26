"""Module 1 — CV extraction.

Owns:
    POST /extraction/upload     -> upload a CV file (PDF/image), persist record
    GET  /extraction/cv/{cv_id} -> fetch a previously persisted record

TODO:
    - Wire the upload handler to ``ExtractionService.extract_from_pdf`` /
      ``extract_from_image`` and persist the result.
    - Enforce per-tenant scoping (only return CVs owned by the calling user).
"""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.dependencies import get_current_user, get_cv_repository, get_extraction_service
from app.models.cv_record import CVRecord
from app.models.user import User
from app.repository.relational_repository import RelationalRepository
from app.service.extraction_service import ExtractionService

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.post("/upload")
async def upload_cv(
    file: Annotated[UploadFile, File(...)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Upload and parse a CV file."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="POST /extraction/upload is not implemented yet.",
    )


@router.get("/cv/{cv_id}")
async def get_cv(
    cv_id: str,
    db: Annotated[AsyncSession, Depends(get_db_session)],
    cv_repo: Annotated[RelationalRepository[CVRecord], Depends(get_cv_repository)],
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Return a persisted CV record."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GET /extraction/cv/{cv_id} is not implemented yet.",
    )
