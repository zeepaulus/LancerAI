"""Service layer — business logic.

Routers inject services via FastAPI ``Depends`` (wiring in ``app.core.providers``).
Services take connectors and repositories by constructor injection.

Layout:
    ``auth/service.py`` — AuthService
    ``extraction/service.py`` — ExtractionService
    ``matching/service.py`` — MatchingService
    ``optimization/`` — OptimizationService + LangGraph pipeline
    ``interview/`` — InterviewService + WebSocket pipeline
"""

from app.service.auth.service import AuthService
from app.service.extraction.service import ExtractionService
from app.service.interview.service import InterviewService
from app.service.matching.service import MatchingService
from app.service.optimization.service import OptimizationService

__all__ = [
    "AuthService",
    "ExtractionService",
    "OptimizationService",
    "MatchingService",
    "InterviewService",
]
