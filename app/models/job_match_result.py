"""Job match result model: stores AI evaluation scores between a CV and a Job Listing."""

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MatchStatus(str, enum.Enum):
    """Possible statuses for a job match."""

    RECOMMENDED = "recommended"
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"


class JobMatchResult(Base):
    """Result of matching a CV against a Job Description.

    Can also be used to track user's saved or applied jobs.
    """

    __tablename__ = "job_match_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    cv_id: Mapped[str] = mapped_column(String(36), ForeignKey("cv_records.id"), nullable=False)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_listings.id"), nullable=False)

    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    matching_rationale: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[MatchStatus] = mapped_column(
        Enum(MatchStatus), default=MatchStatus.RECOMMENDED, nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="job_matches")
    cv_record = relationship("CVRecord", back_populates="job_matches")
    job_listing = relationship("JobListing", back_populates="job_matches")
