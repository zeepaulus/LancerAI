"""Interview package: Real-time Voice AI Interview Pipeline.

Public surface:
    - InterviewService  : REST orchestrator (session lifecycle, reports).
    - InterviewPipeline : WebSocket / real-time audio pipeline.
    - State / sub-schemas : InterviewState + supporting Pydantic models.
"""

from app.service.interview.pipeline import InterviewPipeline
from app.service.interview.service import InterviewService
from app.service.interview.state import (
    ChatMessage,
    InterviewState,
    InterviewTurn,
    STARScore,
)

__all__ = [
    "InterviewService",
    "ChatMessage",
    "InterviewPipeline",
    "InterviewState",
    "InterviewTurn",
    "STARScore",
]
