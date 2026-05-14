"""Module 4 — Voice interview and WebSocket.

MVP MOCK:
    REST endpoints (create session, get report) return deterministic fake data.
    WebSocket voice pipeline remains stub (requires STT/TTS connectors).
"""

import contextlib
import logging
import uuid
from collections.abc import Callable
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user, validate_ws_token
from app.core.providers.services import (
    get_extraction_service,
    get_interview_pipeline_factory,
    get_interview_service,
)
from app.core.rate_limit import limiter
from app.models.user import User
from app.schema.request import InterviewSessionRequest
from app.schema.response import InterviewReportResponse, InterviewSessionResponse, STARScore
from app.service.extraction.service import ExtractionService
from app.service.interview.service import InterviewService

router = APIRouter(prefix="/interview", tags=["interview"])
_logger = logging.getLogger(__name__)


@router.get("/health")
@limiter.limit("100/minute")
async def interview_health(request: Request) -> dict[str, Any]:
    """Lightweight ping for the interview module."""
    return {"status": "ok", "module": "interview"}


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def create_interview_session(
    request: Request,
    payload: InterviewSessionRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewService, Depends(get_interview_service)],
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> InterviewSessionResponse:
    """Create a new (REST-tracked) interview session shell.

    MVP MOCK: validates cv_id ownership, persists a minimal InterviewSession
    row for ownership tracking, returns deterministic session metadata.
    TODO: populate with real data when pipeline is ready.
    """
    # Ownership check
    cv = await extraction.get_cv(db, payload.cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )

    # Persist a minimal session shell so GET /report can verify ownership.
    from app.models.interview_session import InterviewSession

    session_id = str(uuid.uuid4())
    session_record = InterviewSession(
        id=session_id,
        user_id=user.id,
        cv_id=payload.cv_id,
        mode=payload.mode,
    )
    db.add(session_record)
    await db.flush()

    return InterviewSessionResponse(
        session_id=session_id,
        cv_id=payload.cv_id,
        mode=payload.mode,
        status="created",
    )


@router.get("/sessions/{session_id}/report")
@limiter.limit("100/minute")
async def get_interview_report(
    request: Request,
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewService, Depends(get_interview_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> InterviewReportResponse:
    """Fetch the final STAR-scored report for a session.

    MVP MOCK: validates session ownership, returns deterministic report.
    TODO: query real evaluation data from the persisted session.
    """
    # Ownership check: session must exist and belong to the calling user
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    stmt = select(InterviewSession).where(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    session_row = result.scalars().first()
    if session_row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found or access denied.",
        )

    return InterviewReportResponse(
        session_id=session_id,
        overall_confidence=65.0,
        total_questions=5,
        star_scores=[
            STARScore(situation=7.0, task=6.5, action=8.0, result=7.5),
            STARScore(situation=6.0, task=7.0, action=7.5, result=6.0),
        ],
        logic_issues=[
            "Answer #2 lacked specific metrics.",
            "Transition between situation and action was unclear in Q3.",
        ],
        improvement_suggestions=[
            "Quantify results with specific numbers.",
            "Use the STAR framework more explicitly.",
            "Practice answering behavioral questions under time pressure.",
        ],
    )


@router.websocket("/ws")
async def interview_websocket(
    websocket: WebSocket,
    pipeline_factory: Annotated[Callable[..., Any], Depends(get_interview_pipeline_factory)],
) -> None:
    """Real-time voice interview channel.

    TODO: implement audio processing when STT/TTS connectors are ready.
    """
    await websocket.accept()

    try:
        # Require authentication as the first message
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        payload = validate_ws_token(token)
        user_id = payload.get("sub") or payload.get("id")
        if not user_id:
            raise ValueError("Token missing user ID")
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as exc:
        _logger.warning("WS /interview/ws: auth failed — %s", exc)
        await websocket.close(code=1008)
        return
    except Exception as exc:
        _logger.warning("WS /interview/ws: invalid initial message format — %s", exc)
        await websocket.close(code=1008)
        return

    # Initialize pipeline
    _pipeline = pipeline_factory(websocket.send_json, websocket.send_bytes, user_id=user_id)

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data:
                # await pipeline.process_audio(data["bytes"])
                pass
            elif "text" in data:
                # handle json/text commands
                pass
    except WebSocketDisconnect:
        _logger.info("WebSocket disconnected")
    except Exception as exc:
        _logger.error("WebSocket error: %s", exc)
        with contextlib.suppress(Exception):
            await websocket.close(code=1000)
    finally:
        with contextlib.suppress(NotImplementedError, Exception):
            await _pipeline.stop()
