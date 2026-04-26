"""Voice STT Connector — Vietnamese ASR.

Contract for the voice pipeline: load ``vinai/PhoWhisper-base`` (or a
compatible ASR) and turn raw PCM Int16 mono into text.

TODO:
    - Lazy-load HF Transformers pipeline for the configured model id.
    - Resample inputs to 16 kHz when sample_rate differs.
    - Apply an energy gate to avoid hallucinating on silence.
    - Provide a streaming transcribe path for the websocket pipeline.
"""

from collections.abc import AsyncGenerator

SAMPLE_RATE = 16000


class VoiceSTTConnector:
    """Speech-to-text contract used by ``InterviewPipeline``."""

    def __init__(self, model_id: str = "vinai/PhoWhisper-base", device: str = "cpu") -> None:
        self._model_id = model_id
        self._device = device

    async def transcribe(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> str:
        """Transcribe a PCM Int16 mono buffer to a UTF-8 string."""
        raise NotImplementedError("VoiceSTTConnector.transcribe is not implemented yet.")

    async def stream_transcribe(
        self,
        audio_chunk_generator: AsyncGenerator[bytes, None],
        sample_rate: int = SAMPLE_RATE,
    ) -> AsyncGenerator[str, None]:
        """Yield partial / final transcripts for a stream of audio chunks."""
        raise NotImplementedError("VoiceSTTConnector.stream_transcribe is not implemented yet.")
        if False:  # pragma: no cover
            yield ""
