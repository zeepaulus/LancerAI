"""Service providers — request-scoped, receive injected connectors and repositories."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated, Any

from fastapi import Depends

from app.core.llm_connector import LLMConnector
from app.core.ocr_processor import OCRProcessor
from app.core.providers.connectors import (
    get_graph_repository,
    get_llm_connector,
    get_ocr_processor,
    get_stt_connector,
    get_tts_connector,
    get_vector_repository,
)
from app.core.providers.repositories import (
    get_cv_repository,
    get_interview_session_repository,
    get_job_match_repository,
    get_user_repository,
)
from app.core.settings import Settings, get_settings
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector
from app.models.cv_record import CVRecord
from app.models.interview_session import InterviewSession
from app.models.job_match_result import JobMatchResult
from app.models.user import User
from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.graph_repository import GraphRepository
from app.repository.relational_repository import RelationalRepository
from app.service.auth.service import AuthService
from app.service.extraction.service import ExtractionService
from app.service.interview.service import InterviewService
from app.service.matching.service import MatchingService
from app.service.optimization.service import OptimizationService
from app.service.optimization.template_renderer import CVTemplateRenderer


def get_auth_service(
    user_repo: Annotated[RelationalRepository[User], Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> AuthService:
    return AuthService(user_repository=user_repo, settings=settings)


def get_extraction_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    ocr: Annotated[OCRProcessor, Depends(get_ocr_processor)],
    vector_repo: Annotated[BaseVectorRepository, Depends(get_vector_repository)],
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
    vector_repo: Annotated[BaseVectorRepository, Depends(get_vector_repository)],
    cv_repo: Annotated[RelationalRepository[CVRecord], Depends(get_cv_repository)],
    graph_repo: Annotated[GraphRepository, Depends(get_graph_repository)],
) -> OptimizationService:
    return OptimizationService(
        llm_connector=llm,
        vector_repository=vector_repo,
        cv_repository=cv_repo,
        graph_repository=graph_repo,
    )


def get_matching_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    vector_repo: Annotated[BaseVectorRepository, Depends(get_vector_repository)],
    job_match_repo: Annotated[RelationalRepository[JobMatchResult], Depends(get_job_match_repository)],
    graph_repo: Annotated[GraphRepository, Depends(get_graph_repository)],
) -> MatchingService:
    return MatchingService(
        llm_connector=llm,
        vector_repository=vector_repo,
        job_match_repository=job_match_repo,
        graph_repository=graph_repo,
    )


def get_interview_service(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    session_repo: Annotated[RelationalRepository[InterviewSession], Depends(get_interview_session_repository)],
) -> InterviewService:
    return InterviewService(
        llm_connector=llm,
        session_repository=session_repo,
    )


def get_template_renderer(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
) -> CVTemplateRenderer:
    return CVTemplateRenderer(llm_connector=llm)


def get_interview_pipeline_factory(
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
    stt: Annotated[VoiceSTTConnector, Depends(get_stt_connector)],
    tts: Annotated[VoiceTTSConnector, Depends(get_tts_connector)],
) -> Callable[..., Any]:
    """Return a factory that builds an InterviewPipeline for one WebSocket session."""
    from app.service.interview.pipeline import InterviewPipeline

    def _factory(
        send_json: Callable[[dict[str, Any]], Awaitable[None]],
        send_bytes: Callable[[bytes], Awaitable[None]],
        user_id: str,
    ) -> InterviewPipeline:
        return InterviewPipeline(llm=llm, stt=stt, tts=tts, send_json=send_json, send_bytes=send_bytes, user_id=user_id)

    return _factory
