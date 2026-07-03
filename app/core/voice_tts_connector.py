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


def _waveform_to_pcm(audio: object, sample_rate: int) -> bytes:
    """Convert a VieNeu waveform-like object to raw PCM Int16 mono 24 kHz."""
    import numpy as np

    from app.core.voice_stt_connector import _resample

    if isinstance(audio, tuple) and len(audio) >= 2:
        audio, sample_rate = audio[0], int(audio[1])

    if isinstance(audio, dict):
        sample_rate = int(audio.get("sample_rate") or audio.get("sampling_rate") or sample_rate)
        audio = audio.get("audio") or audio.get("waveform") or audio.get("array")

    if isinstance(audio, bytes):
        try:
            import soundfile as sf  # type: ignore[import-untyped]

            data, sr = sf.read(io.BytesIO(audio), dtype="float32")
            audio = data
            sample_rate = int(sr)
        except Exception:
            return audio

    if hasattr(audio, "detach") and hasattr(audio, "cpu"):
        audio = audio.detach().cpu().numpy()

    data = np.asarray(audio)
    if data.size == 0:
        return b""

    if data.ndim > 1:
        data = data[0] if data.shape[0] <= data.shape[-1] else data[:, 0]

    if sample_rate != OUTPUT_SAMPLE_RATE:
        data = _resample(data.astype(np.float32), sample_rate, OUTPUT_SAMPLE_RATE)

    if data.dtype == np.int16:
        pcm = data
    elif np.issubdtype(data.dtype, np.integer):
        pcm = data.clip(-32768, 32767).astype(np.int16)
    else:
        pcm = (data.astype(np.float32) * 32768.0).clip(-32768, 32767).astype(np.int16)

    return pcm.tobytes()


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
        self._vieneu_tts: object | None = None

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

        # Yield the entire sentence PCM data as one block for clean, gapless playback
        yield pcm_data

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

            chunk_size = piper_sr * 2 * 200 // 1000  # ~200 ms buffer size to prevent jitter
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

    async def _stream_vieneu_cli(self, text: str, voice: str) -> AsyncGenerator[bytes, None]:
        """Stream via VieNeu binary subprocess."""
        if self._model_path is None:
            raise ValueError("VieNeu model_path not set")

        model_path = Path(self._model_path)
        candidates = [
            model_path.parent / "vieneu", model_path.parent / "vieneu.exe",
            Path("vieneu"), Path("vieneu.exe"),
        ]
        binary = next((b for b in candidates if b.exists()), None)

        if binary is None:
            raise FileNotFoundError("VieNeu binary not found")

        import numpy as np
        import soundfile as sf  # type: ignore[import-untyped]

        from app.core.voice_stt_connector import _resample

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = Path(tmp.name)

        try:
            proc = await asyncio.create_subprocess_exec(
                str(binary), "--model", str(model_path),
                "--speaker", voice, "--output", str(tmp_path), "--text", text,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await proc.wait()

            data, sr = sf.read(str(tmp_path), dtype="int16")
            if data.ndim > 1:
                data = data[:, 0]
            if sr != OUTPUT_SAMPLE_RATE:
                f32 = data.astype(np.float32) / 32768.0
                f32 = _resample(f32, sr, OUTPUT_SAMPLE_RATE)
                data = (f32 * 32768.0).clip(-32768, 32767).astype(np.int16)

            yield data.tobytes()
        finally:
            tmp_path.unlink(missing_ok=True)

    async def _stream_vieneu_sdk(self, text: str, voice: str) -> AsyncGenerator[bytes, None]:
        """Stream via the official VieNeu SDK."""
        loop = asyncio.get_event_loop()
        pcm_data = await loop.run_in_executor(None, self._synthesize_vieneu_sync, text, voice)
        if pcm_data:
            yield pcm_data

    async def _stream_vieneu(self, text: str, voice: str) -> AsyncGenerator[bytes, None]:
        """Stream via VieNeu SDK first, then CLI binary, and finally edge-tts as fallback."""
        try:
            async for chunk in self._stream_vieneu_sdk(text, voice):
                yield chunk
            return
        except Exception as sdk_exc:
            logger.debug("[TTS] VieNeu SDK not available or failed: %s. Trying CLI...", sdk_exc)

        try:
            async for chunk in self._stream_vieneu_cli(text, voice):
                yield chunk
            return
        except Exception as cli_exc:
            logger.debug("[TTS] VieNeu CLI not available or failed: %s. Falling back to edge-tts...", cli_exc)

        async for chunk in self._stream_edge(text, "vi-VN-HoaiMyNeural"):
            yield chunk

    def _synthesize_vieneu_sync(self, text: str, voice: str) -> bytes:
        """Blocking VieNeu SDK call, executed in a thread pool by _stream_vieneu."""
        if self._vieneu_tts is None:
            try:
                from vieneu import Vieneu
            except ImportError as exc:
                raise RuntimeError("vieneu SDK is not installed. Run: uv sync") from exc

            logger.info("[TTS] Loading VieNeu SDK backend. First run may download model/codec files.")
            self._vieneu_tts = Vieneu()

        tts = self._vieneu_tts
        selected_voice = self._resolve_vieneu_voice(tts, voice)
        audio = tts.infer(text=text, voice=selected_voice) if selected_voice else tts.infer(text=text)
        sample_rate = int(getattr(tts, "sample_rate", OUTPUT_SAMPLE_RATE))
        return _waveform_to_pcm(audio, sample_rate)

    def _resolve_vieneu_voice(self, tts: object, voice: str) -> str | None:
        requested = (voice or "").strip().strip('"').lower()
        if not requested or not hasattr(tts, "list_preset_voices"):
            return None

        try:
            voices = tts.list_preset_voices()
        except Exception as exc:
            logger.debug("[TTS] Could not list VieNeu voices: %s", exc)
            return None

        for label, voice_id in voices:
            voice_id_s = str(voice_id)
            haystack = f"{label} {voice_id_s}".lower()
            if requested in haystack or voice_id_s.lower() in requested:
                return voice_id_s

        logger.warning("[TTS] VieNeu voice %r not found; using SDK default voice", voice)
        return None
