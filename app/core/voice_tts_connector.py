"""Voice TTS Connector — text to PCM audio.

Interface for the interview WebSocket. Supported engine styles:
    - ``edge``: Microsoft Edge TTS over the network.
    - ``piper``: Local Piper CLI + ONNX voice model.
    - ``vieneu``: VieNeu Vietnamese TTS SDK (local).

TODO:
    - `synthesize`: Implement synchronous HTTP/CLI execution to convert full `text`
      to a complete PCM buffer (24kHz mono Int16).
    - `synthesize_stream`: Use asyncio subprocess pipes (for Piper) or WebSockets
      (for Edge) to stream PCM bytes back to the caller incrementally, enabling low-latency.
    - Implement a routing mechanism using `self._engine` (`edge`, `piper`, `vieneu`)
      and maintain a fallback hierarchy if the primary engine fails.
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
        """Return raw PCM Int16 mono at ``OUTPUT_SAMPLE_RATE``.

        TODO:
            - Based on `self._engine`, delegate to the appropriate synthesis module
              (e.g. `edge_tts`, local `piper` binary).
            - Encode `text` and trigger generation.
            - Ensure output format is strictly PCM Int16, 1 channel (mono), 24000 Hz.
              Use `ffmpeg` via python subprocess to resample if necessary.
            - Return the complete byte payload.
        """
        raise NotImplementedError("VoiceTTSConnector.synthesize is not implemented yet.")

    async def synthesize_stream(
        self,
        text: str,
        voice: str | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """Yield PCM chunks for streaming playback.

        TODO:
            - Initialize a streaming connection (e.g., streaming WebSocket for
              `edge_tts`, or `stdout` stream for `piper` subprocess).
            - As chunks of audio are generated, read them asynchronously.
            - Resample/transcode the raw chunk to PCM Int16 24kHz if the engine
              produces a different format (like MP3).
            - `yield` the raw PCM chunk to be dispatched immediately by the WebSocket.
        """
        raise NotImplementedError("VoiceTTSConnector.synthesize_stream is not implemented yet.")
        if False:  # pragma: no cover
            yield b""
