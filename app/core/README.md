# `app/core/` — Infrastructure Primitives

Package chứa toàn bộ cross-cutting concerns của ứng dụng: configuration, database session, external connectors, DI wiring, logging, và security helpers. Không có business logic ở đây.

## Design Principles

- **Singleton connectors**: các tài nguyên nặng (LLM client, ASR model, TTS engine) được khởi tạo một lần duy nhất qua `@lru_cache`, tránh re-init trên mỗi request.
- **Lazy initialization**: engine và model chỉ load khi request đầu tiên yêu cầu — app boot không bị block bởi unavailable backends.
- **Contract-first stubs**: mỗi connector định nghĩa đầy đủ interface trước khi implement để service layer có thể được viết và test độc lập.

## Files

### `settings.py`
Centralized configuration bằng **pydantic-settings**.

- Load từ `.env` file và environment variables (priority: env vars > `.env`).
- Các nhóm config: Application runtime, Auth/JWT, Persistence (PostgreSQL, Redis, Vector DB, Neo4j), LLM (local Ollama + cloud Groq), Voice (STT + TTS).
- Expose singleton `settings` và factory `get_settings()` (dùng với FastAPI `Depends`).

```python
settings.database_url        # postgresql+asyncpg://...
settings.llm_local_model     # qwen2.5:3b
settings.stt_model_id        # vinai/PhoWhisper-base
settings.tts_engine          # edge | piper | vieneu
```

### `database.py`
Async SQLAlchemy engine + session factory.

- Tạo `create_async_engine` với `pool_pre_ping=True` (tự detect broken connections).
- `AsyncSessionLocal` — `async_sessionmaker` với `expire_on_commit=False`.
- `get_db_session()` — FastAPI dependency generator: yield session → commit → rollback on exception.
- **Driver**: `asyncpg` cho PostgreSQL.

### `dependencies.py`
Toàn bộ **Dependency Injection wiring** của ứng dụng theo pattern Controller → Service → Repository.

| Provider | Type | Notes |
|---|---|---|
| `get_llm_connector()` | `@lru_cache` singleton | Wires `LLMConnector` từ settings |
| `get_ocr_processor()` | `@lru_cache` singleton | PaddleOCR stub |
| `get_stt_connector()` | `@lru_cache` singleton | PhoWhisper ASR stub |
| `get_tts_connector()` | `@lru_cache` singleton | Edge/Piper/VieNeu TTS stub |
| `get_vector_repository()` | `@lru_cache` singleton | ChromaDB/Qdrant stub |
| `get_*_repository()` | `@lru_cache` singleton | Generic `RelationalRepository` per model |
| `get_*_service()` | Per-request | Receive injected connectors + repos |
| `get_current_user()` | Per-request | `Authorization: Bearer <jwt>` → `User` |

### `lifespan.py`
FastAPI **lifespan context manager** — startup/shutdown hooks.

- Hiện tại: log env và debug flag.
- Designed để mở rộng: DB connectivity check, connector warm-up, Redis health check.

### `llm_connector.py`
Unified interface cho **Local + Cloud LLM** inference.

| Method | Description |
|---|---|
| `generate(prompt, system, ...)` | One-shot completion |
| `generate_stream(prompt, ...)` | Token streaming (async generator) |
| `generate_chat(messages, ...)` | Chat history completion |
| `generate_chat_stream(messages, ...)` | Streaming chat (dùng cho voice TTS pipeline) |

- **Local backend**: Ollama (`qwen2.5:3b`) via `/api/generate`.
- **Cloud backend**: Groq / OpenAI-compatible (fallback khi `cloud_api_key` được set).
- Tất cả methods hiện là stubs (`NotImplementedError`), interface ổn định cho service layer.

### `voice_stt_connector.py`
Contract cho **Vietnamese ASR** (Speech-to-Text).

- Model: `vinai/PhoWhisper-base` (HuggingFace Transformers pipeline).
- Input: raw PCM Int16 mono buffer @ 16kHz.
- Methods: `transcribe(audio_bytes)` và `stream_transcribe(chunk_generator)` (async generator cho WebSocket).

### `voice_tts_connector.py`
Contract cho **Text-to-Speech** engine.

- Supported engines: `edge` (Microsoft Edge TTS), `piper` (local ONNX), `vieneu` (VieNeu SDK).
- Output: PCM Int16 mono @ 24kHz.
- Methods: `synthesize(text)` → `bytes`; `synthesize_stream(text)` → async generator of PCM chunks.

### `ocr_processor.py`
Contract cho **OCR** (Optical Character Recognition).

- Target stack: **PaddleOCR** với `use_angle_cls=True`, languages `["vi", "en"]`.
- Methods: `extract_text(image_bytes)` → list of `{text, confidence, bbox}`; `extract_text_grouped()` → plain string.
- Dùng bởi `ExtractionService` khi PDF không extract được text trực tiếp.

### `security.py`
Auth primitives — password hashing và JWT helpers.

| Function | Description |
|---|---|
| `hash_password(plain)` | bcrypt/argon2 hashing |
| `verify_password(plain, hashed)` | Constant-time compare |
| `create_access_token(subject, tenant_id, role)` | Sign JWT với claims: sub, tenant_id, role, exp |
| `decode_access_token(token)` | Validate và decode; raise on failure |

### `logger.py`
Production-grade **logging factory**.

- Console handler: UTF-8 output với ANSI color codes (critical cho Vietnamese text trên Windows).
- File handler: `RotatingFileHandler` (10 MB/file, 5 backups), UTF-8 encoding.
- Deduplication: guard set `_INITIALIZED_LOGGERS` tránh duplicate handlers.
- Usage: `logger = get_logger(__name__)` từ bất kỳ module nào.

## Technology

| Component | Library |
|---|---|
| Config | `pydantic-settings` |
| ORM / Async DB | `SQLAlchemy 2.0+`, `asyncpg` |
| LLM inference | `httpx` (Ollama REST), OpenAI-compatible SDK |
| ASR | HuggingFace `transformers` (PhoWhisper) |
| TTS | `edge-tts` / Piper / VieNeu SDK |
| OCR | `paddleocr` |
| Auth | `PyJWT`, `bcrypt` / `argon2-cffi` |
| Logging | Python stdlib `logging` |
