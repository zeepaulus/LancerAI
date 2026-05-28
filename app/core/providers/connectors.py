"""Singleton connector providers — injected by FastAPI DI."""

from __future__ import annotations

from pathlib import Path

from app.core.llm_connector import LLMConnector
from app.core.ocr_processor import OCRProcessor
from app.core.settings import get_settings
from app.core.sync_singleton import thread_safe_singleton
from app.core.voice_stt_connector import VoiceSTTConnector
from app.core.voice_tts_connector import VoiceTTSConnector
from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.graph_repository import GraphRepository
from app.repository.vector_repository import create_vector_repository


def _create_llm_connector() -> LLMConnector:
    s = get_settings()
    return LLMConnector(
        local_base_url=s.llm_local_base_url,
        local_model=s.llm_local_model,
        cloud_base_url=s.llm_cloud_base_url,
        cloud_api_key=s.llm_cloud_api_key,
        cloud_model=s.llm_cloud_model,
        nvidia_base_url=s.llm_nvidia_base_url,
        nvidia_api_key=s.llm_nvidia_api_key,
        nvidia_model=s.llm_nvidia_model,
        nvidia_max_tokens=s.llm_nvidia_max_tokens,
        nvidia_enable_thinking=s.llm_nvidia_enable_thinking,
    )


def _create_ocr_processor() -> OCRProcessor:
    return OCRProcessor()


def _create_stt_connector() -> VoiceSTTConnector:
    s = get_settings()
    return VoiceSTTConnector(
        model_size=s.stt_model_size,
        device=s.stt_device,
        compute_type=s.stt_compute_type,
        language=s.stt_language,
        silence_threshold_ms=s.vad_silence_threshold_ms,
        min_speech_ms=s.vad_min_speech_duration_ms,
    )


def _create_tts_connector() -> VoiceTTSConnector:
    s = get_settings()
    mp = Path(s.tts_model_path) if s.tts_model_path else None
    return VoiceTTSConnector(engine=s.tts_engine, model_path=mp, voice=s.tts_voice)


def _create_vector_repository() -> BaseVectorRepository:
    s = get_settings()
    return create_vector_repository(
        host=s.vector_db_host,
        port=s.vector_db_port,
        collection_name=s.vector_db_collection,
        api_key=s.vector_db_api_key,
        backend=s.vector_db_backend,
    )


def _create_graph_repository() -> GraphRepository:
    s = get_settings()
    return GraphRepository(uri=s.neo4j_uri, user=s.neo4j_user, password=s.neo4j_password)


get_llm_connector = thread_safe_singleton(_create_llm_connector)
get_ocr_processor = thread_safe_singleton(_create_ocr_processor)
get_stt_connector = thread_safe_singleton(_create_stt_connector)
get_tts_connector = thread_safe_singleton(_create_tts_connector)
get_vector_repository = thread_safe_singleton(_create_vector_repository)
get_graph_repository = thread_safe_singleton(_create_graph_repository)
