# `core/` — Thiết lập & connector

Tầng hạ tầng dùng chung: **settings** (`.env`), engine **PostgreSQL** async, vòng
đời app, log, **JWT**/băm mật khẩu, và lớp bọc **LLM**, **OCR**, **STT**, **TTS**.
Phần gắn kết phụ thuộc tập trung tại `dependencies.py`.

## Trách nhiệm

- Nạp thiết lập; tạo session **DB**; cung cấp connector cho service
- **Không** chứa logic nghiệp vụ **CV**/matching/**interview** thuần túy (thuộc
  `service/`)

## Tech (tham chiếu)

`pydantic-settings`, `sqlalchemy`+`asyncpg`, `httpx` (khi gọi **LLM**), thư viện
**OCR**/**STT**/**TTS** theo `pyproject.toml`.

## Thiết lập

Biến chính xem [`.env.example`](../../.env.example) và `settings.py`: `DATABASE_URL`,
`LLM_*`, `STT_*`, `TTS_*`, `auth_*`, **Redis**/Celery nếu dùng worker.
