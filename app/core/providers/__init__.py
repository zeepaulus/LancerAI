"""Re-exports all providers for backward-compatible imports from app.core.providers."""

from app.core.providers.auth import get_current_user
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
    get_job_repository,
    get_user_repository,
)
from app.core.providers.services import (
    get_auth_service,
    get_extraction_service,
    get_interview_service,
    get_matching_service,
    get_optimization_service,
    get_template_renderer,
)

__all__ = [
    "get_current_user",
    "get_graph_repository",
    "get_llm_connector",
    "get_ocr_processor",
    "get_stt_connector",
    "get_tts_connector",
    "get_vector_repository",
    "get_cv_repository",
    "get_interview_session_repository",
    "get_job_repository",
    "get_user_repository",
    "get_auth_service",
    "get_extraction_service",
    "get_interview_service",
    "get_matching_service",
    "get_optimization_service",
    "get_template_renderer",
]
