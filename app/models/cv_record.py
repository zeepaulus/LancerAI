"""CV record model: stores extracted and optimized CV data."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class CVRecord(Base):
    """A single CV extraction and optimization record.

    Each CV belongs to a specific user (data isolation).
    """

    __tablename__ = "cv_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    language: Mapped[str] = mapped_column(String(5), default="vi")
    extracted_data: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    optimized_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    audit_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    optimization_mode: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), server_default="extracted", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner = relationship("User", back_populates="cv_records", lazy="noload")
    interview_sessions = relationship("InterviewSession", back_populates="cv_record", lazy="noload")
    job_matches = relationship("JobMatchResult", back_populates="cv_record", lazy="noload")
