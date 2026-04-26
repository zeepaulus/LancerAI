"""User account model with organization-scoped data.

Each user belongs to an organization. Single-organization deployments can set
``tenant_id == user_id`` (or use a default organization id).

TODO:
    - Add organization / team tables when collaboration features land.
    - Move ``role`` to a dedicated permissions table for finer-grained ACL.
"""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class User(Base):
    """Registered user of the platform."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    cv_records = relationship("CVRecord", back_populates="owner", lazy="selectin")
    interview_sessions = relationship("InterviewSession", back_populates="owner", lazy="selectin")
