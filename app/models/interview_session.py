"""Interview session model: stores voice AI session data and reports."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, CheckConstraint, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from app.models.base import Base


class InterviewSession(Base):
    """A single voice interview session with evaluation results.

    Links to User, CVRecord, and optionally a JobListing so the AI
    interviewer can tailor questions to a specific job description.
    """

    __tablename__ = "interview_sessions"
    __table_args__ = (
        CheckConstraint(
            "overall_confidence >= 0 AND overall_confidence <= 100",
            name="ck_interview_sessions_confidence_range",
        ),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    cv_id: Mapped[str] = mapped_column(String(36), ForeignKey("cv_records.id"), nullable=False, index=True)
    job_listing_id: Mapped[str | None] = mapped_column(
        String(36), ForeignKey("job_listings.id"), nullable=True, index=True
    )

    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    status: Mapped[str] = mapped_column(String(20), server_default="completed", nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    star_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    logic_issues: Mapped[list[str]] = mapped_column(JSON, default=list)
    improvement_suggestions: Mapped[list[str]] = mapped_column(JSON, default=list)
    jd_snapshot: Mapped[str | None] = mapped_column(Text, nullable=True)
    tts_voice: Mapped[str | None] = mapped_column(String(100), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="interview_sessions", lazy="noload")
    cv_record = relationship("CVRecord", back_populates="interview_sessions", lazy="noload")
    job_listing = relationship("JobListing", back_populates="interview_sessions", lazy="noload")
    transcripts = relationship(
        "InterviewTranscript",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="InterviewTranscript.created_at",
        lazy="noload",
    )

    @validates("overall_confidence")
    def _clamp_overall_confidence(self, _key: str, value: float | int | str | None) -> float:
        if value is None:
            return 0.0
        try:
            x = float(value)
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(100.0, x))
