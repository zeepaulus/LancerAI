"""Real-time voice interview pipeline.

Owns one websocket session: microphone PCM in, interviewer audio out.

Audio flow:
    Mic PCM (16kHz)  ->  silence-based turn detection
                     ->  STT transcribe
                     ->  LLM streaming (chat history)
                     ->  TTS streaming (24kHz PCM)
                     ->  Speaker

TODO:
    - Implement ``start`` (build system prompt from CV + JD, kick off greeting).
    - Implement ``feed_audio`` with energy-based turn detection.
    - Implement ``_silence_detection_loop`` to flush user turns to STT.
    - Implement ``_generate_and_speak`` streaming LLM tokens to TTS sentence
      by sentence and sending audio chunks to the client.
    - Implement ``stop`` + ``_run_final_evaluation`` (STAR scoring in Vietnamese).
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.llm_connector import LLMConnector
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector
from app.service.interview.state import InterviewState


class InterviewPipeline:
    """Manages one real-time interview session over a WebSocket."""

    def __init__(
        self,
        llm: LLMConnector,
        stt: VoiceSTTConnector,
        tts: VoiceTTSConnector,
        send_json: Callable[[dict[str, Any]], Awaitable[None]],
        send_bytes: Callable[[bytes], Awaitable[None]],
    ) -> None:
        self._llm = llm
        self._stt = stt
        self._tts = tts
        self._send_json = send_json
        self._send_bytes = send_bytes

        self.state: InterviewState | None = None
        self._active = False
        self._tts_playing = False
        self._abort_generation = asyncio.Event()

    async def start(
        self,
        job_title: str,
        cv_data: dict[str, Any],
        jd_data: dict[str, Any] | None = None,
        mode: str = "practice",
        duration_minutes: int = 5,
    ) -> None:
        """Initialise the session and emit the interviewer's first greeting."""
        raise NotImplementedError("InterviewPipeline.start is not implemented yet.")

    async def feed_audio(self, pcm_bytes: bytes) -> None:
        """Consume one chunk of microphone audio (PCM Int16 mono, 16kHz)."""
        raise NotImplementedError("InterviewPipeline.feed_audio is not implemented yet.")

    async def stop(self) -> dict[str, Any]:
        """Tear down the session and return the final STAR evaluation payload."""
        raise NotImplementedError("InterviewPipeline.stop is not implemented yet.")
