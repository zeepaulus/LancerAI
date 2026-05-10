"""Interview transcript model: stores turn-by-turn conversational history."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MessageRole(str, enum.Enum):
    """Roles in an interview conversation."""

    AI = "ai"
    HUMAN = "human"
    SYSTEM = "system" # system warning for inappropriate content


class InterviewTranscript(Base):
    """A single message/turn in an interview session."""

    __tablename__ = "interview_transcripts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("interview_sessions.id"), nullable=False, index=True
    )

    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Optional URL to the S3 bucket or local storage if raw audio is saved
    audio_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    interview_sessions = relationship("InterviewSession", back_populates="transcripts")
