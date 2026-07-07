# LancerAI

**Trợ lý AI — trích xuất và tối ưu CV, gợi ý việc làm, phỏng vấn giọng nói.**

---

## Giới thiệu

LancerAI là web application phục vụ chuẩn bị xin việc qua các module chính:

- **CV Extraction** — Upload CV PDF hoặc ảnh; OCR đọc nội dung, cấu trúc hóa thông tin (cá nhân, kinh nghiệm, kỹ năng, học vấn) bằng LLM.
- **CV Optimization** — Pipeline agent (LangGraph): phân tích CV, chỉ ra điểm yếu, viết lại có cấu trúc, kiểm tra trung thực trước khi xuất.
- **Job Matching** — Hybrid Scoring (tần suất từ khóa, vị trí xuất hiện, semantic similarity) giữa CV và JD; gợi ý kỹ năng thiếu và mức độ ảnh hưởng.
- **Voice Interview** — Phỏng vấn mô phỏng real-time qua WebSocket: PCM microphone → STT → LLM → TTS; chấm điểm theo STAR.

Backend: FastAPI (Python). Frontend: React + Vite.

---

## Tech Stack

| Tầng | Công nghệ |
|---|---|
| API server | FastAPI, Pydantic v2, Uvicorn |
| Database | PostgreSQL, SQLAlchemy 2.0 async, asyncpg |
| Schema migration | Alembic |
| Task queue | Celery + Redis |
| Vector search | ChromaDB hoặc Qdrant (`VECTOR_DB_BACKEND`) |
| Knowledge graph | Neo4j |
| AI orchestration | LangGraph, langchain-core, langchain-community |
| LLM | Ollama (local, mặc định: qwen2.5:3b) / Groq (cloud fallback) |
| OCR | PaddleOCR (tiếng Việt + tiếng Anh) — planned |
| Speech-to-Text | vinai/PhoWhisper-base (HuggingFace Transformers) — planned |
| Text-to-Speech | edge-tts (hiện hoạt động); Piper ONNX, VieNeu — planned |
| PDF | PyMuPDF (đọc), python-docx (xuất); WeasyPrint — planned |
| Frontend | React 18, Vite 5, react-router-dom 6 |
| Package manager | uv (Python), npm (Node) |
| Testing | pytest |

---

## Trạng thái tính năng (MVP Baseline)

| Module | Status | Notes |
|---|---|---|
| Auth (M0) | **Real baseline** | signup/login/me, bcrypt, JWT, ownership checks |
| CV Extraction (M1) | **MVP mock** | Upload validates + persists CVRecord; returns deterministic structured CV |
| CV Optimization (M2) | **MVP mock** | Returns deterministic optimized_data with audit_score |
| Template render (M2) | **MVP mock** | JSON render; PDF endpoint returns 501 (needs WeasyPrint) |
| Job matching (M3) | **MVP mock** | Deterministic scores + skill gap list; recommendations endpoint returns 501 |
| Interview REST (M4) | **MVP mock** | Session create + report with STAR scores (deterministic) |
| Voice WebSocket (M4) | **Stub/planned** | JWT auth validated; audio processing not implemented |
| LLM/OCR/STT/TTS | **Contract only** | NotImplementedError in connector methods |
| Background workers (M5) | **Stub only** | Celery app configured; tasks are stubs |

### MVP MOCK Policy

- Endpoint chính không trả 501 trong happy path — FE có thể gọi và nhận dữ liệu ngay.
- Connector/engine thật (`LLMConnector`, `OCRProcessor`, `VoiceSTTConnector`, `VoiceTTSConnector`) giữ `NotImplementedError`.
- Mock data phải **deterministic**, **đúng schema Pydantic**, và có `TODO` comment rõ.
- **Ownership check** bắt buộc: mọi endpoint dùng `cv_id`/`session_id` phải verify `user_id` match.
- Không có demo bypass public.

---

## Yêu cầu hệ thống

- Python 3.11+
- Node.js 18+
- [uv](https://docs.astral.sh/uv/)
- Docker và Docker Compose
- [Ollama](https://ollama.com/) — khi chạy LLM local

---

## Cài đặt và khởi chạy

### 1. Clone repository

```bash
git clone https://github.com/zeepaulus/LancerAI.git
cd LancerAI
```

### 2. Biến môi trường

```bash
cp .env.example .env
```

Chỉnh `.env` theo môi trường (xem [`.env.example`](.env.example)):

| Biến | Mô tả |
|---|---|
| `DATABASE_URL` | Connection string đến PostgreSQL (bắt buộc) |
| `AUTH_SECRET_KEY` | Khóa ký JWT — thay trước khi đưa lên production (bắt buộc) |
| `NEO4J_PASSWORD` | Mật khẩu Neo4j (bắt buộc) |
| `ALLOWED_ORIGINS` | CORS origins cho frontend (mặc định: localhost:3000,5173) |
| `FRONTEND_BASE_URL` | Public URL của web app để backend tạo link phòng phỏng vấn |
| `LLM_LOCAL_BASE_URL` | Ollama endpoint (mặc định: `http://localhost:11434`) |
| `LLM_LOCAL_MODEL` | Tên model Ollama (mặc định: `qwen2.5:3b`) |
| `LLM_HOSTED_BASE_URL` | Endpoint OpenAI-compatible của LLM bạn tự host trên cloud; được ưu tiên cho tác vụ nặng |
| `LLM_HOSTED_MODEL` | Tên model self-hosted, ví dụ `Qwen/Qwen2.5-14B-Instruct` |
| `VECTOR_DB_HOST` | Dùng `http://localhost` (không phải `localhost`) để tránh tạo folder local |

### 3. Cách 1 — Compose infra + backend/frontend local

`docker-compose.yml` chạy hạ tầng: PostgreSQL, Redis, ChromaDB, Neo4j.

```bash
docker compose up -d
docker compose ps
```

Terminal 1 — backend:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend:

```bash
cd frontend
npm install
npm run dev
```

- API (Swagger): http://localhost:8000/docs
- Frontend (Vite): http://localhost:3000

### 4. LLM local (tùy chọn)

```bash
ollama pull qwen2.5:3b
```

---

## Chạy tests

```bash
uv run pytest
```

Quality gates:

```bash
uv run ruff check app tests     # lint
uv run mypy app tests            # type check
```

---

## Cấu trúc thư mục

```
lancerai/
├── app/                      Backend — FastAPI application
│   ├── main.py               Entry point: app, middleware, router
│   ├── core/                 Settings, DB, connector, DI, security
│   ├── models/               SQLAlchemy ORM
│   ├── schema/               Pydantic request/response
│   ├── repository/           Data access (PostgreSQL, ChromaDB/Qdrant, Neo4j)
│   ├── router/v1/            HTTP / WebSocket endpoints
│   ├── service/              Business logic
│   │   ├── auth/             M0 — Auth (real baseline)
│   │   ├── extraction/       M1 — CV extraction
│   │   ├── optimization/     M2 — CV Intelligence + LangGraph agents
│   │   ├── matching/         M3 — Job matching
│   │   └── interview/        M4 — Interview service + voice pipeline
│   └── workers/              Celery tasks
│
├── frontend/                 React + Vite SPA
├── docs/                     System overview
├── migration/                Alembic
├── tests/                    pytest (123+ tests)
├── Dockerfile                Multi-stage: backend + frontend
├── docker-compose.yml        PostgreSQL, Redis, ChromaDB, Neo4j
├── pyproject.toml
├── uv.lock
├── .env.example
├── TODO.md
└── CONTRIBUTING.md
```

---

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [`docs/SYSTEM_OVERVIEW.md`](docs/SYSTEM_OVERVIEW.md) | Luồng end-to-end, tính năng, cấu hình |
| [`TODO.md`](TODO.md) | Việc cần làm theo module |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branch, commit, PR, chuẩn code |
| `app/*/README.md` | Module backend |

---

## License

MIT — xem [LICENSE](LICENSE).
