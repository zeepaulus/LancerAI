"""Module 4 — Interview service.

REST-side companion to the realtime websocket pipeline. Owns:
    - persisting completed interview sessions (transcripts + STAR scores)
    - fetching interview reports for the dashboard

The realtime conversation logic lives in ``app/service/interview/pipeline.py``.

TODO:
    - ``persist_session``: turn a finished ``InterviewState`` into rows on
      ``interview_sessions``.
    - ``get_report``: assemble the response shape used by the frontend
      analytics view.
    - Tenant scoping: read/write only sessions where ``user_id`` belongs to
      the calling tenant.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector
from app.models.interview_session import InterviewSession
from app.repository.relational_repository import RelationalRepository


class InterviewService:
    """REST companion for interview session lifecycle."""

    def __init__(
        self,
        llm_connector: LLMConnector,
        stt_connector: VoiceSTTConnector,
        tts_connector: VoiceTTSConnector,
        session_repository: RelationalRepository[InterviewSession],
    ) -> None:
        self._llm = llm_connector
        self._stt = stt_connector
        self._tts = tts_connector
        self._sessions = session_repository

    async def persist_session(self, payload: dict[str, Any]) -> str:
        """Persist a finished interview session and return its id."""
        raise NotImplementedError("InterviewService.persist_session is not implemented yet.")

    async def get_report(self, session_id: str) -> dict[str, Any]:
        """Return the full interview report for the dashboard view."""
        raise NotImplementedError("InterviewService.get_report is not implemented yet.")
