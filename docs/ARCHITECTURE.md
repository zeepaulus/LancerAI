# Kiến trúc LancerAI

Tài liệu mô tả phân tầng, ranh giới trách nhiệm và luồng dữ liệu chính (HTTP,
**WebSocket**, worker nền).

## Phân tầng

```
Transport   app/router/v1/     — FastAPI: REST + WebSocket
DTO         app/schema/        — Pydantic request/response
Nghiệp vụ   app/service/       — Luồng tác nghiệp, agent, pipeline
  ├─ agents/                     — LangGraph tối ưu CV
  └─ interview/                  — Pipeline phỏng vấn realtime
Truy cập    app/repository/      — SQL, vector, graph
ORM         app/models/
Hạ tầng     app/core/            — Thiết lập, gắn kết phụ thuộc, LLM/STT/TTS/OCR, bảo mật
Nền         app/workers/         — Celery
```

Phụ thuộc chỉ đi **xuống**: router không gọi **ORM** trực tiếp; repository không
soạn prompt **LLM**. Điểm lắp ghép: `app/core/dependencies.py`.

## Mẫu thiết kế

| Mẫu | Vai trò |
|-----|---------|
| Controller–Service–Repository | Tách test, thay phần triển khai theo môi trường |
| Dependency Injection | Gắn kết phụ thuộc, thay connector/repo bằng mock khi test |
| Singleton (`@lru_cache`) | Connector nặng (LLM, STT, TTS, …) một instance / process |
| Strategy | `VoiceTTSConnector(engine=…)` — đổi engine không đổi caller |
| LangGraph + state | Trạng thái tối ưu CV có vùng append-only |

## Tách dữ liệu theo tổ chức

- `User.tenant_id` là mã tổ chức; mọi truy vấn tài nguyên thuộc người dùng phải
  lọc `user_id` và `tenant_id` phù hợp.
- **JWT** mang `tenant_id` trong claims khi triển khai xong; `get_current_user`
  trả `User` đã xác thực.

## Pipeline phỏng vấn (realtime)

Mic trình duyệt → **PCM** 16kHz → **WebSocket** → **STT** → **LLM** (stream) →
**TTS** (stream) → trả audio về client. Router **WS** mỏng: tạo pipeline, chuyển
sự kiện, lưu kết quả qua service khi có.

## Worker (bất đồng bộ)

Tác vụ dài (crawl **JD**, render **PDF** hàng loạt) — **Celery** + **Redis**,
không chạy trong request đồng bộ.

## Lưu trữ (mục tiêu vận hành)

| Thành phần | Công nghệ | Dùng cho |
|------------|-----------|----------|
| Quan hệ | PostgreSQL + SQLAlchemy async | User, CV, session, job |
| Vector | Chroma / Qdrant | Embedding, RAG |
| Graph | Neo4j | Quan hệ kỹ năng (tuỳ module) |
| Hàng đợi | Redis + Celery | Job nền |

## Vận hành local

- Backend: `uv run uvicorn app.main:app --reload`
- Hạ tầng: `docker compose` (file ở gốc repo), biến môi trường khớp `settings`
