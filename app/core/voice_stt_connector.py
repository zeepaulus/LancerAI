"""Voice STT Connector — Vietnamese ASR.

Contract for the voice pipeline: load ``vinai/PhoWhisper-base`` (or a
compatible ASR) and turn raw PCM Int16 mono into text.

TODO:
    - Lazy Loading: Initialize the HuggingFace `pipeline` (e.g. `automatic-speech-recognition`)
      on the first method call. Cache the model in memory to avoid repeated loading overhead.
    - Audio Resampling: Use `librosa` or `torchaudio` to resample `audio_bytes` to
      `16000` Hz if `sample_rate` differs.
    - VAD / Energy Gating: Implement Voice Activity Detection (VAD) or a simple RMS
      energy threshold to drop silent chunks, preventing the Whisper model from hallucinating.
    - Streaming: Implement a robust buffering mechanism in `stream_transcribe` that
      aggregates chunks until a natural pause is detected before running inference.
"""

from collections.abc import AsyncGenerator

SAMPLE_RATE = 16000


class VoiceSTTConnector:
    """Speech-to-text contract used by ``InterviewPipeline``."""

    def __init__(self, model_id: str = "vinai/PhoWhisper-base", device: str = "cpu") -> None:
        self._model_id = model_id
        self._device = device

    async def transcribe(self, audio_bytes: bytes, sample_rate: int = SAMPLE_RATE) -> str:
        """Transcribe a PCM Int16 mono buffer to a UTF-8 string.

        TODO:
            - Decode `audio_bytes` into a float32 NumPy array (normalized between -1.0 and 1.0).
            - Resample the array to 16kHz if `sample_rate != SAMPLE_RATE`.
            - Pass the array into the `pipeline()` to generate the transcription.
            - Return the stripped text.
        """
        raise NotImplementedError("VoiceSTTConnector.transcribe is not implemented yet.")

    async def stream_transcribe(
        self,
        audio_chunk_generator: AsyncGenerator[bytes, None],
        sample_rate: int = SAMPLE_RATE,
    ) -> AsyncGenerator[str, None]:
        """Yield partial / final transcripts for a stream of audio chunks.

        TODO:
            - Create an internal sliding buffer.
            - As chunks arrive from `audio_chunk_generator`, append them to the buffer.
            - Periodically execute VAD. When a speech pause is detected, decode the buffer,
              run inference, and yield the text.
            - Flush any remaining audio in the buffer when the generator is exhausted.
        """
        raise NotImplementedError("VoiceSTTConnector.stream_transcribe is not implemented yet.")
        if False:  # pragma: no cover
            yield ""
