"""Voice TTS Connector — text to PCM audio (edge-tts / piper / vieneu).

Audio contract:
    - Output: PCM Int16 mono, OUTPUT_SAMPLE_RATE (24 000 Hz).
    - Bytes are sent directly over WebSocket binary frames.

Engine routing (self._engine):
    - ``edge``: Microsoft Edge TTS — MP3 stream decoded to PCM (MVP default).
    - ``piper``: Local Piper CLI + ONNX model — subprocess stdout.
    - ``vieneu``: VieNeu GGUF binary — subprocess, falls back to edge if missing.
"""

from __future__ import annotations

import asyncio
import io
import logging
import subprocess
import tempfile
import typing
from collections.abc import AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)

OUTPUT_SAMPLE_RATE = 24_000  # Hz


def _mp3_bytes_to_pcm(mp3_bytes: bytes) -> bytes:
    """Convert MP3 bytes to PCM Int16 mono 24 kHz via pydub."""
    try:
        from pydub import AudioSegment  # type: ignore[import-untyped]
        seg = AudioSegment.from_file(io.BytesIO(mp3_bytes), format="mp3")
        seg = seg.set_frame_rate(OUTPUT_SAMPLE_RATE).set_channels(1).set_sample_width(2)
        return typing.cast(bytes, seg.raw_data)
    except Exception as exc:
        logger.warning("[TTS] pydub failed (%s) — trying ffmpeg", exc)
        return _ffmpeg_mp3_to_pcm(mp3_bytes)


def _ffmpeg_mp3_to_pcm(mp3_bytes: bytes) -> bytes:
    """Transcode MP3 to PCM s16le via ffmpeg subprocess."""
    proc = subprocess.run(
        ["ffmpeg", "-y", "-f", "mp3", "-i", "pipe:0",
         "-f", "s16le", "-ar", str(OUTPUT_SAMPLE_RATE), "-ac", "1", "pipe:1"],
        input=mp3_bytes, capture_output=True, check=True,
    )
    return proc.stdout


class VoiceTTSConnector:
    """Text-to-speech connector used by InterviewPipeline."""

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
        """Return complete PCM Int16 mono buffer for text."""
        chunks: list[bytes] = []
        async for chunk in self.synthesize_stream(text, voice=voice):
            chunks.append(chunk)
        return b"".join(chunks)

    async def synthesize_stream(
        self, text: str, voice: str | None = None,
    ) -> AsyncGenerator[bytes, None]:
        """Yield PCM Int16 chunks as they become available.

        Routes to the configured engine; falls back to edge if unavailable.
        """
        effective_voice = voice or self._voice
        if self._engine == "edge":
            async for chunk in self._stream_edge(text, effective_voice):
                yield chunk
        elif self._engine == "piper":
            async for chunk in self._stream_piper(text):
                yield chunk
        elif self._engine == "vieneu":
            async for chunk in self._stream_vieneu(text, effective_voice):
                yield chunk
        else:
            logger.warning("[TTS] Unknown engine %r — falling back to edge", self._engine)
            async for chunk in self._stream_edge(text, effective_voice):
                yield chunk

    # ------------------------------------------------------------------
    # Engine: edge-tts (primary)
    # ------------------------------------------------------------------

    async def _stream_edge(self, text: str, voice: str) -> AsyncGenerator[bytes, None]:
        """Stream via Microsoft Edge TTS; decode MP3 to PCM."""
        try:
            import edge_tts
        except ImportError as exc:
            raise RuntimeError("edge-tts not installed. Run: uv add edge-tts") from exc

        try:
            communicate = edge_tts.Communicate(text, voice)
            mp3_buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio" and isinstance(chunk["data"], bytes):
                    mp3_buffer.write(chunk["data"])
        except Exception as exc:
            logger.warning("[TTS] edge-tts communicate.stream failed: %s", exc)
            raise

        mp3_data = mp3_buffer.getvalue()
        if not mp3_data:
            return

        loop = asyncio.get_event_loop()
        pcm_data = await loop.run_in_executor(None, _mp3_bytes_to_pcm, mp3_data)

        chunk_size = OUTPUT_SAMPLE_RATE * 2 * 20 // 1000  # ~20 ms @ 24kHz
        for i in range(0, len(pcm_data), chunk_size):
            yield pcm_data[i : i + chunk_size]

    # ------------------------------------------------------------------
    # Engine: piper (local ONNX)
    # ------------------------------------------------------------------

    async def _stream_piper(self, text: str) -> AsyncGenerator[bytes, None]:
        """Stream via Piper CLI subprocess; resamples 22050 → 24000 Hz."""
        if self._model_path is None or not Path(self._model_path).exists():
            logger.warning("[TTS] Piper model not found — falling back to edge")
            async for chunk in self._stream_edge(text, self._voice):
                yield chunk
            return

        try:
            import numpy as np

            from app.core.voice_stt_connector import _resample

            piper_sr = 22_050
            proc = await asyncio.create_subprocess_exec(
                "piper", "--model", str(self._model_path), "--output-raw",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
            assert proc.stdin and proc.stdout
            proc.stdin.write(text.encode())
            proc.stdin.close()

            chunk_size = piper_sr * 2 * 20 // 1000
            while True:
                raw = await proc.stdout.read(chunk_size)
                if not raw:
                    break
                audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
                audio = _resample(audio, piper_sr, OUTPUT_SAMPLE_RATE)
                yield (audio * 32768.0).clip(-32768, 32767).astype(np.int16).tobytes()

            await proc.wait()
        except FileNotFoundError:
            logger.warning("[TTS] piper binary not found — falling back to edge")
            async for chunk in self._stream_edge(text, self._voice):
                yield chunk

    # ------------------------------------------------------------------
    # Engine: vieneu (local GGUF)
    # ------------------------------------------------------------------

    async def _stream_vieneu(self, text: str, voice: str) -> AsyncGenerator[bytes, None]:
        """Stream via VieNeu binary subprocess; falls back to edge if missing."""
        if self._model_path is None:
            logger.warning("[TTS] VieNeu model_path not set — falling back to edge")
            async for chunk in self._stream_edge(text, "vi-VN-HoaiMyNeural"):
                yield chunk
            return

        model_path = Path(self._model_path)
        candidates = [
            model_path.parent / "vieneu", model_path.parent / "vieneu.exe",
            Path("vieneu"), Path("vieneu.exe"),
        ]
        binary = next((b for b in candidates if b.exists()), None)

        if binary is None:
            logger.warning("[TTS] VieNeu binary not found — falling back to edge")
            async for chunk in self._stream_edge(text, "vi-VN-HoaiMyNeural"):
                yield chunk
            return

        try:
            import numpy as np
            import soundfile as sf  # type: ignore[import-untyped]

            from app.core.voice_stt_connector import _resample

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp_path = Path(tmp.name)

            proc = await asyncio.create_subprocess_exec(
                str(binary), "--model", str(model_path),
                "--speaker", voice, "--output", str(tmp_path), "--text", text,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()

            data, sr = sf.read(str(tmp_path), dtype="int16")
            tmp_path.unlink(missing_ok=True)

            if data.ndim > 1:
                data = data[:, 0]
            if sr != OUTPUT_SAMPLE_RATE:
                f32 = data.astype(np.float32) / 32768.0
                f32 = _resample(f32, sr, OUTPUT_SAMPLE_RATE)
                data = (f32 * 32768.0).clip(-32768, 32767).astype(np.int16)

            raw = data.tobytes()
            chunk_size = OUTPUT_SAMPLE_RATE * 2 * 20 // 1000
            for i in range(0, len(raw), chunk_size):
                yield raw[i : i + chunk_size]

        except Exception as exc:
            logger.error("[TTS] VieNeu error (%s) — falling back to edge", exc)
            async for chunk in self._stream_edge(text, "vi-VN-HoaiMyNeural"):
                yield chunk
