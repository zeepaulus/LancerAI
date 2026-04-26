"""Service layer: pure business logic.

Each module exposes one Service class. Routers depend on services through DI
(see ``app.core.dependencies``); services depend on connectors + repositories.
"""

from app.service.auth_service import AuthService
from app.service.extraction_service import ExtractionService
from app.service.interview_service import InterviewService
from app.service.matching_service import MatchingService
from app.service.optimization_service import OptimizationService

__all__ = [
    "AuthService",
    "ExtractionService",
    "OptimizationService",
    "MatchingService",
    "InterviewService",
]
