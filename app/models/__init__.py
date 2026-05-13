"""ORM models — public interface.

Import all models here so that:
1. Alembic env.py can discover them via ``Base.metadata`` for autogenerate.
2. Other modules can do ``from app.models import User`` cleanly.
"""

from app.models.base import Base
from app.models.cv_record import CVRecord
from app.models.interview_session import InterviewSession
from app.models.interview_transcript import InterviewTranscript
from app.models.job_listing import JobListing
from app.models.job_match_result import JobMatchResult, MatchStatus
from app.models.user import User, UserRole

__all__ = [
    "Base",
    "User",
    "UserRole",
    "CVRecord",
    "JobListing",
    "JobMatchResult",
    "MatchStatus",
    "InterviewSession",
    "InterviewTranscript",
]
