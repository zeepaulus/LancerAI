"""Centralized application settings.

Loaded from environment variables / .env file via pydantic-settings.
Grouped by domain to keep the project settings navigable.

NOTE:
    This file is the single settings entrypoint. Extend with env-driven fields
    Extend via env-driven fields; scope tracking: ``TODO.md``, package READMEs under ``app/``.
"""

import logging
import threading
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to the project root (two levels up from this file)
_ENV_FILE = Path(__file__).parent.parent.parent / ".env"


class Settings(BaseSettings):
    """Project settings. All fields can be overridden via env vars.

    Sections:
        - Application runtime
        - Auth / organization-scoped data
        - Persistence (PostgreSQL, Redis, Vector DB, Neo4j)
        - LLM (local + cloud fallback)
        - Voice (STT + TTS)
    """

    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), env_file_encoding="utf-8", extra="ignore")

    # --- Application ------------------------------------------------------
    app_env: str = "development"
    app_debug: bool = False  # Enable only for local development; never staging/prod
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    allowed_origins: list[str] = []  # Production: ["https://lancerai.com"]

    # --- Auth / organization-scoped data ----------------------------------
    # tenant_id is server-assigned (= user_id) until invite/organization flow is implemented.
    auth_secret_key: str = Field(...)
    auth_jwt_algorithm: str = "HS256"
    auth_access_token_ttl_minutes: int = 60
    auth_refresh_token_ttl_days: int = 7
    auth_allow_weak_secret: bool = False

    # --- Rate limiting -----------------------------------------------------
    # Only enable when LancerAI sits behind a trusted reverse proxy that sanitizes
    # ``X-Forwarded-For``. Never set True on direct internet-facing instances.
    rate_limit_trust_forwarded_for: bool = False

    @model_validator(mode="after")
    def _validate_secrets(self) -> "Settings":
        if len(self.auth_secret_key) < 32 and not self.auth_allow_weak_secret:
            raise ValueError(
                "AUTH_SECRET_KEY is too short/weak. "
                "Set AUTH_SECRET_KEY to a strong random value (>= 32 chars), or set "
                "AUTH_ALLOW_WEAK_SECRET=true for local dev only."
            )
        if self.auth_allow_weak_secret and self.app_env == "production":
            raise ValueError("AUTH_ALLOW_WEAK_SECRET cannot be enabled in production.")
        return self

    # --- Persistence ------------------------------------------------------
    database_url: str = Field(...)
    database_echo: bool = False
    database_pool_size: int = 20
    database_max_overflow: int = 10

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    vector_db_host: str = "localhost"
    vector_db_port: int = 8001
    vector_db_collection: str = "cv_embeddings"
    vector_db_api_key: str = ""  # Required for Qdrant Cloud / Chroma Cloud
    vector_db_backend: str = "chroma"  # "chroma" or "qdrant"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = Field(...)

    # --- LLM --------------------------------------------------------------
    llm_local_base_url: str = "http://localhost:11434"
    llm_local_model: str = "qwen2.5:3b"
    llm_cloud_api_key: str = ""
    llm_cloud_base_url: str = "https://api.groq.com/openai/v1"
    llm_cloud_model: str = "llama-3.1-70b-versatile"

    # --- Voice ------------------------------------------------------------
    # STT — Faster-Whisper
    stt_model_size: str = "small"                # tiny | base | small | medium
    stt_compute_type: str = "int8"               # int8 | float16 | float32 — int8 for limited VRAM
    stt_language: str = "vi"                     # hardcoded Vietnamese — skip detect step
    stt_device: str = "cpu"                      # cpu | cuda

    # VAD — silero-vad
    vad_silence_threshold_ms: int = 1300         # ms of silence to flush buffer (1.2–1.5s per spec)
    vad_min_speech_duration_ms: int = 200        # min ms of speech to consider a turn

    # TTS
    tts_engine: str = "edge"                     # edge | piper | vieneu
    tts_voice: str = "vi-VN-HoaiMyNeural"        # Edge voice; VieNeu: "Xuân Vĩnh (Nam - Miền Nam)"
    tts_model_path: str = ""                     # VieNeu .gguf model path


_settings_lock = threading.Lock()
_settings_instance: Settings | None = None


def get_settings() -> Settings:
    """Return a process-wide cached Settings instance (thread-safe, lazy)."""
    global _settings_instance
    if _settings_instance is not None:
        return _settings_instance
    with _settings_lock:
        if _settings_instance is None:
            try:
                _settings_instance = Settings()  # type: ignore[call-arg]
            except Exception as e:
                logging.getLogger(__name__).critical(
                    "LancerAI settings invalid — fix environment variables "
                    "(AUTH_SECRET_KEY, APP_ENV, AUTH_ALLOW_WEAK_SECRET, etc.). "
                    "Detail: %s",
                    e,
                )
                raise
        return _settings_instance
