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
import re
import logging
import subprocess
import tempfile
import typing
from collections.abc import AsyncGenerator
from pathlib import Path

logger = logging.getLogger(__name__)

OUTPUT_SAMPLE_RATE = 24_000  # Hz

# Regex to strip markdown / SSML-unsafe characters that crash edge-tts
_MD_STRIP = re.compile(r"[\*#`~\[\]\(\)\|>]+")
_MULTI_SPACE = re.compile(r"\s{2,}")


def _sanitize_for_tts(text: str) -> str:
    """Remove markdown formatting and special characters that edge-tts cannot handle.

    Edge TTS returns "No audio was received" when the input contains
    markdown bold/italic markers, heading hashes, backticks, etc.
    """
    cleaned = _MD_STRIP.sub(" ", text)
    cleaned = cleaned.replace("\n", " ").replace("\r", " ")
    cleaned = _MULTI_SPACE.sub(" ", cleaned).strip()
    return cleaned


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
        local_timeout_seconds: float = 8.0,
    ) -> None:
        self._engine = engine.lower()
        self._model_path = model_path
        self._voice = voice
        self._speed = speed
        self._local_timeout_seconds = max(1.0, float(local_timeout_seconds or 8.0))
        self._vieneu_tts: object | None = None
        self._vieneu_mode: str | None = None

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
        # Sanitize text to remove markdown/special chars that crash TTS engines
        text = _sanitize_for_tts(text)
        if not text:
            return
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
        try:
            pcm_data = await asyncio.wait_for(
                loop.run_in_executor(None, self._synthesize_vieneu_sync, text, voice),
                timeout=self._local_timeout_seconds,
            )
        except TimeoutError as exc:
            raise TimeoutError(
                f"VieNeu SDK exceeded {self._local_timeout_seconds:.1f}s"
            ) from exc
        if pcm_data:
            yield pcm_data

    async def _stream_vieneu(self, text: str, voice: str) -> AsyncGenerator[bytes, None]:
        """Stream via VieNeu local SDK/CLI without falling back to network TTS."""
        try:
            async for chunk in self._stream_vieneu_sdk(text, voice):
                yield chunk
            return
        except Exception as sdk_exc:
            if self._model_path and Path(self._model_path).suffix.lower() == ".gguf":
                logger.warning("[TTS] Local VieNeu GGUF failed: %s", sdk_exc)
                raise
            logger.debug("[TTS] VieNeu SDK not available or failed: %s. Trying CLI...", sdk_exc)

        try:
            async for chunk in self._stream_vieneu_cli(text, voice):
                yield chunk
            return
        except Exception as cli_exc:
            logger.warning("[TTS] VieNeu CLI not available or failed: %s", cli_exc)
            raise

    def _synthesize_vieneu_sync(self, text: str, voice: str) -> bytes:
        """Blocking VieNeu SDK call, executed in a thread pool by _stream_vieneu."""
        if self._vieneu_tts is None:
            try:
                from vieneu import Vieneu
            except ImportError as exc:
                raise RuntimeError("vieneu SDK is not installed. Run: uv sync") from exc

            if self._model_path and Path(self._model_path).suffix.lower() == ".gguf":
                logger.info("[TTS] Loading local VieNeu GGUF backend: %s", self._model_path)
                self._vieneu_tts = self._load_local_vieneu_gguf(Path(self._model_path))
                self._vieneu_mode = "standard"
            else:
                logger.info("[TTS] Loading VieNeu SDK backend. First run may download model/codec files.")
                self._vieneu_tts = Vieneu()
                self._vieneu_mode = "v3turbo"

        tts = self._vieneu_tts
        selected_voice = self._resolve_vieneu_voice(tts, voice)
        if self._vieneu_mode == "standard" and selected_voice and hasattr(tts, "get_preset_voice"):
            audio = tts.infer(text=text, voice=tts.get_preset_voice(selected_voice))
        else:
            audio = tts.infer(text=text, voice=selected_voice) if selected_voice else tts.infer(text=text)
        sample_rate = int(getattr(tts, "sample_rate", OUTPUT_SAMPLE_RATE))
        return _waveform_to_pcm(audio, sample_rate)

    def _load_local_vieneu_gguf(self, model_path: Path) -> object:
        """Load a local VieNeu v2 GGUF model without Hugging Face lookups."""
        from llama_cpp import Llama
        from vieneu.base import BaseVieneuTTS
        from vieneu.standard import VieNeuTTS
        from vieneu.utils import NeuCodecOnnx

        codec_path = model_path.parent / "codec" / "model.onnx"
        if not codec_path.exists():
            raise FileNotFoundError(f"VieNeu codec not found: {codec_path}")

        tts = VieNeuTTS.__new__(VieNeuTTS)
        BaseVieneuTTS.__init__(tts)
        tts.max_context = 512
        tts.streaming_overlap_frames = 1
        tts.streaming_frames_per_chunk = 25
        tts.streaming_lookforward = 10
        tts.streaming_lookback = 100
        tts.streaming_stride_samples = tts.streaming_frames_per_chunk * tts.hop_length
        tts._is_quantized_model = True
        tts._is_onnx_codec = True
        tts.tokenizer = None
        tts.use_chat_format = False
        tts.default_emotion = "<|emotion_0|>"
        tts.codec = NeuCodecOnnx(str(codec_path))
        tts.backbone = Llama(
            model_path=str(model_path),
            verbose=False,
            n_gpu_layers=0,
            n_ctx=4096,
        )
        tts._load_voices(str(model_path.parent))
        return tts

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
