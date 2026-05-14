"""Repository providers — one per ORM model."""

from __future__ import annotations

from app.core.sync_singleton import thread_safe_singleton
from app.models.cv_record import CVRecord
from app.models.interview_session import InterviewSession
from app.models.job_listing import JobListing
from app.models.user import User
from app.repository.relational_repository import RelationalRepository


def _create_user_repository() -> RelationalRepository[User]:
    return RelationalRepository(User)


def _create_cv_repository() -> RelationalRepository[CVRecord]:
    return RelationalRepository(CVRecord)


def _create_job_repository() -> RelationalRepository[JobListing]:
    return RelationalRepository(JobListing)


def _create_interview_session_repository() -> RelationalRepository[InterviewSession]:
    return RelationalRepository(InterviewSession)


get_user_repository = thread_safe_singleton(_create_user_repository)
get_cv_repository = thread_safe_singleton(_create_cv_repository)
get_job_repository = thread_safe_singleton(_create_job_repository)
get_interview_session_repository = thread_safe_singleton(_create_interview_session_repository)
