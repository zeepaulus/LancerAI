"""Interview session model: stores voice AI session data and reports."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class InterviewSession(Base):
    """A single voice interview session with evaluation results.

    Links directly to both user and CV for efficient querying.
    """

    __tablename__ = "interview_sessions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    cv_id: Mapped[str] = mapped_column(String(36), ForeignKey("cv_records.id"), nullable=False)
    
    # Allows the AI interviewer to tailor the questions to a specific job description
    job_listing_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("job_listings.id"), nullable=True)

    mode: Mapped[str] = mapped_column(String(20), nullable=False)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    overall_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    star_scores: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    logic_issues: Mapped[list[str]] = mapped_column(JSON, default=list)
    improvement_suggestions: Mapped[list[str]] = mapped_column(JSON, default=list)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="interview_sessions")
    cv_record = relationship("CVRecord", back_populates="interview_sessions")
    job_listing = relationship("JobListing", back_populates="interview_sessions")
    transcripts = relationship("InterviewTranscript", back_populates="interview_sessions", cascade="all, delete-orphan", order_by="InterviewTranscript.created_at")
