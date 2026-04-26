"""Schema layer: Pydantic models for request/response validation."""

from app.schema.request import (
    AuthLoginRequest,
    AuthSignupRequest,
    CVUploadRequest,
    InterviewSessionRequest,
    JobMatchRequest,
    OptimizationRequest,
)
from app.schema.response import (
    CVExtractionResponse,
    InterviewReportResponse,
    JobMatchResponse,
)

__all__ = [
    "AuthLoginRequest",
    "AuthSignupRequest",
    "CVUploadRequest",
    "OptimizationRequest",
    "JobMatchRequest",
    "InterviewSessionRequest",
    "CVExtractionResponse",
    "JobMatchResponse",
    "InterviewReportResponse",
]
