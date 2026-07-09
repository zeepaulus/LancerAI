"""Module 4 â€” Voice interview and WebSocket."""

import contextlib
import inspect
import json
import logging
from collections.abc import Callable
from typing import Annotated, Any

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user, validate_ws_token
from app.core.llm_connector import LLMConnector
from app.core.providers.services import (
    get_extraction_service,
    get_interview_pipeline_factory,
    get_interview_service,
    get_llm_connector,
)
from app.core.rate_limit import limiter
from app.core.settings import Settings, get_settings
from app.models.interview_session import InterviewSession
from app.models.job_listing import JobListing
from app.models.user import User
from app.schema.request import InterviewSessionRequest
from app.schema.response import InterviewReportResponse, InterviewSessionResponse, STARScore
from app.service.extraction.service import ExtractionService
from app.service.interview.planning import (
    build_interview_plan,
    build_manual_jd_data,
    infer_job_title,
    job_listing_to_jd_data,
    normalise_it_role,
)
from app.service.interview.service import InterviewService

router = APIRouter(prefix="/interview", tags=["interview"])
_logger = logging.getLogger(__name__)


def _supported_kwargs(func: Callable[..., Any], kwargs: dict[str, Any]) -> dict[str, Any]:
    """Return kwargs accepted by func, keeping compatibility with older services."""
    signature = inspect.signature(func)
    parameters = signature.parameters
    if any(parameter.kind == inspect.Parameter.VAR_KEYWORD for parameter in parameters.values()):
        return kwargs
    return {key: value for key, value in kwargs.items() if key in parameters}


_JD_SCRAPE_SYSTEM = """Bạn là một trợ lý AI chuyên nghiệp phân tích tin tuyển dụng (Job Description).
Hãy phân tích nội dung văn bản thô (raw text/markdown) được cào từ trang tin tuyển dụng và trả về kết quả dưới dạng JSON có cấu trúc như sau:
{
    "job_title": "Tên vị trí công việc (ví dụ: Kỹ sư Backend Python, Frontend React Developer)",
    "company": "Tên công ty tuyển dụng (nếu có)",
    "jd_text": "Mô tả công việc chi tiết và yêu cầu tuyển dụng được rút gọn và định dạng lại sạch sẽ bằng Markdown tiếng Việt",
    "focus_area": "Mảng tập trung chính (ví dụ: React, Python, Django, AWS, QA/QC, Business Analyst)"
}
Lưu ý: Chỉ trả về duy nhất khối JSON hợp lệ, không kèm bất kỳ lời giải thích hay tag markdown ```json."""


@router.get("/health")
@limiter.limit("100/minute")
async def interview_health(request: Request) -> dict[str, Any]:
    """Lightweight ping for the interview module."""
    return {"status": "ok", "module": "interview"}


@router.get("/scrape-jd")
@limiter.limit("20/minute")
async def scrape_job_description(
    request: Request,
    url: str,
    user: Annotated[User, Depends(get_current_user)],
    llm: Annotated[LLMConnector, Depends(get_llm_connector)],
) -> dict[str, Any]:
    """Crawl a job description page and structure the output using LLM."""
    if not url.strip():
        raise HTTPException(status_code=400, detail="Vui lòng cung cấp link URL tuyển dụng.")

    url = url.strip()
    from app.service.matching.service import _fetch_jd_from_url
    raw_text = await _fetch_jd_from_url(url)

    if not raw_text or len(raw_text.strip()) < 50:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Không thể cào dữ liệu từ URL này. Vui lòng kiểm tra lại link hoặc copy-paste thủ công."
        )

    # Ask LLM to clean and structure it
    prompt = [
        {"role": "system", "content": _JD_SCRAPE_SYSTEM},
        {"role": "user", "content": f"URL tuyển dụng: {url}\n\nNội dung thô:\n{raw_text[:6000]}"}
    ]

    try:
        from app.core.json_extractor import clean_and_parse_json

        response = await llm.generate_chat(prompt, use_cloud=llm.has_cloud)
        structured_data = clean_and_parse_json(response)
        return structured_data
    except Exception as exc:
        _logger.error("Failed to parse JD via LLM: %s", exc)
        # Fallback to returning raw text in standard schema
        return {
            "job_title": "",
            "company": "",
            "jd_text": raw_text[:4000],
            "focus_area": ""
        }


@router.post("/sessions", status_code=status.HTTP_201_CREATED)
@limiter.limit("100/minute")
async def create_interview_session(
    request: Request,
    payload: InterviewSessionRequest,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewService, Depends(get_interview_service)],
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> InterviewSessionResponse:
    """Create a new interview session shell."""
    cv = await extraction.get_cv(db, payload.cv_id, user.id)
    if cv is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="CV not found or access denied.",
        )

    cv_data: dict[str, Any] = cv.optimized_data or cv.extracted_data or {}
    jd_url = (payload.jd_url or "").strip()
    jd_text = (payload.jd_text or "").strip()
    if jd_url and not jd_text:
        from app.service.matching.service import _fetch_jd_from_url
        jd_text = await _fetch_jd_from_url(jd_url)

    jd_data = build_manual_jd_data(
        job_title=payload.job_title,
        jd_text=jd_text,
        jd_url=jd_url,
    )
    if payload.job_listing_id:
        job_result = await db.execute(
            select(JobListing).where(
                JobListing.id == payload.job_listing_id,
                JobListing.is_active.is_(True),
            )
        )
        job = job_result.scalars().first()
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job listing not found or inactive.",
            )
        jd_data = job_listing_to_jd_data(job)

    job_title = normalise_it_role((payload.job_title or "").strip() or infer_job_title(cv_data, jd_data))
    interview_plan = build_interview_plan(
        cv_data=cv_data,
        jd_data=jd_data,
        job_title=job_title,
        mode=payload.mode,
        focus_area=payload.focus_area,
        duration_minutes=payload.duration_minutes,
    )
    try:
        create_kwargs = _supported_kwargs(
            service.create_session,
            {
                "session": db,
                "cv_id": payload.cv_id,
                "user_id": user.id,
                "mode": payload.mode,
                "job_listing_id": getattr(payload, "job_listing_id", None),
                "focus_area": payload.focus_area,
                "duration_minutes": getattr(payload, "duration_minutes", 5),
                "job_title": job_title,
                "jd_data": jd_data,
                "interview_plan": interview_plan,
            },
        )
        session_id = await service.create_session(**create_kwargs)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create session: {exc}",
        ) from exc

    frontend_base_url = (
        settings.frontend_base_url
        or (settings.allowed_origins[0] if settings.allowed_origins else "")
        or str(request.base_url).rstrip("/")
    )

    return InterviewSessionResponse(
        session_id=session_id,
        cv_id=payload.cv_id,
        mode=payload.mode,
        status="created",
        room_name=InterviewService.room_name_for(session_id),
        meeting_url=InterviewService.meeting_url_for(session_id, frontend_base_url),
        job_title=job_title,
        duration_minutes=payload.duration_minutes,
        interview_plan=interview_plan,
    )


@router.get("/sessions", response_model=list[InterviewReportResponse])
@limiter.limit("100/minute")
async def list_interview_sessions(
    request: Request,
    user: Annotated[User, Depends(get_current_user)],
    service: Annotated[InterviewService, Depends(get_interview_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> list[InterviewReportResponse]:
    """List interview sessions for the current user."""
    try:
        sessions = await service.list_sessions(db, user.id)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list sessions: {exc}",
        ) from exc

    reports: list[InterviewReportResponse] = []
    for record in sessions:
        stored_scores = record.star_scores or {}
        star_scores: list[STARScore] = []
        for score_dict in stored_scores.get("scores", []):
            try:
                star_scores.append(
                    STARScore(
                        situation=float(score_dict.get("situation_score", 0)),
                        task=float(score_dict.get("task_score", 0)),
                        action=float(score_dict.get("action_score", 0)),
                        result=float(score_dict.get("result_score", 0)),
                    )
                )
            except Exception:
                continue

        setup = stored_scores.get("setup", {}) if isinstance(stored_scores, dict) else {}
        reports.append(
            InterviewReportResponse(
                session_id=str(record.id),
                overall_confidence=float(record.overall_confidence or 0.0),
                total_questions=int(record.total_questions or 0),
                star_scores=star_scores,
                logic_issues=list(record.logic_issues or []),
                improvement_suggestions=list(record.improvement_suggestions or []),
                behavior_score=float(stored_scores.get("behavior_score", 100.0)),
                behavior_observations=list(stored_scores.get("behavior_observations", [])),
                scorecard=stored_scores.get("scorecard") or {},
                interview_plan=stored_scores.get("interview_plan") or {},
                created_at=record.started_at.isoformat() if record.started_at else None,
                title=stored_scores.get("title") or setup.get("job_title") or "Phá»ng váº¥n AI",
                focus_area=stored_scores.get("focus_area") or setup.get("focus_area") or "",
                status="incomplete" if (record.completed_at is None or record.total_questions == 0) else "completed",
            )
        )
    return reports


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
    service: Annotated[InterviewService, Depends(get_interview_service)],
    extraction: Annotated[ExtractionService, Depends(get_extraction_service)],
    db: Annotated[AsyncSession, Depends(get_db_session)],
) -> None:
    """Real-time voice interview channel.

    Frame protocol:
      - First message (JSON): ``{"token": "<jwt>", "session_id": "...", "duration_minutes": 5}``
      - Subsequent binary frames: raw PCM Int16 mono 16 kHz audio chunks.
      - Server sends JSON events and binary PCM TTS audio.
    """
    await websocket.accept()
    _pipeline = None

    async def safe_close(code: int) -> None:
        with contextlib.suppress(Exception):
            await websocket.close(code=code)

    try:
        # Require authentication as the first message
        auth_data = await websocket.receive_json()
        token = auth_data.get("token")
        session_id = str(auth_data.get("session_id") or "").strip()
        if not session_id:
            raise ValueError("Initial message missing session_id")
        payload = validate_ws_token(token)
        user_id = payload.get("sub") or payload.get("id")
        if not user_id:
            raise ValueError("Token missing user ID")
    except WebSocketDisconnect:
        _logger.info("WS /interview/ws: client disconnected before auth message")
        return
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, ValueError) as exc:
        _logger.warning("WS /interview/ws: auth failed â€” %s", exc)
        await safe_close(1008)
        return
    except Exception as exc:
        _logger.warning("WS /interview/ws: invalid initial message format â€” %s", exc)
        await safe_close(1008)
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

    stmt = select(InterviewSession).where(
        InterviewSession.id == session_id,
        InterviewSession.user_id == str(user_id),
    )
    result = await db.execute(stmt)
    session_record = result.scalars().first()
    if session_record is None:
        _logger.warning(
            "WS /interview/ws: session %s not found or denied for user=%s",
            session_id,
            user_id,
        )
        await safe_close(1008)
        return

    cv = await extraction.get_cv(db, session_record.cv_id, str(user_id))
    if cv is None:
        _logger.warning(
            "WS /interview/ws: CV %s for session %s not found or denied",
            session_record.cv_id,
            session_id,
        )
        await safe_close(1008)
        return

    # Initialize pipeline after ownership checks pass.
    _pipeline = pipeline_factory(safe_send_json, safe_send_bytes, user_id=str(user_id))

    cv_data: dict[str, Any] = cv.optimized_data or cv.extracted_data or {}
    stored_context = session_record.star_scores or {}
    setup_context = stored_context.get("setup", {}) if isinstance(stored_context, dict) else {}
    interview_plan = stored_context.get("interview_plan", {}) if isinstance(stored_context, dict) else {}
    jd_data: dict[str, Any] = {}
    if session_record.job_listing_id:
        job_result = await db.execute(
            select(JobListing).where(
                JobListing.id == session_record.job_listing_id,
                JobListing.is_active.is_(True),
            )
        )
        jd_data = job_listing_to_jd_data(job_result.scalars().first())
    if not jd_data:
        stored_jd = setup_context.get("jd_data") if isinstance(setup_context, dict) else {}
        jd_data = stored_jd if isinstance(stored_jd, dict) else {}
    job_title: str = normalise_it_role(str(
        (setup_context.get("job_title") if isinstance(setup_context, dict) else "")
        or infer_job_title(cv_data, jd_data)
    ))
    mode: str = session_record.mode
    try:
        stored_duration = setup_context.get("duration_minutes") if isinstance(setup_context, dict) else None
        duration_minutes = max(1, min(60, int(stored_duration or auth_data.get("duration_minutes", 5))))
    except (TypeError, ValueError):
        duration_minutes = 5

    try:
        await _pipeline.start(
            session_id=session_id,
            job_title=job_title,
            cv_data=cv_data,
            jd_data=jd_data,
            interview_plan=interview_plan,
            mode=mode,
            duration_minutes=duration_minutes,
        )
    except Exception as exc:
        _logger.error("WS /interview/ws: pipeline.start failed â€” %s", exc)
        await safe_close(1011)
        return

    try:
        while True:
            data = await websocket.receive()
            if "bytes" in data:
                await _pipeline.feed_audio(data["bytes"])
            elif "text" in data:
                try:
                    msg = json.loads(data["text"])
                    if msg.get("action") == "stop":
                        break
                    if msg.get("action") == "behavior_event":
                        await _pipeline.record_behavior_event(msg.get("event") or {})
                    if msg.get("action") == "text_answer":
                        await _pipeline.feed_text(str(msg.get("text") or ""))
                except Exception:
                    pass
    except WebSocketDisconnect:
        _logger.info("WebSocket disconnected (user=%s)", user_id)
    except Exception as exc:
        _logger.error("WebSocket error: %s", exc)
        await safe_close(1000)
    finally:
        if _pipeline is not None:
            try:
                evaluation = await _pipeline.stop()
                if evaluation:
                    evaluation["session_id"] = session_id
                    await service.persist_session(db, evaluation)
            except Exception as exc:
                _logger.error("WS /interview/ws: failed to persist final evaluation: %s", exc)
