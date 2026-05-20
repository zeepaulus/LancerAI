"""Module 1 — CV extraction.

Owns:
    POST /extraction/cvs       -> upload a CV file (PDF/image), persist record
    GET  /extraction/cv/{cv_id} -> fetch a previously persisted record

MVP MOCK:
    Endpoints return deterministic fake data matching the response schema.
    Replace with PyMuPDF/OCR + LLM parsing when implementing for real.
"""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.services import get_extraction_service
from app.core.rate_limit import limiter
from app.models.cv_record import CVRecord
from app.models.user import User
from app.schema.response import CVExtractionResponse
from app.service.extraction.service import MAX_FILE_SIZE, ExtractionService

router = APIRouter(prefix="/extraction", tags=["extraction"])

# ---------------------------------------------------------------------------
# MVP mock data factory — deterministic, schema-compliant
# ---------------------------------------------------------------------------

_MOCK_EXTRACTED_DATA: dict[str, Any] = {
    "personal_info": {
        "name": "Nguyễn Văn A",
        "email": "nguyenvana@email.com",
        "phone": "0901234567",
        "linkedin": "linkedin.com/in/nguyenvana",
        "location": "Ho Chi Minh City",
    },
    "education": [
        {
            "school": "HCMC University of Technology",
            "degree": "Bachelor",
            "major": "Computer Science",
            "gpa": "3.5",
            "period": "2018 - 2022",
        }
    ],
    "experience": [
        {
            "company": "TechCorp Vietnam",
            "title": "Backend Engineer",
            "period": "2022 - Present",
            "descriptions": [
                "Designed RESTful APIs serving 10k RPM.",
                "Migrated monolith to microservices.",
            ],
            "key_impacts": ["Reduced latency by 40%"],
            "tech_stack": ["Python", "FastAPI", "PostgreSQL"],
        }
    ],
    "projects": [
        {
            "name": "CV Optimizer",
            "role": "Lead Developer",
            "tech_stack": ["LangGraph", "Qdrant"],
            "description": "Multi-agent CV analysis pipeline.",
            "key_impacts": ["Processed 500+ CVs"],
            "potential_roast_points": ["No metrics on improvement"],
        }
    ],
    "skills_matrix": {
        "languages": ["Python", "TypeScript"],
        "frameworks": ["FastAPI", "React"],
        "tools": ["Docker", "Git", "PostgreSQL"],
        "soft_skills": ["Communication", "Leadership"],
    },
    "certifications": ["AWS Solutions Architect Associate"],
    "languages": ["Vietnamese", "English"],
}


def _build_extraction_response(cv_id: str) -> CVExtractionResponse:
    """Build a CVExtractionResponse from mock data."""
    return CVExtractionResponse(cv_id=cv_id, **_MOCK_EXTRACTED_DATA)


@router.post("/cvs", status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_cv(
    request: Request,
    file: Annotated[UploadFile, File(...)],
    service: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    user: Annotated[User, Depends(get_current_user)],
    mock: bool = True,
) -> CVExtractionResponse:
    """Upload and parse a CV file.

    If mock=True (default for MVP), persists a CVRecord with fake extracted_data.
    If mock=False, calls the real OCR+LLM pipeline.
    """
    allowed_types = {"application/pdf", "image/png", "image/jpeg", "image/webp"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type '{file.content_type}'. Allowed: {sorted(allowed_types)}.",
        )

    # Drain upload with size check and store bytes
    chunk_size = 64 * 1024
    file_bytes = bytearray()
    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        file_bytes.extend(chunk)
        if len(file_bytes) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File exceeds the {MAX_FILE_SIZE:,}-byte (10 MB) limit.",
            )

    if mock:
        # MVP MOCK: persist record with fake data
        cv_id = str(uuid.uuid4())
        record = CVRecord(
            id=cv_id,
            user_id=user.id,
            filename=file.filename or "unknown.pdf",
            language="vi",
            extracted_data=_MOCK_EXTRACTED_DATA,
        )
        db.add(record)
        await db.flush()
        return _build_extraction_response(cv_id)

    # Real Extraction Pipeline
    filename = file.filename or "unknown"
    try:
        if file.content_type == "application/pdf":
            return await service.extract_from_pdf(
                file_bytes=bytes(file_bytes),
                filename=filename,
                user_id=user.id,
                session=db,
            )
        else:
            return await service.extract_from_image(
                file_bytes=bytes(file_bytes),
                filename=filename,
                user_id=user.id,
                session=db,
            )
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Not implemented: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Extraction failed: {str(e)}",
        )


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
