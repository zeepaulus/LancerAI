"""Job listing model: stores crawled JD data."""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JobListing(Base):
    """A crawled job listing from external job boards.

    Admin-managed: `created_by` tracks which admin imported the data.
    """

    __tablename__ = "job_listings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    source: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[str] = mapped_column(String(500), nullable=False)
    title: Mapped[str] = mapped_column(String(300), nullable=False)
    company: Mapped[str] = mapped_column(String(200), default="")
    location: Mapped[str] = mapped_column(String(200), default="")
    description: Mapped[str] = mapped_column(Text, default="")
    requirements: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    salary_range: Mapped[str] = mapped_column(String(100), default="")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True)
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
