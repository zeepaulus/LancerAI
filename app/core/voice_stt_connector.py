"""Voice STT Connector — Vietnamese ASR via faster-whisper + silero-vad.

Architecture (per MVP spec):
    - VAD: silero-vad (PyTorch) — detects speech/silence, flushes buffer after
      ``vad_silence_threshold_ms`` of continuous silence.
    - STT: faster-whisper (CTranslate2) — model ``small``, compute_type ``int8``
      to fit limited VRAM (≤4 GB) on consumer GPUs. Language hardcoded to ``vi``
      to skip language-detection overhead.

Audio contract:
    - Input: PCM Int16 mono, 16 kHz (raw bytes from browser microphone).
    - silero-vad expects float32 at 16 kHz in chunks of 512 samples.
    - faster-whisper expects float32 numpy array at 16 kHz.
"""

from __future__ import annotations

import asyncio
import logging
import typing
from collections.abc import AsyncGenerator

import numpy as np

logger = logging.getLogger(__name__)

SAMPLE_RATE = 16_000  # Hz — input contract
# silero-vad requires 512-sample chunks at 16kHz (= 32 ms per chunk)
VAD_CHUNK_SAMPLES = 512
MIN_TRANSCRIBE_DURATION_SECONDS = 0.25
MIN_TRANSCRIBE_RMS = 0.003


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _pcm_bytes_to_float32(pcm_bytes: bytes) -> np.ndarray:
    """Convert raw PCM Int16 bytes to a float32 numpy array in [-1, 1]."""
    samples = np.frombuffer(pcm_bytes, dtype=np.int16).astype(np.float32)
    samples /= 32768.0
    return samples


def _rms(audio: np.ndarray) -> float:
    if audio.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(audio**2)))


def _resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """Resample audio using torchaudio (high-quality sinc interpolation)."""
    if orig_sr == target_sr:
        return audio
    try:
        import torch
        import torchaudio.functional as ta_functional  # type: ignore[import-untyped]

        tensor = torch.from_numpy(audio).unsqueeze(0)  # (1, T)
        resampled = ta_functional.resample(tensor, orig_sr, target_sr)
        return typing.cast(np.ndarray, resampled.squeeze(0).numpy())
    except ImportError:
        # Fallback: linear interpolation (lower quality, no extra dep)
        ratio = target_sr / orig_sr
        new_len = int(len(audio) * ratio)
        interp_audio = np.interp(
            np.linspace(0, len(audio) - 1, new_len),
            np.arange(len(audio)),
            audio,
        ).astype(np.float32)
        return typing.cast(np.ndarray, interp_audio)


# ---------------------------------------------------------------------------
# VAD Processor
# ---------------------------------------------------------------------------


class _VADProcessor:
    """Wraps silero-vad to detect speech / silence on 512-sample chunks.

    Loaded lazily on first call to avoid paying the torch import cost if
    the connector is constructed but never used in a session.
    """

    def __init__(self, silence_threshold_ms: int = 1300, min_speech_ms: int = 200) -> None:
        self._silence_threshold_ms = silence_threshold_ms
        self._min_speech_ms = min_speech_ms

        self._model: object | None = None
        self._utils: object | None = None

        # State tracking
        self._speech_ms_accumulated: float = 0.0
        self._silence_ms_accumulated: float = 0.0
        self._in_speech: bool = False

    # ms per 512-sample chunk at 16kHz
    _MS_PER_CHUNK: float = (VAD_CHUNK_SAMPLES / SAMPLE_RATE) * 1000

    def _ensure_loaded(self) -> None:
        if self._model is not None:
            return
        # 1. Try local package import first (offline-friendly, avoids Snakers4 download hang/fail)
        try:
            import silero_vad
            model = silero_vad.load_silero_vad(onnx=False)
            self._model = model
            logger.info("[VAD] silero-vad loaded locally from package")
            return
        except Exception as local_exc:
            logger.debug("[VAD] Local silero-vad package load failed: %s. Trying torch.hub...", local_exc)

        # 2. Fallback to torch.hub
        try:
            import torch

            model, utils = torch.hub.load(  # type: ignore[no-untyped-call]
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                onnx=False,
                trust_repo=True,
            )
            self._model = model
            self._utils = utils
            logger.info("[VAD] silero-vad loaded via torch.hub")
        except Exception as exc:
            logger.warning("[VAD] silero-vad unavailable (%s) — falling back to energy-based VAD", exc)
            self._model = None

    def is_speech(self, chunk_float32: np.ndarray) -> bool:
        """Return True if the chunk contains speech."""
        self._ensure_loaded()

        if self._model is None:
            # Energy-based fallback: RMS > threshold
            rms = float(np.sqrt(np.mean(chunk_float32**2)))
            return rms > 0.01  # ~-40 dBFS threshold

        try:
            import torch

            tensor = torch.from_numpy(chunk_float32)
            confidence: float = self._model(tensor, SAMPLE_RATE).item()  # type: ignore[operator]
            return confidence > 0.5
        except Exception:
            rms = float(np.sqrt(np.mean(chunk_float32**2)))
            return rms > 0.01

    def update(self, chunk_float32: np.ndarray) -> bool:
        """Feed one chunk; return True when silence threshold is crossed (= sentence ready)."""
        speech = self.is_speech(chunk_float32)

        if speech:
            self._speech_ms_accumulated += self._MS_PER_CHUNK
            self._silence_ms_accumulated = 0.0
            self._in_speech = True
        else:
            self._silence_ms_accumulated += self._MS_PER_CHUNK

        # Trigger when: we had enough speech AND now enough silence
        if (
            self._in_speech
            and self._speech_ms_accumulated >= self._min_speech_ms
            and self._silence_ms_accumulated >= self._silence_threshold_ms
        ):
            self.reset()
            return True

        return False

    def reset(self) -> None:
        self._speech_ms_accumulated = 0.0
        self._silence_ms_accumulated = 0.0
        self._in_speech = False
        if self._model is not None and hasattr(self._model, "reset_states"):
            try:
                self._model.reset_states()
            except Exception as exc:
                logger.debug("[VAD] Failed to reset model states: %s", exc)


# ---------------------------------------------------------------------------
# Main connector
# ---------------------------------------------------------------------------


class VoiceSTTConnector:
    """Speech-to-text connector using faster-whisper (CTranslate2 engine).

    Provides:
        - ``transcribe``: one-shot transcription of a complete audio buffer.
        - ``stream_transcribe``: async generator that yields text per spoken
          sentence, driven by silero-vad silence detection.

    Args:
        model_size: faster-whisper model size string (``tiny``, ``base``,
            ``small``, ``medium``). ``small`` gives the best speed/accuracy
            tradeoff for Vietnamese on consumer hardware.
        device: ``cpu`` or ``cuda``.
        compute_type: ``int8`` (default, VRAM-friendly), ``float16``, or
            ``float32``.
        language: BCP-47 language code. Hardcoded to ``vi`` per spec to skip
            the language-detection overhead.
        silence_threshold_ms: ms of continuous silence to treat as an
            end-of-utterance boundary. Spec recommends 1 200–1 500 ms.
        min_speech_ms: minimum ms of speech before the buffer is eligible
            to be flushed.
    """

    def __init__(
        self,
        model_size: str = "small",
        device: str = "cpu",
        compute_type: str = "int8",
        language: str = "vi",
        silence_threshold_ms: int = 1300,
        min_speech_ms: int = 200,
    ) -> None:
        self._model_size = model_size
        self._device = device
        self._compute_type = compute_type
        self._language = language

        self._whisper: object | None = None  # WhisperModel — lazy loaded
        self._vad = _VADProcessor(
            silence_threshold_ms=silence_threshold_ms,
            min_speech_ms=min_speech_ms,
        )

    # ------------------------------------------------------------------
    # Lazy model loading
    # ------------------------------------------------------------------

    def _ensure_whisper(self) -> None:
        """Load the faster-whisper WhisperModel on first use."""
        if self._whisper is not None:
            return
        try:
            from faster_whisper import WhisperModel  # type: ignore[import-untyped]

            logger.info(
                "[STT] Loading faster-whisper model=%s device=%s compute=%s",
                self._model_size,
                self._device,
                self._compute_type,
            )
            self._whisper = WhisperModel(
                self._model_size,
                device=self._device,
                compute_type=self._compute_type,
            )
            logger.info("[STT] faster-whisper ready")
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Run: uv add faster-whisper"
            ) from exc

    # ------------------------------------------------------------------
    # Public API — VAD
    # ------------------------------------------------------------------

    def check_vad(self, chunk_float32: np.ndarray) -> bool:
        """Feed one audio chunk to VAD; return True when silence threshold crossed (sentence ready)."""
        return self._vad.update(chunk_float32)

    def reset_vad(self) -> None:
        """Reset VAD accumulated speech/silence counters."""
        self._vad.reset()

    # ------------------------------------------------------------------
    # Public API — Transcription
    # ------------------------------------------------------------------

    async def transcribe(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> str:
        """Transcribe a complete PCM Int16 mono buffer to UTF-8 text.

        The call is offloaded to a thread executor so the async event loop
        is not blocked during inference.

        Args:
            audio_bytes: Raw PCM Int16 mono bytes.
            sample_rate: Sample rate of the incoming audio. Will be
                resampled to 16 kHz if different.

        Returns:
            Stripped transcription string (empty string if nothing detected).
        """
        audio = _pcm_bytes_to_float32(audio_bytes)
        duration_seconds = len(audio) / max(1, sample_rate)
        audio_rms = _rms(audio)
        if duration_seconds < MIN_TRANSCRIBE_DURATION_SECONDS or audio_rms < MIN_TRANSCRIBE_RMS:
            logger.info(
                "[STT] Skipping low-energy audio before model load duration=%.2fs rms=%.5f",
                duration_seconds,
                audio_rms,
            )
            return ""

        self._ensure_whisper()
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_bytes, sample_rate)

    def _transcribe_sync(self, audio_bytes: bytes, sample_rate: int) -> str:
        """Synchronous transcription body — runs in a thread pool."""
        audio = _pcm_bytes_to_float32(audio_bytes)
        if sample_rate != SAMPLE_RATE:
            audio = _resample(audio, sample_rate, SAMPLE_RATE)

        duration_seconds = len(audio) / SAMPLE_RATE
        audio_rms = _rms(audio)
        if duration_seconds < MIN_TRANSCRIBE_DURATION_SECONDS or audio_rms < MIN_TRANSCRIBE_RMS:
            logger.info(
                "[STT] Skipping low-energy audio duration=%.2fs rms=%.5f",
                duration_seconds,
                audio_rms,
            )
            return ""

        segments, _ = self._whisper.transcribe(  # type: ignore[union-attr]
            audio,
            language=self._language,
            beam_size=5,
            vad_filter=False,  # We handle VAD ourselves
            condition_on_previous_text=False,
            no_speech_threshold=0.6,
        )
        text = " ".join(seg.text for seg in segments).strip()
        return text

    async def stream_transcribe(
        self,
        audio_chunk_generator: AsyncGenerator[bytes, None],
        sample_rate: int = SAMPLE_RATE,
    ) -> AsyncGenerator[str, None]:
        """Yield per-sentence transcripts from a continuous audio stream.

        VAD (silero-vad) analyses each 512-sample chunk. When silence exceeds
        ``silence_threshold_ms`` after sufficient speech, the accumulated buffer
        is flushed through faster-whisper and the text is yielded.

        Args:
            audio_chunk_generator: Async generator yielding raw PCM Int16 bytes.
            sample_rate: Sample rate of incoming chunks.

        Yields:
            Transcribed sentences as they are completed.
        """
        self._ensure_whisper()
        self._vad.reset()

        # Rolling PCM buffer (float32) for a single utterance
        speech_buffer: list[np.ndarray] = []
        # Leftover bytes from misaligned chunks (not a multiple of VAD_CHUNK_SAMPLES)
        leftover = np.array([], dtype=np.float32)

        async def _flush(buf: list[np.ndarray]) -> str:
            if not buf:
                return ""
            combined = np.concatenate(buf)
            pcm_int16 = (combined * 32768.0).clip(-32768, 32767).astype(np.int16).tobytes()
            return await self.transcribe(pcm_int16, sample_rate=SAMPLE_RATE)

        async for raw_chunk in audio_chunk_generator:
            chunk_f32 = _pcm_bytes_to_float32(raw_chunk)
            if sample_rate != SAMPLE_RATE:
                chunk_f32 = _resample(chunk_f32, sample_rate, SAMPLE_RATE)

            # Prepend leftover samples
            if len(leftover):
                chunk_f32 = np.concatenate([leftover, chunk_f32])

            # Process in VAD_CHUNK_SAMPLES windows
            offset = 0
            while offset + VAD_CHUNK_SAMPLES <= len(chunk_f32):
                window = chunk_f32[offset : offset + VAD_CHUNK_SAMPLES]
                offset += VAD_CHUNK_SAMPLES

                # Always accumulate the window into the speech buffer
                speech_buffer.append(window)

                if self._vad.update(window):
                    # Sentence boundary detected — flush and yield
                    text = await _flush(speech_buffer)
                    speech_buffer = []
                    if text:
                        yield text

            leftover = chunk_f32[offset:]

        # Generator exhausted — flush remaining audio
        if speech_buffer:
            text = await _flush(speech_buffer)
            if text:
                yield text

        return  # explicit return to satisfy type checker
