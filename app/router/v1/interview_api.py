"""Module 4 — Voice interview and WebSocket."""

import contextlib
import logging
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
from app.schema.response import InterviewReportResponse, InterviewSessionResponse
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
    """Create a new interview session shell."""
    cv = await extraction.get_cv(db, payload.cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )
    try:
        session_id = await service.create_session(
            session=db,
            cv_id=payload.cv_id,
            user_id=user.id,
            mode=payload.mode,
            job_listing_id=getattr(payload, "job_listing_id", None),
            duration_minutes=getattr(payload, "duration_minutes", 5),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {exc}",
        ) from exc

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
    """Fetch the final STAR-scored report for a session."""
    # Ownership check
    from sqlalchemy import select

    from app.models.interview_session import InterviewSession

    stmt = select(InterviewSession).where(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user.id,
    )
    result = await db.execute(stmt)
    if result.scalars().first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Interview session not found or access denied.",
        )
    try:
        return await service.get_report(session=db, session_id=session_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve report: {exc}",
        ) from exc


@router.websocket("/ws")
async def interview_websocket(
    websocket: WebSocket,
    pipeline_factory: Annotated[Callable[..., Any], Depends(get_interview_pipeline_factory)],
) -> None:
    """Real-time voice interview channel.

    Frame protocol:
      - First message (JSON): ``{"token": "<jwt>", "cv_id": "...", "job_title": "...",
                                 "mode": "practice|mock|quick", "duration_minutes": 5}``
      - Subsequent binary frames: raw PCM Int16 mono 16 kHz audio chunks.
      - Server sends JSON events and binary PCM TTS audio.
    """
    await websocket.accept()
    _pipeline = None

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

    # Wrap send functions to handle disconnects gracefully without raising RuntimeError
    async def safe_send_json(data: dict[str, Any]) -> None:
        try:
            await websocket.send_json(data)
        except Exception as e:
            _logger.debug("WS send_json failed (client disconnected): %s", e)

    async def safe_send_bytes(data: bytes) -> None:
        try:
            await websocket.send_bytes(data)
        except Exception as e:
            _logger.debug("WS send_bytes failed (client disconnected): %s", e)

    # Initialize pipeline
    _pipeline = pipeline_factory(safe_send_json, safe_send_bytes, user_id=user_id)

    # Start the interview session
    cv_data: dict[str, Any] = auth_data.get("cv_data") or {}
    jd_data: dict[str, Any] | None = auth_data.get("jd_data")
    job_title: str = auth_data.get("job_title", "Software Engineer")
    mode: str = auth_data.get("mode", "practice")
    duration_minutes: int = int(auth_data.get("duration_minutes", 5))

    try:
        await _pipeline.start(
            job_title=job_title,
            cv_data=cv_data,
            jd_data=jd_data,
            mode=mode,
            duration_minutes=duration_minutes,
        )
    except Exception as exc:
        _logger.error("WS /interview/ws: pipeline.start failed — %s", exc)
        await websocket.close(code=1011)
        return

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data:
                await _pipeline.feed_audio(data["bytes"])
            elif "text" in data:
                try:
                    msg = __import__("json").loads(data["text"])
                    if msg.get("action") == "stop":
                        break
                except Exception:
                    pass
    except WebSocketDisconnect:
        _logger.info("WebSocket disconnected (user=%s)", user_id)
    except Exception as exc:
        _logger.error("WebSocket error: %s", exc)
        with contextlib.suppress(Exception):
            await websocket.close(code=1000)
    finally:
        if _pipeline is not None:
            with contextlib.suppress(Exception):
                await _pipeline.stop()
