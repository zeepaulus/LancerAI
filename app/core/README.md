Config, DB session, external service connectors, DI providers, logging, and security primitives. No product business logic here.

## Principles

- Heavy connectors (LLM, ASR, TTS, vector DB) use **lazy initialization** via thread-safe singletons (`app/core/sync_singleton.py`), exposed through providers in `app/core/providers/`.
- Connector methods are **connector contracts** (`raise NotImplementedError`) until a real implementation is wired. Do not call them directly; always inject via `Depends`.
- FastAPI `Depends` wires repositories and services at `app/core/providers/services.py` (including `get_interview_pipeline_factory`).

## File

### `settings.py`
`pydantic-settings`: `.env` + biến môi trường. `get_settings()` cache một bản `Settings` trong process (khóa thread-safe).

### `database.py`
Engine async SQLAlchemy + `get_db_session`.

### `providers/`
- `providers/connectors.py` — `get_llm_connector`, `get_ocr_processor`, STT/TTS, vector, graph.
- `providers/repositories.py` — `get_*_repository` cho từng model.
- `providers/services.py` — `get_*_service`, `get_template_renderer`, `get_interview_pipeline_factory`.
- `providers/auth.py` — `get_current_user`.

### `lifespan.py`
Startup: kiểm tra DB, warm-up vector repository (best-effort).

### `llm_connector.py`
Ollama / OpenAI-compatible — method hiện stub.

### `voice_stt_connector.py` / `voice_tts_connector.py`
STT/TTS — stub.

### `ocr_processor.py`
OCRProcessor — Đã được implement với PaddleOCR.
- **Lazy Initialization:** PaddleOCR engine chỉ được khởi tạo khi có lời gọi method đầu tiên (`_get_ocr_engine`) nhằm giảm thời gian startup và tiết kiệm bộ nhớ cho các luồng không dùng OCR.
- **Method `extract_text`:** Nhận image bytes, trả về danh sách các block text kèm bounding box và độ tin cậy.
- **Method `extract_text_grouped`:** Áp dụng logic gom nhóm theo không gian (spatial sorting: trên xuống, trái sang phải) để nối kết quả thành một string liền mạch theo đúng thứ tự đọc (reading order).

### `security.py`
bcrypt hash/verify; JWT encode/decode (`HS256`, secret từ settings).

### `logger.py`
Console UTF-8; file xoay vòng nếu `LOG_TO_FILE` không tắt. Thư mục: `LOG_DIR` hoặc `<project>/logs`.

### `sync_singleton.py`
Helper `thread_safe_singleton(factory)` cho getter sync.

## Công nghệ

| Thành phần | Gói |
|------------|-----|
| Config | pydantic-settings |
| ORM / DB | SQLAlchemy 2, asyncpg |
| Auth | PyJWT, bcrypt |
| Logging | stdlib `logging` |
