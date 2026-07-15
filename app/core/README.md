# `app/core/` - Infrastructure, Connectors And Providers

`app/core/` chứa các primitive dùng chung cho backend: settings, database, security, logging, rate limit, lifecycle, DI providers và connectors tới hệ thống AI.

Không đặt product business logic ở đây. Business logic nằm trong `app/service/`.

## Principles

- Settings đọc từ `.env` qua `pydantic-settings`.
- DB access dùng SQLAlchemy async engine và `AsyncSession`.
- Heavy connectors được lazy-load qua providers/singletons.
- Routers nhận service bằng `Depends`; service nhận dependencies qua constructor.
- Security, rate limit và logging là cross-cutting concerns.

## Key Files

| File/Folder | Vai trò |
|---|---|
| `settings.py` | `Settings` model, env validation, cached `get_settings()` |
| `database.py` | Async engine/session factory, `get_db_session` |
| `security.py` | Password hash/verify, JWT create/decode |
| `rate_limit.py` | SlowAPI limiter và IP key function |
| `logger.py` | Console/file logging |
| `lifespan.py` | Startup/shutdown hooks |
| `json_extractor.py` | Clean/parse JSON từ LLM responses |
| `sync_singleton.py` | Thread-safe singleton helper |
| `providers/` | FastAPI dependency factories |
| `llm_connector.py` | Ollama, self-hosted, Groq, NVIDIA NIM, streaming, embeddings, cache hooks |
| `ocr_processor.py` | PaddleOCR lazy-load, grouped text extraction |
| `voice_stt_connector.py` | Groq Whisper fallback, faster-whisper, silero/energy VAD helpers |
| `voice_tts_connector.py` | Edge TTS, Piper, VieNeu, PCM output |

## Providers

| Provider file | Exposes |
|---|---|
| `providers/auth.py` | `get_current_user`, `validate_ws_token` |
| `providers/connectors.py` | LLM, OCR, STT, TTS, vector repo, graph repo |
| `providers/repositories.py` | Repositories for ORM models |
| `providers/services.py` | Auth/extraction/optimization/matching/interview services, renderer, pipeline factory |

## Settings Groups

| Nhóm | Biến tiêu biểu |
|---|---|
| App | `APP_ENV`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`, `ALLOWED_ORIGINS` |
| Auth | `AUTH_SECRET_KEY`, `AUTH_JWT_ALGORITHM`, token TTLs |
| DB/Redis | `DATABASE_URL`, `REDIS_URL`, Celery URLs |
| Vector | `VECTOR_DB_BACKEND`, `VECTOR_DB_HOST`, `VECTOR_DB_PORT`, `VECTOR_DB_COLLECTION` |
| Graph | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` |
| LLM | Ollama, self-hosted, Groq, NVIDIA NIM variables |
| Cache | `LLM_CACHE_ENABLED`, `LLM_CACHE_SIMILARITY_THRESHOLD` |
| Voice | STT, VAD, TTS engine/model/voice variables |

## LLM Routing Summary

- Default local calls use Ollama.
- Cloud-heavy calls can route to self-hosted endpoint, Groq or NVIDIA NIM.
- Streaming is implemented for interview responses.
- Embeddings try Ollama first, then NVIDIA, then OpenAI-compatible endpoint when cloud is requested.
- Semantic cache is optional and stored through `LLMCacheRepository`.

## Voice Contract

| Direction | Format |
|---|---|
| Browser -> backend | PCM Int16 mono 16 kHz |
| Backend -> browser | PCM Int16 mono 24 kHz |

STT skips very short/low-RMS audio before loading a model. TTS sanitizes markdown-like characters before synthesis.
