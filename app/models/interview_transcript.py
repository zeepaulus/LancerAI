"""Interview transcript model: stores turn-by-turn conversation history."""

import enum
import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MessageRole(str, enum.Enum):  # noqa: UP042
    """Speaker role in an interview conversation turn."""

    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system"  # system warnings, e.g. inappropriate content detection


class InterviewTranscript(Base):
    """A single message / turn in a voice interview session.

    Ordered by ``created_at`` — use ``InterviewSession.transcripts`` relationship
    (ordered, cascade delete-orphan) to iterate the full conversation.
    """

    __tablename__ = "interview_transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(String(36), ForeignKey("interview_sessions.id"), nullable=False, index=True)
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    turn_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    star_score: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    stt_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    session = relationship("InterviewSession", back_populates="transcripts")
