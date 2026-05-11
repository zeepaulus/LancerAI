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
| Vector search | ChromaDB |
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
| Frontend | UI đăng nhập / đăng ký | Route có — chưa tích hợp API |
| Frontend | UI upload và xem CV | Chưa có |
| Frontend | UI phỏng vấn (WebSocket + audio) | Chưa có |

Chi tiết công việc và file tham chiếu: [`TODO.md`](TODO.md).

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
| `DATABASE_URL` | Connection string đến PostgreSQL |
| `AUTH_SECRET_KEY` | Khóa ký JWT — thay trước khi đưa lên production |
| `LLM_LOCAL_BASE_URL` | Ollama endpoint (mặc định: `http://localhost:11434`) |
| `LLM_LOCAL_MODEL` | Tên model Ollama (mặc định: `qwen2.5:3b`) |
| `STT_MODEL_ID` | Model ASR (mặc định: `vinai/PhoWhisper-base`) |
| `TTS_ENGINE` | `edge` hoặc `piper` (`piper` cần `TTS_MODEL_PATH`) |

### 3. Cách 1 — Compose infra + backend/frontend local

`docker-compose.yml` hiện chỉ chạy hạ tầng: PostgreSQL, Redis, ChromaDB, Neo4j. Từ host qua `localhost`: Postgres `5432`, Redis `6379`, Chroma host port `8001` → container `8000` ([`.env.example`](.env.example): `VECTOR_DB_PORT=8001`), Neo4j Bolt `7687`.

```bash
docker compose up -d
docker compose ps
```

Terminal 1 — backend, tại thư mục gốc repo:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Terminal 2 — frontend, tại thư mục `frontend/`:

```bash
cd frontend
npm install
npm run dev
```

- API (Swagger): http://localhost:8000/docs  
- Frontend (Vite): http://localhost:3000  

### 4. Cách 2 — Build image backend/frontend rồi chạy container

Chạy hạ tầng trước:

```bash
docker compose up -d
```

Build image từ `Dockerfile`:

```bash
docker build --target backend -t lancerai-backend .
docker build --target frontend -t lancerai-frontend .
```

Tên network compose mặc định của repo này là `lancerai_default`; kiểm tra bằng `docker network ls` nếu cần.

PowerShell:

```powershell
docker rm -f lancerai-backend lancerai-frontend 2>$null

docker run -d --name lancerai-backend --network lancerai_default -p 8000:8000 `
  -e DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/lancerai `
  -e REDIS_URL=redis://redis:6379/0 `
  -e CELERY_BROKER_URL=redis://redis:6379/1 `
  -e CELERY_RESULT_BACKEND=redis://redis:6379/2 `
  -e VECTOR_DB_HOST=chromadb `
  -e VECTOR_DB_PORT=8000 `
  -e NEO4J_URI=bolt://neo4j:7687 `
  -e NEO4J_USER=neo4j `
  -e NEO4J_PASSWORD=your-neo4j-password `
  lancerai-backend

docker exec lancerai-backend uv run --no-sync alembic upgrade head

docker run -d --name lancerai-frontend --network lancerai_default -p 3000:3000 `
  -e VITE_API_BASE_URL=http://localhost:8000 `
  lancerai-frontend
```

Dừng hai container app: `docker stop lancerai-backend lancerai-frontend`. Infra Compose giữ với `docker compose ...` hoặc gỡ stack với `docker compose down`.

### 5. LLM local (tùy chọn)

```bash
ollama pull qwen2.5:3b
```

---

## Chạy tests

```bash
uv run pytest
```

Coverage HTML:

```bash
uv run pytest --cov=app --cov-report=html
```

---

## Cấu trúc thư mục

```
lancerai/
├── app/                      Backend — FastAPI application
│   ├── main.py               Entry point: app, middleware, router
│   ├── core/                 Settings, DB, connector, DI
│   ├── models/               SQLAlchemy ORM
│   ├── schema/               Pydantic request/response
│   ├── repository/           Data access (PostgreSQL, ChromaDB, Neo4j)
│   ├── router/v1/            HTTP / WebSocket
│   ├── service/              Business logic, LangGraph, interview
│   └── workers/              Celery tasks
│
├── frontend/                 React + Vite SPA
│   └── src/                  Pages, components, api, config, assets, utils
│
├── docs/                     Tổng quan hệ thống
│   └── SYSTEM_OVERVIEW.md
│
├── migration/                Alembic
├── tests/                    pytest
├── infra/                    Ghi chú triển khai (Compose ở gốc repo)
├── Dockerfile                Multi-stage: backend + frontend
├── docker-compose.yml        PostgreSQL, Redis, ChromaDB, Neo4j
├── pyproject.toml
├── uv.lock
├── requirements.txt          Export từ lockfile (pip)
├── .env.example
├── TODO.md
└── CONTRIBUTING.md
```

Mỗi thư mục con trong `app/` có `README.md` mô tả phạm vi và thiết kế.

---

## Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [`docs/SYSTEM_OVERVIEW.md`](docs/SYSTEM_OVERVIEW.md) | Luồng end-to-end, tính năng, cấu hình |
| [`infra/README.md`](infra/README.md) | Triển khai Docker Compose, biến môi trường |
| [`TODO.md`](TODO.md) | Việc cần làm theo module |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Branch, commit, PR, chuẩn code |
| `app/*/README.md` | Module backend |

---

## Biến môi trường

Danh sách đầy đủ: [`.env.example`](.env.example). Nhóm chính:

- **Application** — `APP_ENV`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`
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
