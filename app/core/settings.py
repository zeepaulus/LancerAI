"""Centralized application settings.

Loaded from environment variables / .env file via pydantic-settings.
Grouped by domain to keep the project settings navigable.

NOTE:
    This file is the single settings entrypoint. Extend with env-driven fields
    as features land; see TODO.md and per-folder READMEs for scope.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Project settings. All fields can be overridden via env vars.

    Sections:
        - Application runtime
        - Auth / organization-scoped data
        - Persistence (PostgreSQL, Redis, Vector DB, Neo4j)
        - LLM (local + cloud fallback)
        - Voice (STT + TTS)
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- Application ------------------------------------------------------
    app_env: str = "development"
    app_debug: bool = True
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # --- Auth / organization-scoped data ----------------------------------
    # TODO: replace demo-user fallback with real JWT auth (see app/service/auth_service.py)
    auth_secret_key: str = "change-me-in-production"
    auth_jwt_algorithm: str = "HS256"
    auth_access_token_ttl_minutes: int = 60 * 24
    demo_user_id: str = "demo-user"
    demo_user_email: str = "demo@lancerai.local"
    demo_user_display_name: str = "Demo User"

    # --- Persistence ------------------------------------------------------
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/lancerai"
    database_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str = "redis://localhost:6379/1"
    celery_result_backend: str = "redis://localhost:6379/2"

    vector_db_host: str = "localhost"
    vector_db_port: int = 8001
    vector_db_collection: str = "cv_embeddings"

    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "your-neo4j-password"

    # --- LLM --------------------------------------------------------------
    llm_local_base_url: str = "http://localhost:11434"
    llm_local_model: str = "qwen2.5:3b"
    llm_cloud_api_key: str = ""
    llm_cloud_base_url: str = "https://api.groq.com/openai/v1"
    llm_cloud_model: str = "llama-3.1-70b-versatile"

    # --- Voice ------------------------------------------------------------
    stt_model_id: str = "vinai/PhoWhisper-base"
    stt_device: str = "cpu"
    tts_engine: str = "edge"  # edge | piper | vieneu
    tts_voice: str = "vi-VN-HoaiMyNeural"
    tts_model_path: str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()


settings = get_settings()
