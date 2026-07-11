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
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_connector import LLMConnector
from app.models.interview_session import InterviewSession
from app.models.interview_transcript import InterviewTranscript, MessageRole
from app.repository.relational_repository import RelationalRepository
from app.schema.response import InterviewReportResponse, InterviewTranscriptResponse, STARScore
from app.service.interview.scoring import score_to_confidence

logger = logging.getLogger(__name__)


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

    @staticmethod
    def room_name_for(session_id: str) -> str:
        """Return the stable realtime room name for an interview session."""
        return f"interview-{session_id}"

    @staticmethod
    def meeting_url_for(session_id: str, frontend_base_url: str) -> str:
        """Return the candidate-facing meeting URL for the existing SPA."""
        base_url = frontend_base_url.rstrip("/")
        return f"{base_url}/chat?session_id={session_id}"

    async def create_session(
        self,
        session: AsyncSession,
        cv_id: str,
        user_id: str,
        mode: str,
        job_listing_id: str | None = None,
        focus_area: str | None = None,
        duration_minutes: int = 5,
        job_title: str = "",
        jd_data: dict[str, Any] | None = None,
        interview_plan: dict[str, Any] | None = None,
    ) -> str:
        """Create a session shell record (status: created) and return its id.

        Called by POST /interview/sessions before the WebSocket is opened.

        Steps:
          1. Create a new InterviewSession row with initial zero metrics.
          2. Flush to DB (generates UUID).
          3. Return the generated session_id.
        """
        record = await self._sessions.create(
            session,
            user_id=user_id,
            cv_id=cv_id,
            job_listing_id=job_listing_id,
            mode=mode,
            total_questions=0,
            overall_confidence=0.0,
            star_scores={
                "status": "created",
                "setup": {
                    "job_title": job_title,
                    "duration_minutes": duration_minutes,
                    "focus_area": focus_area or "",
                    "jd_data": jd_data or {},
                },
                "title": job_title or "Phỏng vấn AI",
                "focus_area": focus_area or "",
                "interview_plan": interview_plan or {},
            },
            logic_issues=[],
            improvement_suggestions=[],
        )
        await session.commit()

        # Persist new columns (additive — does not affect existing logic)
        from app.core.settings import get_settings as _get_settings

        _s = _get_settings()
        _jd_snapshot = (jd_data or {}).get("jd_text") or None
        await self._sessions.update(
            session,
            record.id,
            status="in_progress",
            jd_snapshot=_jd_snapshot,
            tts_voice=_s.tts_voice,
            llm_model=_s.llm_cloud_model,
        )
        await session.commit()

        logger.info(
            "[InterviewService] Created session %s for user=%s cv=%s mode=%s",
            record.id,
            user_id,
            cv_id,
            mode,
        )
        return str(record.id)

    async def persist_session(
        self,
        session: AsyncSession,
        payload: dict[str, Any],
    ) -> str:
        """Persist a finished interview session and return its id.

        Called by the WebSocket handler after ``InterviewPipeline.stop()``
        returns the final STAR evaluation payload.

        Steps:
          1. Retrieve the existing InterviewSession by session_id.
          2. Update STAR metrics and mark completed_at.
          3. Bulk insert InterviewTranscript rows.
          4. Return the session_id.
        """
        session_id: str = payload.get("session_id", "")
        if not session_id:
            raise ValueError("payload must contain 'session_id'")

        record = await self._sessions.get_by_id(session, session_id)
        if record is None:
            raise ValueError(f"InterviewSession '{session_id}' not found")

        # Map STAR scores from pipeline payload
        star_scores_raw: list[dict[str, Any]] = [
            s if isinstance(s, dict) else s.model_dump() for s in payload.get("star_scores", [])
        ]
        scorecard: dict[str, Any] = payload.get("scorecard", {})
        scorecard_overall = float(scorecard.get("overall_score", 0.0))
        if scorecard_overall:
            overall_confidence = score_to_confidence(scorecard_overall)
        else:
            overall_score: float = float(payload.get("overall_score", 0.0))
            overall_confidence = min(100.0, overall_score * 10)

        improvements: list[str] = payload.get("improvements", [])
        behavior_observations: list[dict[str, Any]] = payload.get("behavior_observations", [])
        behavior_issues: list[str] = payload.get("behavior_issues", [])
        behavior_score = float(payload.get("behavior_score", 100.0))
        existing_scores = record.star_scores or {}

        await self._sessions.update(
            session,
            session_id,
            total_questions=len(star_scores_raw),
            overall_confidence=overall_confidence,
            star_scores={
                **existing_scores,
                "status": "completed",
                "scores": star_scores_raw,
                "final_feedback": payload.get("final_feedback", ""),
                "behavior_score": behavior_score,
                "behavior_observations": behavior_observations,
                "scorecard": scorecard,
                "title": existing_scores.get("title") or payload.get("job_title") or "Phỏng vấn AI",
                "focus_area": existing_scores.get("focus_area") or "",
            },
            logic_issues=behavior_issues,
            improvement_suggestions=improvements,  # strengths stored separately in scorecard JSON
            completed_at=datetime.now(UTC),
        )

        # Mark session as completed (additive — does not affect existing logic)
        await self._sessions.update(session, session_id, status="completed")

        # Bulk insert transcript turns
        transcript_turns: list[dict[str, Any]] = payload.get("transcript", [])
        for _turn_idx, turn in enumerate(transcript_turns, start=1):
            role_str: str = turn.get("role", "")
            content: str = turn.get("content", "")
            if not content:
                continue

            # Map pipeline roles to MessageRole enum
            if role_str == "interviewer":
                db_role = MessageRole.AI
            elif role_str == "candidate":
                db_role = MessageRole.HUMAN
            else:
                db_role = MessageRole.SYSTEM

            transcript_record = InterviewTranscript(
                session_id=session_id,
                role=db_role,
                content=content,
                turn_number=_turn_idx,
            )
            session.add(transcript_record)

        await session.commit()
        logger.info(
            "[InterviewService] Persisted session %s — %d turns, score=%.1f",
            session_id,
            len(transcript_turns),
            overall_confidence,
        )
        return session_id

    async def get_report(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> InterviewReportResponse:
        """Return the full interview report for the dashboard view.

        Steps:
          1. Query the InterviewSession by session_id.
          2. Validate existence.
          3. Build InterviewReportResponse from ORM data.
        """
        record = await self._sessions.get_by_id(session, session_id)
        if record is None:
            raise ValueError(f"InterviewSession '{session_id}' not found")

        # Parse STAR scores from stored JSON
        star_scores_list: list[STARScore] = []
        stored_scores = record.star_scores or {}
        for score_dict in stored_scores.get("scores", []):
            try:
                star_scores_list.append(
                    STARScore(
                        situation=float(score_dict.get("situation_score", 0)),
                        task=float(score_dict.get("task_score", 0)),
                        action=float(score_dict.get("action_score", 0)),
                        result=float(score_dict.get("result_score", 0)),
                    )
                )
            except Exception as exc:
                logger.debug("[InterviewService] Skipping malformed STAR score: %s", exc)

        transcript_rows = await session.execute(
            select(InterviewTranscript)
            .where(InterviewTranscript.session_id == session_id)
            .order_by(InterviewTranscript.created_at.asc())
        )
        transcript: list[InterviewTranscriptResponse] = []
        for row in transcript_rows.scalars().all():
            if row.role == MessageRole.AI:
                role = "interviewer"
            elif row.role == MessageRole.HUMAN:
                role = "candidate"
            else:
                role = "system"
            transcript.append(
                InterviewTranscriptResponse(
                    role=role,
                    content=row.content,
                    created_at=row.created_at.isoformat() if row.created_at else "",
                )
            )

        return InterviewReportResponse(
            session_id=session_id,
            overall_confidence=float(record.overall_confidence or 0.0),
            total_questions=int(record.total_questions or 0),
            star_scores=star_scores_list,
            logic_issues=list(record.logic_issues or []),
            improvement_suggestions=list(record.improvement_suggestions or []),
            behavior_score=float(stored_scores.get("behavior_score", 100.0)),
            behavior_observations=list(stored_scores.get("behavior_observations", [])),
            scorecard=stored_scores.get("scorecard") or {},
            interview_plan=stored_scores.get("interview_plan") or {},
            transcript=transcript,
            created_at=record.started_at.isoformat() if record.started_at else None,
            title=stored_scores.get("title") or stored_scores.get("setup", {}).get("job_title") or "Phỏng vấn AI",
            focus_area=stored_scores.get("focus_area") or stored_scores.get("setup", {}).get("focus_area") or "",
            status="incomplete" if (record.completed_at is None or record.total_questions == 0) else "completed",
        )

    async def list_sessions(
        self,
        session: AsyncSession,
        user_id: str,
    ) -> list[InterviewSession]:
        """Fetch all interview sessions belonging to the user, newest first."""
        stmt = (
            select(InterviewSession)
            .where(InterviewSession.user_id == user_id)
            .order_by(InterviewSession.started_at.desc())
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
