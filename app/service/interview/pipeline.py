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
from app.service.interview.agents import evaluate_node, wrap_up_node
from app.service.interview.state import ChatMessage, InterviewState, InterviewTurn
from app.service.interview.state_machine import SessionPhase

logger = logging.getLogger(__name__)

# Sentence boundary detection — flush TTS when one of these patterns is found
_SENTENCE_BOUNDARY = re.compile(r"(?<=[.?!\n])\s*")
# Minimum characters in a TTS sentence (avoid sending tiny fragments)
_MIN_SENTENCE_CHARS = 15


def _split_sentence(text: str) -> tuple[str, str]:
    """Split off the first complete sentence from ``text``.

    Returns (sentence, remainder). If no boundary found, returns ("", text).
    """
    parts = _SENTENCE_BOUNDARY.split(text, maxsplit=1)
    if len(parts) >= 2 and len(parts[0].strip()) >= _MIN_SENTENCE_CHARS:
        return parts[0].strip(), parts[1]
    return "", text


def _build_system_prompt(
    job_title: str,
    cv_data: dict[str, Any],
    jd_data: dict[str, Any] | None,
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

        # Raw PCM audio buffer (bytes) accumulated during LISTENING phase
        self._audio_buffer: bytearray = bytearray()
        # asyncio.Queue: each item is a bytearray snapshot of _audio_buffer to transcribe
        self._stt_queue: asyncio.Queue[bytearray] = asyncio.Queue()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start(
        self,
        job_title: str,
        cv_data: dict[str, Any],
        jd_data: dict[str, Any] | None = None,
        mode: str = "practice",
        duration_minutes: int = 5,
    ) -> None:
        """Initialise the session and emit the interviewer's first greeting."""
        session_id = str(uuid.uuid4())
        system_prompt = _build_system_prompt(job_title, cv_data, jd_data, mode, duration_minutes)

        self.state = InterviewState(
            session_id=session_id,
            cv_data=cv_data,
            jd_data=jd_data or {},
            job_title=job_title,
            interview_mode=mode,  # type: ignore[arg-type]
            duration_minutes=duration_minutes,
            start_time=time.time(),
            chat_history=[ChatMessage(role="system", content=system_prompt)],
        )

        logger.info("[Pipeline] Session %s started — user=%s mode=%s", session_id, self._user_id, mode)
        await self._send_json({"event": "session_started", "session_id": session_id})

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

            import numpy as np
            window_f32 = np.frombuffer(window_bytes, dtype=np.int16).astype(np.float32) / 32768.0

            if self._stt._vad.update(window_f32):
                # Silence threshold crossed — snapshot and queue for STT
                snapshot = bytearray(self._audio_buffer)
                self._audio_buffer.clear()
                self._stt._vad.reset()
                await self._process_user_turn(bytes(snapshot))
                break

    async def stop(self) -> dict[str, Any]:
        """Tear down the session and return the final STAR evaluation payload."""
        self._phase = SessionPhase.STOPPED
        self._abort_tts.set()

        if self.state is None:
            return {}

        logger.info("[Pipeline] Stopping session %s", self.state.session_id)
        evaluation = await self._run_final_evaluation()
        await self._send_json({"event": "session_ended", "evaluation": evaluation})
        return evaluation

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

        logger.info("[Pipeline] Transcript: %r", transcript)
        self.state.latest_transcript = transcript
        self.state.chat_history.append(ChatMessage(role="user", content=transcript))
        self.state.turns.append(InterviewTurn(role="candidate", content=transcript))

        await self._send_json({"event": "transcript", "text": transcript})

        # --- LLM + TTS ---
        self._phase = SessionPhase.SPEAKING
        await self._send_json({"event": "phase_change", "phase": SessionPhase.SPEAKING})
        await self._generate_and_speak()

    # ------------------------------------------------------------------
    # Internal: LLM → sentence chunking → TTS streaming
    # ------------------------------------------------------------------

    async def _generate_and_speak(self) -> None:
        """Stream LLM tokens, chunk into sentences, synthesise + send PCM."""
        if self.state is None:
            return

        self._abort_tts.clear()
        full_response: list[str] = []
        pending_text = ""

        try:
            async for token in self._llm.generate_chat_stream(
                self.state.to_llm_messages(), use_cloud=bool(self._llm._cloud_api_key)
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
            if self.state and self.state.is_time_up() and self._phase != SessionPhase.STOPPED:
                await self._send_json({"event": "time_up"})
                await self.stop()
            else:
                self._phase = SessionPhase.LISTENING
                await self._send_json({"event": "phase_change", "phase": SessionPhase.LISTENING})

    async def _speak_sentence(self, sentence: str) -> None:
        """Synthesise one sentence and stream its PCM chunks to the client."""
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

            wrap_result = await wrap_up_node(self.state, self._llm)
            if wrap_result:
                self.state = self.state.model_copy(update=wrap_result)

        except Exception as exc:
            logger.error("[Pipeline] Final evaluation failed: %s", exc)

        return {
            "session_id": self.state.session_id,
            "job_title": self.state.job_title,
            "duration_seconds": time.time() - self.state.start_time,
            "overall_score": self.state.overall_score,
            "strengths": self.state.strengths,
            "improvements": self.state.improvements,
            "final_feedback": self.state.final_feedback,
            "star_scores": [s.model_dump() for s in self.state.star_scores],
            "transcript": [t.model_dump() for t in self.state.turns],
        }
