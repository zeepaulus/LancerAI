"""Voice TTS Connector — text to PCM audio.

Interface for the interview WebSocket. Supported engine styles:
    - ``edge``: Microsoft Edge TTS over the network.
    - ``piper``: Local Piper CLI + ONNX voice model.
    - ``vieneu``: VieNeu Vietnamese TTS SDK (local).

TODO:
    - Implement ``synthesize`` (returns PCM 24kHz mono Int16).
    - Implement ``synthesize_stream`` (async chunked PCM for low-latency playback).
    - Pick engine based on ``self._engine`` with graceful fallbacks.
"""

from collections.abc import AsyncGenerator
from pathlib import Path

OUTPUT_SAMPLE_RATE = 24000


class VoiceTTSConnector:
    """Text-to-speech contract used by ``InterviewPipeline``."""

    def __init__(
        self,
        engine: str = "edge",
        model_path: Path | None = None,
        voice: str = "vi-VN-HoaiMyNeural",
        speed: float = 1.0,
    ) -> None:
        self._engine = engine.lower()
        self._model_path = model_path
        self._voice = voice
        self._speed = speed

    async def synthesize(self, text: str, voice: str | None = None) -> bytes:
        """Return raw PCM Int16 mono at ``OUTPUT_SAMPLE_RATE``."""
        raise NotImplementedError("VoiceTTSConnector.synthesize is not implemented yet.")

    async def synthesize_stream(
        self,
        text: str,
        voice: str | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """Yield PCM chunks for streaming playback."""
        raise NotImplementedError("VoiceTTSConnector.synthesize_stream is not implemented yet.")
        if False:  # pragma: no cover
            yield b""
