"""FastAPI dependency providers (DI wiring).

The application uses the Controller-Service-Repository pattern. Routers depend
on services; services depend on connectors + repositories. Connectors are
lazy-singletons (``lru_cache``) so heavy resources (LLM client, ASR model)
are reused across requests.

Wiring:
    Each provider returns instances whose methods raise
    ``NotImplementedError`` until backends are connected. The DI graph stays
    stable; extend implementations, not the dependency shape.

TODO:
    - Replace ``get_current_user`` demo behaviour with real JWT validation.
    - Add organization scoping helpers once shared-organization data is enabled.
"""

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.llm_connector import LLMConnector
from app.core.ocr_processor import OCRProcessor
from app.core.settings import Settings, get_settings
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector
from app.models.cv_record import CVRecord
from app.models.interview_session import InterviewSession
from app.models.job_listing import JobListing
from app.models.user import User
from app.repository.relational_repository import RelationalRepository
from app.repository.vector_repository import VectorRepository
from app.service.auth_service import AuthService
from app.service.extraction_service import ExtractionService
from app.service.interview_service import InterviewService
from app.service.matching_service import MatchingService
from app.service.optimization_service import OptimizationService

# ---------------------------------------------------------------------------
# Singleton connectors
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_llm_connector() -> LLMConnector:
    s = get_settings()
    return LLMConnector(
        local_base_url=s.llm_local_base_url,
        local_model=s.llm_local_model,
        cloud_base_url=s.llm_cloud_base_url,
        cloud_api_key=s.llm_cloud_api_key,
        cloud_model=s.llm_cloud_model,
    )


@lru_cache(maxsize=1)
def get_ocr_processor() -> OCRProcessor:
    return OCRProcessor()


@lru_cache(maxsize=1)
def get_stt_connector() -> VoiceSTTConnector:
    s = get_settings()
    return VoiceSTTConnector(model_id=s.stt_model_id, device=s.stt_device)


@lru_cache(maxsize=1)
def get_tts_connector() -> VoiceTTSConnector:
    s = get_settings()
    mp = Path(s.tts_model_path) if s.tts_model_path else None
    return VoiceTTSConnector(engine=s.tts_engine, model_path=mp, voice=s.tts_voice)


@lru_cache(maxsize=1)
def get_vector_repository() -> VectorRepository:
    s = get_settings()
    return VectorRepository(
        host=s.vector_db_host, 
        port=s.vector_db_port, 
        collection_name=s.vector_db_collection,
        api_key=s.vector_db_api_key
    )


# ---------------------------------------------------------------------------
# Repositories (per ORM model)
# ---------------------------------------------------------------------------


@lru_cache(maxsize=1)
def get_user_repository() -> RelationalRepository[User]:
    return RelationalRepository(User)


@lru_cache(maxsize=1)
def get_cv_repository() -> RelationalRepository[CVRecord]:
    return RelationalRepository(CVRecord)


@lru_cache(maxsize=1)
def get_job_repository() -> RelationalRepository[JobListing]:
    return RelationalRepository(JobListing)


@lru_cache(maxsize=1)
def get_interview_session_repository() -> RelationalRepository[InterviewSession]:
    return RelationalRepository(InterviewSession)


# ---------------------------------------------------------------------------
# Services (request-scoped — receive injected dependencies)
# ---------------------------------------------------------------------------


def get_auth_service(
    user_repo: Annotated[RelationalRepository[User], Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(user_repository=user_repo, settings=settings)


def get_extraction_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    ocr: Annotated[OCRProcessor, Depends(get_ocr_processor)],
    vector_repo: Annotated[VectorRepository, Depends(get_vector_repository)],
    cv_repo: Annotated[RelationalRepository[CVRecord], Depends(get_cv_repository)],
) -> ExtractionService:
    return ExtractionService(
        ocr_processor=ocr,
        llm_connector=llm,
        vector_repository=vector_repo,
        cv_repository=cv_repo,
    )


def get_optimization_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    vector_repo: Annotated[VectorRepository, Depends(get_vector_repository)],
    cv_repo: Annotated[RelationalRepository[CVRecord], Depends(get_cv_repository)],
) -> OptimizationService:
    return OptimizationService(
        llm_connector=llm,
        vector_repository=vector_repo,
        cv_repository=cv_repo,
    )


def get_matching_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    vector_repo: Annotated[VectorRepository, Depends(get_vector_repository)],
    job_repo: Annotated[RelationalRepository[JobListing], Depends(get_job_repository)],
) -> MatchingService:
    return MatchingService(
        llm_connector=llm,
        vector_repository=vector_repo,
        job_repository=job_repo,
    )


def get_interview_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    stt: Annotated[VoiceSTTConnector, Depends(get_stt_connector)],
    tts: Annotated[VoiceTTSConnector, Depends(get_tts_connector)],
    session_repo: Annotated[RelationalRepository[InterviewSession], Depends(get_interview_session_repository)],
) -> InterviewService:
    return InterviewService(
        llm_connector=llm,
        stt_connector=stt,
        tts_connector=tts,
        session_repository=session_repo,
    )


# ---------------------------------------------------------------------------
# Auth dependency
# ---------------------------------------------------------------------------


async def get_current_user(
    db: Annotated[AsyncSession, Depends(get_db_session)],
    auth: Annotated[AuthService, Depends(get_auth_service)],
    authorization: Annotated[str | None, Header()] = None,
) -> User:
    """Resolve the calling user from the ``Authorization: Bearer <jwt>`` header.

    Behaviour:
        - If ``Authorization`` is missing, respond with 401 to match the API contract.
        - Token resolution is delegated to ``AuthService.resolve_token``.

    TODO:
        - Replace with real JWT decode + DB lookup.
        - Add organization scoping (downstream queries should filter by
          ``user.tenant_id`` where organization data is shared).
    """
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        return await auth.resolve_token(db, token)
    except NotImplementedError as exc:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="JWT authentication is not implemented yet.",
        ) from exc
