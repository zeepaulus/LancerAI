"""Job match result model: AI evaluation scores between a CV and a Job Listing."""

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MatchStatus(str, enum.Enum):  # noqa: UP042
    """Lifecycle status of a job match result."""

    RECOMMENDED = "recommended"
    SAVED = "saved"
    APPLIED = "applied"
    REJECTED = "rejected"


class JobMatchResult(Base):
    """Result of matching a CV against a Job Description.

    Also tracks the user's workflow: recommended → saved → applied / rejected.
    """

    __tablename__ = "job_match_results"
    __table_args__ = (
        CheckConstraint("match_score >= 0.0 AND match_score <= 1.0", name="ck_job_match_results_score_range"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    cv_id: Mapped[str] = mapped_column(String(36), ForeignKey("cv_records.id"), nullable=False, index=True)
    job_id: Mapped[str] = mapped_column(String(36), ForeignKey("job_listings.id"), nullable=False, index=True)

    match_score: Mapped[float] = mapped_column(Float, default=0.0)
    matching_rationale: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    missing_skills: Mapped[list[str]] = mapped_column(JSON, default=list)
    status: Mapped[MatchStatus] = mapped_column(Enum(MatchStatus), default=MatchStatus.RECOMMENDED, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    owner = relationship("User", back_populates="job_matches", lazy="noload")
    cv_record = relationship("CVRecord", back_populates="job_matches", lazy="noload")
    job_listing = relationship("JobListing", back_populates="job_matches", lazy="noload")
