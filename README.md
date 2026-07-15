<p align="center">
  <img src="frontend/src/assets/Logo/lancerai_logo.png" width="132" alt="LancerAI logo" />
</p>

<h1 align="center">LancerAI</h1>

<p align="center">
  <strong>AI career copilot for CV extraction, CV optimization, job matching, and voice interview practice.</strong>
</p>

<p align="center">
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/badge/license-MIT-16A34A?style=for-the-badge"></a>
  <img alt="Python" src="https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white">
  <img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/React-18-149ECA?style=for-the-badge&logo=react&logoColor=white">
  <img alt="Vite" src="https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white">
  <img alt="Docker" src="https://img.shields.io/badge/Docker-ready-2496ED?style=for-the-badge&logo=docker&logoColor=white">
</p>

<p align="center">
  <a href="#-product-overview">Overview</a>
  ·
  <a href="#-features">Features</a>
  ·
  <a href="#-tech-stack--libraries">Tech Stack</a>
  ·
  <a href="#-quick-start">Quick Start</a>
  ·
  <a href="#-api-surface">API</a>
  ·
  <a href="#-documentation">Docs</a>
</p>

---

**Cập nhật tài liệu:** 2026-07-11<br>
**Trạng thái:** project full-stack đã có backend thật, frontend SPA, Docker stack, worker, migration, tests và tài liệu module.

## ✨ Product Overview

LancerAI là web application hỗ trợ ứng viên chuẩn bị hồ sơ và phỏng vấn. Hệ thống cho phép upload CV, trích xuất dữ liệu có cấu trúc, tối ưu CV theo vị trí mục tiêu, so khớp CV với Job Description, gợi ý việc làm và luyện phỏng vấn AI qua giọng nói.

```text
Candidate
  -> Upload CV
  -> Review extracted profile
  -> Optimize CV
  -> Match with JD / job corpus
  -> Practice voice interview
  -> Review report and next actions
```

### Why It Matters

| Giá trị | LancerAI hỗ trợ |
|---|---|
| Chuẩn hóa hồ sơ | Trích xuất CV thành dữ liệu có cấu trúc để review và tái sử dụng |
| Tối ưu theo mục tiêu | Multi-agent pipeline phân tích, rewrite và audit CV theo JD |
| Ra quyết định nhanh | Hybrid matching score giúp ứng viên biết mình hợp vị trí nào |
| Luyện phỏng vấn thực tế | WebSocket voice pipeline với STT, LLM interviewer, TTS và báo cáo STAR |
| Vận hành được | Có Docker, migration, worker, env templates, tests và tài liệu kỹ thuật |

## 🧭 Architecture

```text
Browser
  -> React + Vite SPA
  -> REST API / WebSocket
  -> FastAPI routers
  -> Service layer
  -> Repository / connector layer
  -> PostgreSQL / Redis / ChromaDB or Qdrant / Neo4j / LLM / STT / TTS
```

| Layer | Path | Vai trò |
|---|---|---|
| Frontend | `frontend/` | React SPA cho landing, auth, dashboard, CV, matching, interview và reports |
| API | `app/router/v1/` | REST/WebSocket endpoints, auth guard, rate limit, input validation |
| Services | `app/service/` | Business logic cho auth, extraction, optimization, matching, interview |
| Core | `app/core/` | Settings, DB, security, providers, AI/voice connectors, rate limit |
| Persistence | `app/models/`, `app/repository/` | SQLAlchemy models, relational/vector/graph/cache repositories |
| Workers | `app/workers/` | Celery crawler và document export |
| Migrations | `migration/` | Alembic schema migration |
| Tests | `tests/` | pytest suite cho API, models, services, security và workers |

## ✅ Features

| Module | Status | Highlights |
|---|---:|---|
| 🔐 Auth | Done | Signup/login/me, profile update, password change, bcrypt, JWT, ownership checks |
| 📄 CV Extraction | Done | PDF text extraction, OCR fallback when available, LLM JSON extraction, CV history/edit |
| 🧠 CV Optimization | Done | LangGraph retrieval -> roast -> rewrite -> audit, deterministic scorecard, PDF render |
| 🎯 Job Matching | Done | Frequency, position and semantic scoring, JD URL guard, LLM feedback fallback |
| 💼 Job Recommendations | Done with data dependency | Vector search over crawled job corpus from TopCV worker |
| 🎙️ Voice Interview | Done with runtime dependency | WebSocket audio, VAD, STT, streaming LLM interviewer, TTS, STAR report |
| ⚙️ Workers | Done | Celery tasks for TopCV crawling and PDF/DOCX document generation |
| 🧪 Quality | Active | pytest, Ruff, mypy, GitHub Actions workflow |

## 🧰 Tech Stack & Libraries

### Backend

| Area | Libraries / Tools |
|---|---|
| API | FastAPI, Uvicorn, Pydantic v2, python-multipart |
| Auth & Security | bcrypt, PyJWT, SlowAPI |
| Database | PostgreSQL, SQLAlchemy 2 async, asyncpg, Alembic |
| Background Jobs | Celery, Redis |
| AI Orchestration | LangGraph, LangChain Core, LangChain Community |
| Vector Search | ChromaDB or Qdrant |
| Knowledge Graph | Neo4j |
| LLM Providers | Ollama, self-hosted OpenAI-compatible endpoint, Groq, NVIDIA NIM |
| LLM Cache | PostgreSQL `llm_response_cache` with prompt hash and embedding similarity |
| CV/PDF | PyMuPDF, WeasyPrint, python-docx |
| OCR | PaddleOCR lazy-load when installed; production image currently excludes Paddle to reduce size |
| Voice | faster-whisper, Groq Whisper, silero-vad, edge-tts, Piper, VieNeu |
| Utilities | httpx, BeautifulSoup, Playwright, Scrapy, NumPy, Pillow, soundfile |

### Frontend

| Area | Libraries / Tools |
|---|---|
| UI Runtime | React 18, React DOM |
| Routing | React Router 6 |
| Build Tooling | Vite, `@vitejs/plugin-react` |
| Assets | Local logo, illustrations, SVG icons, Lottie JSON |
| API Layer | `fetch` wrappers with Bearer token handling, timeout and user-facing error sanitizer |

### Infrastructure & QA

| Area | Tools |
|---|---|
| Local Services | Docker Compose: PostgreSQL, Redis, ChromaDB, Neo4j |
| Production Shape | Dockerfile multi-stage build, `docker-compose.prod.yml`, Nginx reverse proxy |
| Python Packaging | uv, `pyproject.toml`, `uv.lock` |
| Frontend Packaging | npm, `package-lock.json` |
| Testing | pytest, pytest-asyncio |
| Code Quality | Ruff, mypy |
| CI | GitHub Actions |

## 🚀 Quick Start

### 1. Requirements

| Tool | Recommended |
|---|---|
| Python | 3.11+ |
| Python package manager | uv |
| Node.js | `^20.19.0` or `>=22.12.0`; Node 22 LTS recommended |
| Container runtime | Docker + Docker Compose |
| Optional local LLM | Ollama |
| Optional voice tooling | ffmpeg for local audio/TTS workflows |

### 2. Clone And Configure

```bash
git clone https://github.com/zeepaulus/LancerAI.git
cd LancerAI
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Recommended local edits in `.env`:

```env
AUTH_SECRET_KEY=<random-string-at-least-32-characters>
AUTH_ALLOW_WEAK_SECRET=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lancerai
NEO4J_PASSWORD=dev-password-change-me
VECTOR_DB_HOST=http://localhost
VECTOR_DB_PORT=8001
FRONTEND_BASE_URL=http://localhost:3000
```

For production, set `AUTH_ALLOW_WEAK_SECRET=false` and use real secrets/API keys.

### 3. Start Local Infrastructure

`docker-compose.yml` starts only supporting services: PostgreSQL, Redis, ChromaDB and Neo4j.

```bash
docker compose up -d
docker compose ps
```

### 4. Start Backend

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Useful backend URLs:

| URL | Purpose |
|---|---|
| http://localhost:8000/ | API service banner |
| http://localhost:8000/docs | Swagger UI |
| http://localhost:8000/health | Lightweight health check |
| http://localhost:8000/ready | Database readiness check |

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000.

### 6. Optional Local LLM

```bash
ollama pull qwen2.5:3b
```

Backend defaults to Ollama at `http://localhost:11434`. Cloud/self-hosted providers can be configured through the `LLM_*` environment variables.

### 7. Optional Worker

```bash
uv run celery -A app.workers.celery_app worker --loglevel=info -P threads -c 2
```

Current worker tasks:

| Task | Purpose |
|---|---|
| `crawl_job_listings` | Crawl TopCV, save job listings and store embeddings best-effort |
| `generate_document` | Export optimized CV as PDF/DOCX payload |

## 🔐 Environment Variables

| Group | Important Variables |
|---|---|
| App | `APP_ENV`, `APP_DEBUG`, `APP_HOST`, `APP_PORT`, `LOG_TO_FILE` |
| Auth | `AUTH_SECRET_KEY`, `AUTH_JWT_ALGORITHM`, `AUTH_ALLOW_WEAK_SECRET` |
| Frontend/CORS | `ALLOWED_ORIGINS`, `FRONTEND_BASE_URL`, `VITE_API_BASE_URL` |
| PostgreSQL | `DATABASE_URL`, `DATABASE_ECHO` |
| Redis/Celery | `REDIS_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` |
| Vector DB | `VECTOR_DB_BACKEND`, `VECTOR_DB_HOST`, `VECTOR_DB_PORT`, `VECTOR_DB_COLLECTION` |
| Neo4j | `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` |
| LLM Local | `LLM_LOCAL_BASE_URL`, `LLM_LOCAL_MODEL` |
| LLM Hosted | `LLM_HOSTED_BASE_URL`, `LLM_HOSTED_API_KEY`, `LLM_HOSTED_MODEL` |
| LLM Cloud | `LLM_CLOUD_API_KEY`, `LLM_CLOUD_BASE_URL`, `LLM_CLOUD_MODEL` |
| NVIDIA NIM | `LLM_NVIDIA_API_KEY`, `LLM_NVIDIA_BASE_URL`, `LLM_NVIDIA_MODEL` |
| Cache | `LLM_CACHE_ENABLED`, `LLM_CACHE_SIMILARITY_THRESHOLD` |
| STT | `STT_MODEL_SIZE`, `STT_MODEL_PATH`, `STT_COMPUTE_TYPE`, `STT_LANGUAGE`, `STT_DEVICE` |
| VAD | `VAD_SILENCE_THRESHOLD_MS`, `VAD_MIN_SPEECH_DURATION_MS` |
| TTS | `TTS_ENGINE`, `TTS_VOICE`, `TTS_LOCAL_TIMEOUT_SECONDS`, `TTS_MODEL_PATH` |

Full examples live in [.env.example](.env.example), [.env.production.example](.env.production.example) and [frontend/.env.example](frontend/.env.example).

## 🔌 API Surface

All business endpoints use the `/api/v1` prefix.

| Group | Method | Path | Purpose |
|---|---|---|---|
| System | GET | `/` | Service banner and endpoint summary |
| System | GET | `/health` | Lightweight health check |
| System | GET | `/ready` | Database readiness check |
| Auth | POST | `/api/v1/auth/signup` | Create account |
| Auth | POST | `/api/v1/auth/login` | Login and return JWT |
| Auth | GET | `/api/v1/auth/me` | Current user profile |
| Auth | PATCH | `/api/v1/auth/me` | Update display name |
| Auth | PUT | `/api/v1/auth/password` | Change password |
| Extraction | POST | `/api/v1/extraction/cvs` | Upload PDF/PNG/JPEG/WebP CV |
| Extraction | GET | `/api/v1/extraction/cvs` | List user CV history |
| Extraction | GET | `/api/v1/extraction/cv/{cv_id}` | Fetch extracted CV |
| Extraction | PUT | `/api/v1/extraction/cvs/{cv_id}` | Save reviewed CV data |
| Optimization | POST | `/api/v1/optimization/cvs/{cv_id}/optimizations` | Run CV optimization pipeline |
| Optimization | POST | `/api/v1/optimization/cvs/{cv_id}/render` | Render CV template JSON |
| Optimization | GET | `/api/v1/optimization/cvs/{cv_id}/pdf` | Stream PDF or JSON fallback |
| Jobs | GET | `/api/v1/jobs/listings` | List active job listings |
| Jobs | GET | `/api/v1/jobs/listings/{job_id}` | Job listing detail |
| Jobs | POST | `/api/v1/jobs/matches` | Match CV with JD text or URL |
| Jobs | GET | `/api/v1/jobs/recommendations/{cv_id}` | Recommend jobs via vector search |
| Interview | GET | `/api/v1/interview/health` | Interview module health |
| Interview | GET | `/api/v1/interview/scrape-jd?url=...` | Crawl and structure JD |
| Interview | POST | `/api/v1/interview/sessions` | Create interview session |
| Interview | GET | `/api/v1/interview/sessions` | List sessions/reports |
| Interview | GET | `/api/v1/interview/sessions/{session_id}/report` | STAR report and transcript |
| Interview | WS | `/api/v1/interview/ws` | Real-time voice interview channel |

Most business endpoints require:

```http
Authorization: Bearer <access_token>
```

The interview WebSocket expects the first message to be JSON:

```json
{"token":"<jwt>","session_id":"<session_id>","duration_minutes":5}
```

After that, the client sends PCM Int16 mono 16 kHz audio bytes or JSON actions such as `stop`, `text_answer` and `behavior_event`.

## 📁 Project Structure

```text
LancerAI_remote_latest/
|-- app/                       FastAPI backend
|   |-- main.py                App entrypoint, middleware, system endpoints
|   |-- core/                  Settings, DB, connectors, providers, security, rate limit
|   |-- models/                SQLAlchemy ORM models
|   |-- schema/                Pydantic request/response contracts
|   |-- repository/            Relational, vector, graph and LLM cache repositories
|   |-- router/v1/             REST/WebSocket API routers
|   |-- service/               Auth, extraction, optimization, matching, interview logic
|   `-- workers/               Celery app, crawler worker, document worker
|-- frontend/                  React + Vite SPA
|   `-- src/
|       |-- api/               API wrappers and paths
|       |-- pages/             App routes/pages
|       |-- components/        Shared UI and layout
|       |-- config/            Env and storage keys
|       |-- store/             Theme context
|       `-- assets/            Logo, illustrations, icons, Lottie assets
|-- migration/                 Alembic migration environment
|-- docs/                      System docs, reports, flow study cases, team plan
|-- infra/                     Deployment notes
|-- tests/                     pytest suite
|-- docker-compose.yml         Local infrastructure stack
|-- docker-compose.prod.yml    Production stack
|-- Dockerfile                 Multi-stage backend/frontend images
|-- pyproject.toml             Python dependencies and tooling config
|-- frontend/package.json      Frontend dependencies and scripts
`-- README.md
```

## 🧪 Quality Gates

Recommended checks before merging:

```bash
uv run pytest
uv run ruff check app tests
uv run mypy app tests
cd frontend && npm run build
```

Useful focused commands:

```bash
uv run pytest -v
uv run pytest -k auth
uv run pytest --collect-only -q
```

Integration tests are marked with `integration` and excluded from the default pytest command through `pyproject.toml`.

## 🧱 Docker & Deployment

### Local Infrastructure

```bash
docker compose up -d
docker compose down
```

This starts only PostgreSQL, Redis, ChromaDB and Neo4j. Run backend/frontend from local shells for development.

### Production Compose

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

Production compose includes:

| Service | Role |
|---|---|
| PostgreSQL | Relational data |
| Redis | Cache and Celery broker/result backend |
| ChromaDB | Default vector database |
| Neo4j | Skill knowledge graph |
| Backend | FastAPI application |
| Celery worker | Background crawler/export jobs |
| Frontend | Static React build |
| Nginx | Reverse proxy |

Production requires a real `.env`, especially strong auth secrets, database passwords, allowed origins and AI provider keys if local models are not used.

## 📚 Documentation

| Document | Best For |
|---|---|
| [docs/README.md](docs/README.md) | Documentation hub and reading path |
| [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) | Architecture, runtime components, major flows |
| [docs/FLOW_STUDY_CASES.md](docs/FLOW_STUDY_CASES.md) | User flows, edge cases and backlog priorities |
| [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) | Current project status, risks and roadmap |
| [docs/TEAM_PLAN.md](docs/TEAM_PLAN.md) | Team plan, responsibilities and quality gates |
| [DESIGN.md](DESIGN.md) | Product UI/UX direction and known UX gaps |
| [app/README.md](app/README.md) | Backend package overview |
| [app/router/v1/README.md](app/router/v1/README.md) | Detailed API v1 notes |
| [app/service/README.md](app/service/README.md) | Business service layer |
| [app/service/optimization/README.md](app/service/optimization/README.md) | CV optimization pipeline |
| [app/service/interview/README.md](app/service/interview/README.md) | Voice interview pipeline |
| [tests/README.md](tests/README.md) | Test suite structure |
| [migration/README.md](migration/README.md) | Alembic migration guide |
| [infra/README.md](infra/README.md) | Deployment notes |
| [TODO.md](TODO.md) | Technical backlog |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow |

## 🛡️ Operational Notes

- PaddleOCR is not installed in the production image by default to reduce image size. PDF files with a text layer still work through PyMuPDF; scanned CVs/images need an OCR-capable environment.
- LLM/STT/TTS flows depend on local models or external APIs. Some paths degrade gracefully, but core AI flows still need at least one configured backend.
- Recommendations require a populated job corpus and saved embeddings.
- Browser microphone/camera access requires HTTPS, except on localhost.
- `AUTH_SECRET_KEY` can be weak only for local demos when `AUTH_ALLOW_WEAK_SECRET=true`; production blocks weak secrets.
- `VECTOR_DB_HOST` should include the scheme, for example `http://localhost`, when using Chroma HTTP server.
- JD URL fetch includes basic SSRF protection: only `http/https`, with localhost and private/reserved IPs blocked.

## 📜 License

MIT. See [LICENSE](LICENSE).
