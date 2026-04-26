"""Core layer: shared AI processors, logging, and infrastructure.

Import core components directly from this package:
    from app.core import get_logger, LLMConnector
"""

from app.core.llm_connector import LLMConnector
from app.core.logger import get_logger
from app.core.ocr_processor import OCRProcessor
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector

__all__ = [
    "get_logger",
    "LLMConnector",
    "OCRProcessor",
    "VoiceSTTConnector",
    "VoiceTTSConnector",
]
