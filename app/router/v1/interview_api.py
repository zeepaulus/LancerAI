"""Module 4 — Voice interview and WebSocket."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, WebSocket, status

from app.core.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/interview", tags=["interview"])


@router.get("/health")
async def interview_health() -> dict[str, Any]:
    """Lightweight ping for the interview module."""
    return {"status": "ok", "module": "interview"}


@router.post("/sessions")
async def create_interview_session(
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Create a new (REST-tracked) interview session shell."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="POST /interview/sessions is not implemented yet.",
    )


@router.get("/sessions/{session_id}/report")
async def get_interview_report(
    session_id: str,
    user: Annotated[User, Depends(get_current_user)],
) -> dict[str, Any]:
    """Fetch the final STAR-scored report for a session."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="GET /interview/sessions/{session_id}/report is not implemented yet.",
    )


@router.websocket("/ws")
async def interview_websocket(websocket: WebSocket) -> None:
    """Real-time voice interview channel.

    Protocol (target):
        Client -> bytes  : raw PCM Int16 mono @ 16kHz
        Client -> json   : ``{"type": "start_session", "cv_id": "...", ...}``
                            ``{"type": "end_session"}``
        Server -> json   : transcripts, AI text, status events
        Server -> bytes  : TTS PCM @ 24kHz mono

    TODO:
        - Authenticate the connection from a query token (``?token=...``).
        - Build ``InterviewPipeline`` per-session and dispatch start/audio/end.
        - Persist the resulting session via ``InterviewService.persist_session``.
    """
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "error",
            "message": "Interview websocket pipeline is not implemented yet.",
        }
    )
    await websocket.close(code=1011)
