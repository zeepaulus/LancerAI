# LancerAI

**Trợ lý sự nghiệp bằng AI — trích xuất và tối ưu CV, gợi ý việc làm, phỏng vấn giọng nói.**

---

## Giới thiệu

LancerAI là một web application full-stack giúp ứng viên chuẩn bị cho quá trình xin việc thông qua bốn module chính:

- **CV Extraction** — Upload file CV dạng PDF hoặc ảnh; hệ thống dùng OCR để đọc nội dung và cấu trúc hóa thông tin (thông tin cá nhân, kinh nghiệm, kỹ năng, học vấn) bằng LLM.
- **CV Optimization** — Pipeline đa agent AI (LangGraph) phân tích CV, xác định điểm yếu, viết lại theo công thức có cấu trúc, và kiểm tra tính trung thực trước khi xuất kết quả.
- **Job Matching** — Chấm điểm mức độ phù hợp giữa CV và một mô tả công việc (JD) bằng thuật toán Hybrid Scoring (tần suất từ khóa + vị trí xuất hiện + semantic similarity). Xác định các kỹ năng còn thiếu và mức độ ảnh hưởng.
- **Voice Interview** — Phỏng vấn mô phỏng real-time qua WebSocket. Hệ thống lắng nghe ứng viên qua microphone (audio PCM), chuyển giọng nói thành văn bản (STT), tạo câu hỏi/phản hồi bằng LLM, và đọc lại bằng giọng tổng hợp (TTS). Chấm điểm câu trả lời theo framework STAR.

Backend được xây dựng bằng FastAPI (Python), frontend bằng React + Vite.

---

## Tech Stack

| Tầng | Công nghệ |
|---|---|
| API server | FastAPI, Pydantic v2, Uvicorn |
| Database | PostgreSQL, SQLAlchemy 2.0 async, asyncpg |
| Schema migration | Alembic |
| Task queue | Celery + Redis |
| Vector search | ChromaDB (có thể thay bằng Qdrant) |
| Knowledge graph | Neo4j |
| AI orchestration | LangGraph, langchain-core |
| LLM | Ollama (local, mặc định: qwen2.5:3b) / Groq (cloud fallback) |
| OCR | PaddleOCR (tiếng Việt + tiếng Anh) |
| Speech-to-Text | vinai/PhoWhisper-base (HuggingFace Transformers) |
| Text-to-Speech | edge-tts / Piper / VieNeu SDK |
| PDF | PyMuPDF (đọc), WeasyPrint (xuất) |
| Frontend | React 18, Vite 5, react-router-dom 6 |
| Package manager | uv (Python), npm (Node) |
| Testing | pytest |

---

## Trạng thái tính năng

| Module | Tính năng | Trạng thái |
|---|---|---|
| M0 | Đăng ký / đăng nhập (JWT) | Scaffold — chưa implement |
| M0 | Auth middleware (`get_current_user`) | Đã implement (chế độ demo) |
| M1 | Upload CV (PDF / ảnh) | Scaffold — chưa implement |
| M1 | OCR + LLM extraction có cấu trúc | Scaffold — chưa implement |
| M2 | LangGraph CV optimization pipeline | Graph đã wiring — các agent là stub |
| M2 | Render template CV (xuất PDF) | Scaffold — chưa implement |
| M3 | CV-JD matching (Hybrid Scoring) | Scaffold — chưa implement |
| M3 | Gợi ý việc làm từ corpus | Scaffold — chưa implement |
| M4 | Voice interview qua WebSocket | Scaffold — chưa implement |
| M4 | STAR evaluation và báo cáo | Scaffold — chưa implement |
| M5 | Job listing crawler (Celery) | Stub only |
| M5 | PDF/DOCX export worker (Celery) | Stub only |
| Frontend | UI đăng nhập / đăng ký | Chưa bắt đầu |
| Frontend | UI upload và xem CV | Chưa bắt đầu |
| Frontend | UI phỏng vấn (WebSocket + audio) | Chưa bắt đầu |

Danh sách công việc chi tiết kèm file tham chiếu: xem [`TODO.md`](TODO.md).

---

## Yêu cầu hệ thống

- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker + Docker Compose (cho PostgreSQL, Redis, ChromaDB, Neo4j)
- [Ollama](https://ollama.com/) — nếu chạy LLM local

---

## Cài đặt và khởi chạy

### 1. Clone repository

```bash
git clone https://github.com/<org>/lancerai.git
cd lancerai
```

### 2. Cấu hình biến môi trường

```bash
cp .env.example .env
```

Mở `.env` và điền các giá trị cần thiết:

| Biến | Mô tả |
|---|---|
| `DATABASE_URL` | Connection string đến PostgreSQL |
| `AUTH_SECRET_KEY` | Khóa ký JWT — bắt buộc thay đổi trước khi lên production |
| `LLM_LOCAL_BASE_URL` | Địa chỉ Ollama (mặc định: `http://localhost:11434`) |
| `LLM_LOCAL_MODEL` | Tên model Ollama (mặc định: `qwen2.5:3b`) |
| `STT_MODEL_ID` | Model ASR (mặc định: `vinai/PhoWhisper-base`) |
| `TTS_ENGINE` | Engine TTS: `edge`, `piper`, hoặc `vieneu` |

Xem [`.env.example`](.env.example) để biết danh sách đầy đủ.

### 3. Khởi động các dịch vụ hạ tầng

```bash
docker compose up -d
```

Lệnh này khởi động PostgreSQL, Redis, ChromaDB và Neo4j ở background.

### 4. Cài đặt dependencies Python và chạy migration

```bash
uv sync
uv run alembic upgrade head
```

### 5. Khởi động backend

```bash
uv run uvicorn app.main:app --reload --port 8000
```

- API documentation (Swagger UI): http://localhost:8000/docs
- Health check: http://localhost:8000/health

### 6. Khởi động frontend

Mở terminal khác:

```bash
cd frontend
npm install
npm run dev
```

Frontend chạy tại http://localhost:3000.

Tạo file `frontend/.env` với nội dung:

```
VITE_API_BASE_URL=http://localhost:8000
```

### 7. (Tùy chọn) Tải model LLM local

```bash
ollama pull qwen2.5:3b
```

---

## Chạy tests

```bash
uv run pytest
```

Kèm báo cáo coverage:

```bash
uv run pytest --cov=app --cov-report=html
```

---

## Cấu trúc thư mục

```
lancerai/
├── app/                      Backend — FastAPI application
│   ├── main.py               Entry point: khởi tạo app, middleware, mount router
│   ├── core/                 Hạ tầng: settings, DB, connector, DI wiring
│   ├── models/               SQLAlchemy ORM models (định nghĩa bảng PostgreSQL)
│   ├── schema/               Pydantic request/response schemas
│   ├── repository/           Data access layer (PostgreSQL, ChromaDB, Neo4j)
│   ├── router/v1/            Khai báo HTTP endpoint và WebSocket
│   ├── service/              Business logic (service, LangGraph agent, interview pipeline)
│   └── workers/              Celery background tasks
│
├── frontend/                 Frontend — React + Vite SPA
│   └── src/                  Pages, features, components, utils
│
├── docs/                     Tài liệu kiến trúc và tổng quan hệ thống
│   ├── ARCHITECTURE.md       Kiến trúc chi tiết, multi-tenancy, pipeline design
│   └── SYSTEM_OVERVIEW.md    Cách frontend và backend kết nối; mô tả từng tính năng
│
├── migration/                Alembic migration scripts
├── tests/                    Test tự động (pytest)
├── infra/                    Cấu hình hạ tầng
├── docker-compose.yml        Stack dịch vụ local (DB, Redis, ChromaDB, Neo4j)
├── pyproject.toml            Dependencies Python và cấu hình tooling
├── .env.example              Mẫu biến môi trường
├── TODO.md                   Danh sách công việc cần implement
└── CONTRIBUTING.md           Quy trình phát triển, tiêu chuẩn code, hướng dẫn đóng góp
```

Mỗi thư mục con trong `app/` có file `README.md` riêng mô tả chi tiết trách nhiệm, các file bên trong và các quyết định thiết kế.

---

## Tài liệu

| Tài liệu | Mục đích |
|---|---|
| [`docs/SYSTEM_OVERVIEW.md`](docs/SYSTEM_OVERVIEW.md) | Cách hệ thống hoạt động end-to-end; mô tả từng tính năng |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Kiến trúc, multi-tenancy, AI pipeline |
| [`TODO.md`](TODO.md) | Danh sách công việc cần implement theo module |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Quy trình phát triển, tên branch, tiêu chuẩn code |
| `app/*/README.md` | Tài liệu kỹ thuật từng module backend |

---

## Biến môi trường

Xem [`.env.example`](.env.example) để biết danh sách đầy đủ. Các biến được nhóm theo:

- **Application runtime** — `APP_ENV`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`
- **Auth / JWT** — `AUTH_SECRET_KEY`, `AUTH_JWT_ALGORITHM`
- **Database** — `DATABASE_URL`, `REDIS_URL`, `CELERY_BROKER_URL`
- **Vector DB** — `VECTOR_DB_HOST`, `VECTOR_DB_PORT`, `VECTOR_DB_COLLECTION`
- **Graph DB** — `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD`
- **LLM** — `LLM_LOCAL_BASE_URL`, `LLM_LOCAL_MODEL`, `LLM_CLOUD_API_KEY`
- **Voice STT** — `STT_MODEL_ID`, `STT_DEVICE`
- **Voice TTS** — `TTS_ENGINE`, `TTS_VOICE`, `TTS_MODEL_PATH`

---

## License

MIT — xem [LICENSE](LICENSE).
