"""Module 4 — Interview service.

REST-side companion to the realtime websocket pipeline. Owns:
    - persisting completed interview sessions (transcripts + STAR scores)
    - fetching interview reports for the dashboard

The realtime conversation logic lives in ``app/service/interview/pipeline.py``.

NOTE:
    This service intentionally does NOT hold STT/TTS connectors.
    Audio processing belongs exclusively to ``InterviewPipeline`` (WebSocket
    layer). Here we only work with text data (transcripts, STAR scores) — we
    need the LLM solely for post-hoc evaluation/scoring of the completed
    transcript.

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
from app.models.interview_session import InterviewSession
from app.repository.relational_repository import RelationalRepository
from app.schema.response import InterviewReportResponse


class InterviewService:
    """REST companion for interview session lifecycle.

    Responsibilities:
        - Create an interview session shell (REST record before WebSocket
          starts).
        - Persist the final evaluation payload after WebSocket session ends.
        - Serve interview reports for the frontend analytics dashboard.

    Note: STT/TTS are NOT injected here. Audio connectors live only inside
    ``InterviewPipeline``, which is instantiated per WebSocket connection.
    """

    def __init__(
        self,
        llm_connector: LLMConnector,
        session_repository: RelationalRepository[InterviewSession],
    ) -> None:
        self._llm = llm_connector
        self._sessions = session_repository

    async def create_session(
        self,
        cv_id: str,
        user_id: str,
        mode: str,
        job_listing_id: str | None = None,
        focus_area: str | None = None,
        duration_minutes: int = 5,
    ) -> str:
        """Create a session shell record (status: created) and return its id.

        Called by POST /interview/sessions before the WebSocket is opened.
        TODO:
            - Validate `cv_id` exists and is owned by `user_id` by querying
              the DB.
            - Create a new `InterviewSession` model instance with `user_id`,
              `cv_id`, `mode`, `job_listing_id`, and `duration_minutes`.
            - Set initial status/metrics to zero or pending (e.g.,
              `total_questions=0`, `overall_confidence=0.0`).
            - Persist using `self._sessions.add(session)` and commit to
              generate a new `session_id`.
            - Return the generated `session_id` string.
        """
        raise NotImplementedError("InterviewService.create_session is not implemented yet.")

    async def persist_session(self, payload: dict[str, Any]) -> str:
        """Persist a finished interview session and return its id.

        Called by the WebSocket handler after ``InterviewPipeline.stop()``
        returns the final STAR evaluation payload.
        TODO:
            - Extract `session_id` from `payload`. Retrieve the corresponding
              `InterviewSession` via `self._sessions.get_by_id(session_id)`.
            - Map the STAR framework evaluations from `payload` to the
              `InterviewSession` columns (e.g., `overall_confidence`,
              `star_metrics`).
            - Mark the `completed_at` timestamp.
            - Iterate over `payload["transcript"]` and construct
              `InterviewTranscript` model instances.
            - Bulk insert the transcripts into the database.
            - Return the `session_id`.
        """
        raise NotImplementedError("InterviewService.persist_session is not implemented yet.")

    async def get_report(self, session_id: str) -> InterviewReportResponse:
        """Return the full interview report for the dashboard view.

        TODO:
            - Query the database for the `InterviewSession` by `session_id`.
              Eagerly load or separately fetch its associated
              `InterviewTranscript` rows.
            - Validate existence; raise an exception (or return None) if not
              found.
            - Transform the raw ORM records into the `InterviewReportResponse`
              Pydantic schema structure (or a corresponding dictionary).
            - Ensure sensitive fields are excluded and data types match the API
              contract.
        """
        raise NotImplementedError("InterviewService.get_report is not implemented yet.")
