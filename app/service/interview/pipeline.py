"""Real-time voice interview pipeline.

Owns one WebSocket session: microphone PCM in, interviewer audio out.

Audio flow:
    Mic PCM (16kHz)  →  VAD (silero-vad) silence detection
                     →  STT (faster-whisper int8, lang=vi)
                     →  LLM streaming (generate_chat_stream, chat history)
                     →  TTS per-sentence streaming (synthesize_stream)
                     →  WebSocket send_bytes  →  Speaker

State machine:
    LISTENING   — VAD running, accepting mic audio.
    PROCESSING  — VAD triggered silence. STT + LLM thinking. Mic ignored.
    SPEAKING    — TTS sending PCM chunks to client.
    STOPPED     — Session ended.
"""

from __future__ import annotations

import asyncio
import logging
import re
import time
import uuid
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.llm_connector import LLMConnector
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector
from app.service.interview.agents import evaluate_node, scorecard_node
from app.service.interview.behavior import (
    behavior_feedback_lines,
    normalise_behavior_event,
    summarize_behavior,
)
from app.service.interview.pacing import PacingClock, PacingSignal, is_terminal, signal_instruction
from app.service.interview.planning import plan_for_prompt
from app.service.interview.state import ChatMessage, InterviewState, InterviewTurn
from app.service.interview.state_machine import SessionPhase

logger = logging.getLogger(__name__)

# Sentence boundary detection — flush TTS when one of these patterns is found
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.?!\n])\s*")
# Minimum characters in a TTS sentence (avoid sending tiny fragments)
_MIN_SENTENCE_CHARS = 15
_MAX_QUESTIONS: dict[str, int] = {"quick": 4, "practice": 7, "mock": 10}
_GRACE_MINUTES: dict[str, int] = {"quick": 1, "practice": 2, "mock": 3}


def _split_sentence(text: str) -> tuple[str, str]:
    """Split off the first complete sentence from ``text``.

    Returns (sentence, remainder). If no boundary found, returns ("", text).
    """
    matches = list(_SENTENCE_BOUNDARY.finditer(text))
    if not matches:
        return "", text

    for match in matches:
        end_idx = match.end()
        prefix = text[:end_idx].strip()
        if len(prefix) >= _MIN_SENTENCE_CHARS:
            remainder = text[end_idx:]
            return prefix, remainder
    return "", text


def _build_system_prompt(
    job_title: str,
    cv_data: dict[str, Any],
    jd_data: dict[str, Any] | None,
    interview_plan: dict[str, Any] | None,
    mode: str,
    duration_minutes: int,
) -> str:
    """Compose the Vietnamese interviewer system prompt."""
    cv_summary = cv_data.get("summary", "") or cv_data.get("raw_text", "")[:800]
    jd_summary = ""
    if jd_data:
        jd_summary = jd_data.get("description", "") or jd_data.get("raw_text", "")[:600]
    mode_instruction = {
        "practice": "Phỏng vấn luyện tập — thân thiện, khuyến khích, đưa gợi ý nhỏ sau mỗi câu.",
        "mock": "Phỏng vấn thử thực chiến — chuyên nghiệp, đánh giá nghiêm túc, không gợi ý.",
        "quick": "Phỏng vấn nhanh — hỏi 3-4 câu trọng tâm, ngắn gọn, tập trung kỹ năng cốt lõi.",
    }.get(mode, "Phỏng vấn tiêu chuẩn.")

    return f"""Bạn là một chuyên gia phỏng vấn tuyển dụng người Việt, \
đang phỏng vấn ứng viên cho vị trí **{job_title}**.

## Phong cách
- Nói bằng tiếng Việt tự nhiên, lịch sự, chuyên nghiệp.
- Hỏi một câu tại một thời điểm. Không liệt kê nhiều câu cùng lúc.
- Câu trả lời ngắn gọn (1-2 câu) khi nhận xét hoặc chuyển chủ đề.
- Chế độ: {mode_instruction}
- Thời lượng phỏng vấn: {duration_minutes} phút.

## Thông tin ứng viên (CV)
{cv_summary if cv_summary else "(Chưa có thông tin CV)"}

## Mô tả vị trí (JD)
{jd_summary if jd_summary else "(Chưa có JD — hỏi theo kỹ năng tổng quát cho vị trí)"}

## Quy trình
1. Bắt đầu bằng lời chào ngắn và câu hỏi giới thiệu bản thân.
2. Đặt các câu hỏi STAR (Tình huống, Nhiệm vụ, Hành động, Kết quả).
3. Lắng nghe và đặt câu hỏi tiếp nối nếu câu trả lời chưa rõ.
4. Khi hết thời gian, thông báo kết thúc lịch sự.

Hãy bắt đầu phỏng vấn ngay bây giờ."""


def _build_planned_system_prompt(
    job_title: str,
    cv_data: dict[str, Any],
    jd_data: dict[str, Any] | None,
    interview_plan: dict[str, Any] | None,
    mode: str,
    duration_minutes: int,
) -> str:
    """Compose the interviewer prompt with the precomputed plan attached."""
    base_prompt = _build_system_prompt(
        job_title=job_title,
        cv_data=cv_data,
        jd_data=jd_data,
        interview_plan=interview_plan,
        mode=mode,
        duration_minutes=duration_minutes,
    )
    return (
        f"{base_prompt}\n\n"
        "## Interview plan / evaluation brief\n"
        f"{plan_for_prompt(interview_plan or {})}\n\n"
        "## Important operating rules\n"
        "- Bám theo interview plan nhưng vẫn hỏi tự nhiên theo câu trả lời của ứng viên.\n"
        "- Chỉ hỏi một câu tại một thời điểm.\n"
        "- Không đọc điểm số hoặc kết luận tuyển dụng trong lúc phỏng vấn.\n"
        "- Ưu tiên câu hỏi dựa trên CV, dự án, kinh nghiệm thật và yêu cầu JD nếu có.\n"
    )


def _build_system_prompt(
    job_title: str,
    cv_data: dict[str, Any],
    jd_data: dict[str, Any] | None,
    interview_plan: dict[str, Any] | None,
    mode: str,
    duration_minutes: int,
) -> str:
    """Compose the final Vietnamese interviewer prompt for CV-first interviews."""
    cv_summary = cv_data.get("summary", "") or cv_data.get("raw_text", "")[:1200]
    jd_summary = ""
    if jd_data:
        jd_summary = jd_data.get("description", "") or jd_data.get("raw_text", "")[:900]

    mode_instruction = {
        "practice": (
            "Luyện tập: thân thiện, khuyến khích, có thể phản hồi rất ngắn sau câu trả lời "
            "nhưng vẫn phải hỏi chuyên nghiệp và có chiều sâu."
        ),
        "mock": (
            "Mock interview: nghiêm túc như phỏng vấn thật, không gợi ý đáp án, "
            "chỉ hỏi follow-up khi cần evidence."
        ),
        "quick": "Phỏng vấn nhanh: chọn câu hỏi có giá trị đánh giá cao nhất, tránh lan man.",
    }.get(mode, "Phỏng vấn tiêu chuẩn, chuyên nghiệp, tập trung vào CV/JD.")

    return f"""Bạn là Senior Interviewer người Việt đang phỏng vấn ứng viên cho vị trí {job_title}.

Mục tiêu phiên live:
- Kiểm chứng năng lực thật trong CV, mức phù hợp với JD và khả năng trình bày theo STAR.
- Hỏi sâu vào dự án, kinh nghiệm, kỹ năng, impact và khoảng trống CV/JD.
- Tạo trải nghiệm tự nhiên như một buổi phỏng vấn thật trên web.

Phong cách:
- Tiếng Việt tự nhiên, lịch sự, ngắn gọn.
- Mỗi lượt chỉ hỏi MỘT câu.
- Không đọc rubric, không nói điểm số, không kết luận tuyển dụng trong lúc phỏng vấn.
- Khi ứng viên trả lời mơ hồ, hỏi follow-up về vai trò cá nhân, hành động cụ thể, trade-off hoặc kết quả đo được.
- Khi câu trả lời đã đủ rõ, chuyển sang câu hỏi kế tiếp theo kế hoạch.
- Nếu gần hết thời gian, chốt lịch sự thay vì mở chủ đề mới.

Chế độ: {mode_instruction}
Thời lượng mục tiêu: {duration_minutes} phút.

CV ứng viên:
{cv_summary if cv_summary else "(Chưa có nội dung CV đủ rõ. Hỏi mở để xác minh kinh nghiệm và kỹ năng chính.)"}

JD / yêu cầu vị trí:
{jd_summary if jd_summary else "(Chưa có JD chi tiết. Đánh giá theo vai trò mục tiêu và nội dung CV.)"}

Luồng hỏi ưu tiên:
1. Mở đầu ngắn và yêu cầu ứng viên giới thiệu trọng tâm phù hợp vị trí.
2. Deep-dive vào kinh nghiệm/dự án nổi bật trong CV.
3. Hỏi STAR để lấy evidence về trách nhiệm cá nhân, hành động và kết quả.
4. Kiểm tra kỹ năng/JD fit và các gap quan trọng.
5. Quan sát cách giao tiếp, độ rõ ràng và khả năng phản biện.
6. Kết thúc bằng cơ hội bổ sung nếu còn thời gian.

Hãy bắt đầu ngay bằng lời chào ngắn và một câu hỏi mở đầu sát CV/vị trí."""


def _build_planned_system_prompt(
    job_title: str,
    cv_data: dict[str, Any],
    jd_data: dict[str, Any] | None,
    interview_plan: dict[str, Any] | None,
    mode: str,
    duration_minutes: int,
) -> str:
    """Compose the final interviewer prompt with the precomputed plan attached."""
    base_prompt = _build_system_prompt(
        job_title=job_title,
        cv_data=cv_data,
        jd_data=jd_data,
        interview_plan=interview_plan,
        mode=mode,
        duration_minutes=duration_minutes,
    )
    return (
        f"{base_prompt}\n\n"
        "Interview plan / evaluation brief:\n"
        f"{plan_for_prompt(interview_plan or {})}\n\n"
        "Operating rules:\n"
        "- Bám interview plan nhưng phản ứng tự nhiên theo câu trả lời thực tế.\n"
        "- Chỉ hỏi một câu mỗi lượt; câu hỏi tối đa khoảng 35 từ.\n"
        "- Ưu tiên câu hỏi dựa trên CV, dự án, kinh nghiệm thật và yêu cầu JD.\n"
        "- Không bịa thông tin ngoài CV/JD/transcript.\n"
        "- Không tiết lộ scorecard, recommendation hoặc đánh giá nội bộ cho ứng viên trong phiên live.\n"
    )


class InterviewPipeline:
    """Manages one real-time interview session over a WebSocket."""

    def __init__(
        self,
        llm: LLMConnector,
        stt: VoiceSTTConnector,
        tts: VoiceTTSConnector,
        send_json: Callable[[dict[str, Any]], Awaitable[None]],
        send_bytes: Callable[[bytes], Awaitable[None]],
        user_id: str,
    ) -> None:
        self._llm = llm
        self._stt = stt
        self._tts = tts
        self._send_json = send_json
        self._send_bytes = send_bytes
        self._user_id = user_id

        self.state: InterviewState | None = None
        self._phase = SessionPhase.STOPPED
        self._abort_tts = asyncio.Event()
        self._final_evaluation: dict[str, Any] | None = None
        self._candidate_turn_count = 0
        self._pacing_clock: PacingClock | None = None
        self._last_pacing_signal: PacingSignal | None = None

        # Raw PCM audio buffer (bytes) accumulated during LISTENING phase
        self._audio_buffer: bytearray = bytearray()
        # VAD consumes _audio_buffer in windows; STT still needs the whole utterance.
        self._speech_buffer: bytearray = bytearray()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start(
        self,
        job_title: str,
        cv_data: dict[str, Any],
        jd_data: dict[str, Any] | None = None,
        interview_plan: dict[str, Any] | None = None,
        mode: str = "practice",
        duration_minutes: int = 5,
        session_id: str | None = None,
    ) -> None:
        """Initialise the session and emit the interviewer's first greeting."""
        session_id = session_id or str(uuid.uuid4())
        system_prompt = _build_planned_system_prompt(
            job_title, cv_data, jd_data, interview_plan, mode, duration_minutes
        )
        self._audio_buffer.clear()
        self._speech_buffer.clear()
        self._final_evaluation = None
        self._candidate_turn_count = 0
        self._last_pacing_signal = None
        self._pacing_clock = PacingClock(
            duration_minutes=duration_minutes,
            grace_minutes=_GRACE_MINUTES.get(mode, 2),
            dead_air_prompt_sec=45,
            max_silence_end_min=max(3, duration_minutes),
            wrap_soon_minutes=1 if duration_minutes <= 5 else 2,
            now=time.time,
        )
        self._pacing_clock.start()

        self.state = InterviewState(
            session_id=session_id,
            cv_data=cv_data,
            jd_data=jd_data or {},
            interview_plan=interview_plan or {},
            job_title=job_title,
            interview_mode=mode,  # type: ignore[arg-type]
            duration_minutes=duration_minutes,
            start_time=time.time(),
            chat_history=[ChatMessage(role="system", content=system_prompt)],
        )

        logger.info("[Pipeline] Session %s started — user=%s mode=%s", session_id, self._user_id, mode)
        await self._send_json(
            {
                "event": "session_started",
                "session_id": session_id,
                "job_title": job_title,
                "duration_minutes": duration_minutes,
                "interview_plan": interview_plan or {},
            }
        )

        # Emit greeting
        self._phase = SessionPhase.SPEAKING
        await self._generate_and_speak()

    async def feed_audio(self, pcm_bytes: bytes) -> None:
        """Consume one chunk of microphone PCM Int16 mono 16kHz audio.

        Only accumulates while in LISTENING phase; audio arriving during
        PROCESSING or SPEAKING is silently dropped to avoid cross-talk.
        """
        if self._phase != SessionPhase.LISTENING:
            return

        self._audio_buffer.extend(pcm_bytes)

        # VAD: analyse in 512-sample (1024-byte) windows
        while len(self._audio_buffer) >= 1024:
            window_bytes = bytes(self._audio_buffer[:1024])
            del self._audio_buffer[:1024]
            self._speech_buffer.extend(window_bytes)

            import numpy as np
            window_f32 = np.frombuffer(window_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            if self._stt.check_vad(window_f32):
                # Silence threshold crossed: send the complete utterance to STT.
                snapshot = bytes(self._speech_buffer)
                self._audio_buffer.clear()
                self._speech_buffer.clear()
                self._stt.reset_vad()
                await self._process_user_turn(snapshot)
                break

    async def stop(self) -> dict[str, Any]:
        """Tear down the session and return the final STAR evaluation payload."""
        if self.state is None:
            return {}
        if self._final_evaluation is not None:
            return self._final_evaluation

        self._phase = SessionPhase.STOPPED
        self._abort_tts.set()

        logger.info("[Pipeline] Stopping session %s", self.state.session_id)
        evaluation = await self._run_final_evaluation()
        self._final_evaluation = evaluation
        await self._send_json({"event": "session_ended", "evaluation": evaluation})
        return evaluation

    async def record_behavior_event(self, raw_event: dict[str, Any]) -> None:
        """Store a lightweight browser/camera behavioral observation."""
        if self.state is None:
            return
        event = normalise_behavior_event(raw_event)
        if event is None:
            return
        self.state.behavior_events.append(event)
        await self._send_json(
            {
                "event": "behavior_event_ack",
                "kind": event.kind,
                "severity": event.severity,
            }
        )

    async def feed_text(self, text: str) -> None:
        """Accept a typed candidate answer as a fallback to microphone/STT."""
        transcript = text.strip()
        if not transcript or self._phase not in {SessionPhase.LISTENING, SessionPhase.PROCESSING}:
            return
        await self._handle_user_transcript(transcript)

    # ------------------------------------------------------------------
    # Internal: user turn processing
    # ------------------------------------------------------------------

    async def _process_user_turn(self, audio_bytes: bytes) -> None:
        """STT → update history → LLM → TTS."""
        if self.state is None:
            return

        self._phase = SessionPhase.PROCESSING
        await self._send_json({"event": "phase_change", "phase": SessionPhase.PROCESSING})

        # --- STT ---
        try:
            transcript = await self._stt.transcribe(audio_bytes)
        except Exception as exc:
            logger.error("[Pipeline] STT failed: %s", exc)
            self._phase = SessionPhase.LISTENING
            await self._send_json({"event": "phase_change", "phase": SessionPhase.LISTENING})
            return

        if not transcript.strip():
            # Empty transcript — go back to listening
            self._phase = SessionPhase.LISTENING
            await self._send_json({"event": "phase_change", "phase": SessionPhase.LISTENING})
            return

        await self._handle_user_transcript(transcript)

    async def _handle_user_transcript(self, transcript: str) -> None:
        """Update state from a candidate transcript, then ask the LLM to respond."""
        if self.state is None:
            return

        logger.info("[Pipeline] Transcript: %r", transcript)
        self.state.latest_transcript = transcript
        self.state.chat_history.append(ChatMessage(role="user", content=transcript))
        self.state.turns.append(InterviewTurn(role="candidate", content=transcript))
        self._candidate_turn_count += 1
        if self._pacing_clock is not None:
            self._pacing_clock.note_activity()

        await self._send_json({"event": "transcript", "text": transcript})

        # --- LLM + TTS ---
        self._phase = SessionPhase.SPEAKING
        await self._send_json({"event": "phase_change", "phase": SessionPhase.SPEAKING})
        await self._generate_and_speak()

    # ------------------------------------------------------------------
    # Internal: LLM → sentence chunking → TTS streaming
    # ------------------------------------------------------------------

    def _inject_context_message(self) -> None:
        """Attach runtime guidance without permanently bloating chat history."""
        if self.state is None:
            return

        max_questions = _MAX_QUESTIONS.get(self.state.interview_mode, 7)
        pacing_signal = self._current_pacing_signal()
        instruction = signal_instruction(pacing_signal)
        remaining_seconds = int(
            self._pacing_clock.remaining_to_target()
            if self._pacing_clock is not None
            else self.state.get_remaining_seconds()
        )
        should_wrap = (
            self._candidate_turn_count >= max_questions
            or remaining_seconds <= 45
            or pacing_signal in {PacingSignal.WRAP_UP_NOW, PacingSignal.FORCE_END, PacingSignal.ABANDON}
        )
        if should_wrap:
            guidance = (
                "Runtime guidance: this should be the final interviewer turn. "
                "Briefly thank the candidate, close the interview, and do not ask a new question."
            )
        else:
            questions_left = max(1, max_questions - self._candidate_turn_count)
            guidance = (
                "Runtime guidance: ask exactly one focused follow-up or next CV/JD-based question. "
                f"Approximate candidate turns left: {questions_left}. "
                f"Approximate seconds left: {remaining_seconds}."
            )
        if instruction:
            guidance = f"{guidance} {instruction}"

        self.state.chat_history = [
            message
            for message in self.state.chat_history
            if not (message.role == "system" and message.content.startswith("Runtime guidance:"))
        ]
        self.state.chat_history.append(ChatMessage(role="system", content=guidance))

    def _current_pacing_signal(self) -> PacingSignal:
        if self._pacing_clock is None:
            return PacingSignal.ON_TRACK
        signal = self._pacing_clock.signal()
        if signal != self._last_pacing_signal:
            logger.info("[Pipeline] Pacing signal changed: %s", signal.value)
            self._last_pacing_signal = signal
        return signal

    def _is_interview_over(self) -> bool:
        if self.state is None:
            return True
        max_questions = _MAX_QUESTIONS.get(self.state.interview_mode, 7)
        pacing_signal = self._current_pacing_signal()
        return (
            is_terminal(pacing_signal)
            or pacing_signal == PacingSignal.WRAP_UP_NOW
            or self._candidate_turn_count >= max_questions
        )

    async def _generate_and_speak(self) -> None:
        """Stream LLM tokens, chunk into sentences, synthesise + send PCM."""
        if self.state is None:
            return

        self._inject_context_message()
        self._abort_tts.clear()
        full_response: list[str] = []
        pending_text = ""

        try:
            async for token in self._llm.generate_chat_stream(
                self.state.to_llm_messages(), use_cloud=self._llm.has_cloud
            ):
                if self._abort_tts.is_set() or self._phase == SessionPhase.STOPPED:
                    break

                full_response.append(token)
                pending_text += token

                # Try to flush a complete sentence
                sentence, pending_text = _split_sentence(pending_text)
                if sentence:
                    await self._speak_sentence(sentence)
                    if self._abort_tts.is_set():
                        break

            # Flush any remaining text
            if pending_text.strip() and not self._abort_tts.is_set():
                await self._speak_sentence(pending_text.strip())

        except Exception as exc:
            logger.error("[Pipeline] LLM/TTS error: %s", exc)
            await self._send_json({"event": "error", "message": str(exc)})
        finally:
            assistant_content = "".join(full_response).strip()
            if assistant_content and self.state:
                self.state.chat_history.append(
                    ChatMessage(role="assistant", content=assistant_content)
                )
                self.state.turns.append(
                    InterviewTurn(role="interviewer", content=assistant_content)
                )
                await self._send_json({"event": "assistant_text", "text": assistant_content})

            # Check time-based wrap-up
            if self.state and self._is_interview_over() and self._phase != SessionPhase.STOPPED:
                await self._send_json({"event": "time_up"})
                await self.stop()
            else:
                self._phase = SessionPhase.LISTENING
                await self._send_json({"event": "phase_change", "phase": SessionPhase.LISTENING})

    async def _speak_sentence(self, sentence: str) -> None:
        """Synthesise one sentence and stream its PCM chunks to the client."""
        logger.info("[Pipeline] Speaking sentence: %r", sentence)
        try:
            async for pcm_chunk in self._tts.synthesize_stream(sentence):
                if self._abort_tts.is_set():
                    return
                await self._send_bytes(pcm_chunk)
        except Exception as exc:
            logger.warning("[Pipeline] TTS sentence failed: %s", exc)

    # ------------------------------------------------------------------
    # Internal: evaluation
    # ------------------------------------------------------------------

    async def _run_final_evaluation(self) -> dict[str, Any]:
        """Run STAR scoring + holistic wrap-up and return the payload."""
        if self.state is None:
            return {}

        try:
            # Evaluate unanswered turns
            candidate_turns = [t for t in self.state.turns if t.role == "candidate"]
            if candidate_turns and len(self.state.star_scores) < len(candidate_turns):
                eval_result = await evaluate_node(self.state, self._llm)
                if eval_result:
                    self.state = self.state.model_copy(update=eval_result)

        except Exception as exc:
            logger.error("[Pipeline] Final evaluation failed: %s", exc)

        behavior_summary = summarize_behavior(self.state.behavior_events)
        behavior_issues, behavior_suggestions = behavior_feedback_lines(behavior_summary)
        scorecard = await scorecard_node(self.state, self._llm, behavior_summary)
        final_feedback = scorecard.summary or scorecard.headline or self.state.final_feedback
        strengths = scorecard.strengths or self.state.strengths
        improvements = scorecard.concerns or self.state.improvements

        return {
            "session_id": self.state.session_id,
            "job_title": self.state.job_title,
            "duration_seconds": time.time() - self.state.start_time,
            "overall_score": scorecard.overall_score * 2,
            "scorecard": scorecard.model_dump(),
            "strengths": strengths,
            "improvements": improvements + behavior_suggestions,
            "final_feedback": final_feedback,
            "star_scores": [s.model_dump() for s in self.state.star_scores],
            "transcript": [t.model_dump() for t in self.state.turns],
            "behavior_score": behavior_summary.score,
            "behavior_observations": [obs.model_dump() for obs in behavior_summary.observations],
            "behavior_issues": behavior_issues,
        }
