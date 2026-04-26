"""ORM models public interface.

Import all models here so that:
1. Alembic env.py can discover them for autogenerate.
2. Other modules can use `from app.models import User` cleanly.
"""

from app.models.base import Base
from app.models.cv_record import CVRecord
from app.models.interview_session import InterviewSession
from app.models.job_listing import JobListing
from app.models.user import User

__all__ = [
    "Base",
    "User",
    "CVRecord",
    "JobListing",
    "InterviewSession",
]
