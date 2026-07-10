# LancerAI

LancerAI là web application hỗ trợ ứng viên chuẩn bị hồ sơ và phỏng vấn: trích xuất CV, tối ưu CV theo vị trí mục tiêu, so khớp CV với Job Description, gợi ý việc làm và luyện phỏng vấn AI qua giọng nói.

Cập nhật tài liệu: 2026-07-10.

## Mục Lục

- [Tổng quan](#tổng-quan)
- [Tính năng hiện tại](#tính-năng-hiện-tại)
- [Tech stack](#tech-stack)
- [Cài đặt nhanh](#cài-đặt-nhanh)
- [Biến môi trường quan trọng](#biến-môi-trường-quan-trọng)
- [API chính](#api-chính)
- [Cấu trúc project](#cấu-trúc-project)
- [Chạy test và quality gate](#chạy-test-và-quality-gate)
- [Docker và triển khai](#docker-và-triển-khai)
- [Ghi chú vận hành](#ghi-chú-vận-hành)
- [Tài liệu liên quan](#tài-liệu-liên-quan)

## Tổng Quan

Project gồm hai phần chính:

- `app/`: backend FastAPI, xử lý auth, upload CV, pipeline AI, matching, phỏng vấn voice, persistence và worker.
- `frontend/`: React SPA, cung cấp luồng đăng nhập, quản lý CV, tối ưu CV, matching việc làm, phỏng vấn và báo cáo.

Luồng hệ thống rút gọn:

```text
Browser
  -> React + Vite SPA
  -> REST API / WebSocket
  -> FastAPI routers
  -> service layer
  -> PostgreSQL / Redis / ChromaDB hoặc Qdrant / Neo4j / LLM / STT / TTS
```

Các module được chia theo milestone:

| Module | Mục tiêu |
|---|---|
| M0 Auth | Đăng ký, đăng nhập, JWT, hồ sơ cá nhân, đổi mật khẩu |
| M1 CV Extraction | Upload PDF/ảnh, đọc text/OCR, LLM trích xuất CV thành JSON |
| M2 CV Optimization | LangGraph pipeline: retrieval -> roast -> rewrite -> audit, chấm điểm CV |
| M3 Job Matching | So khớp CV với JD, crawler job listing, recommendation qua vector search |
| M4 Voice Interview | Tạo phiên phỏng vấn, WebSocket audio, STT, LLM interviewer, TTS, báo cáo STAR |
| M5 Workers | Celery worker cho crawler TopCV và xuất tài liệu PDF/DOCX |

## Tính Năng Hiện Tại

| Nhóm | Trạng thái | Ghi chú |
|---|---|---|
| Auth | Đã implement | Signup/login/me, update profile, đổi mật khẩu, bcrypt, JWT, ownership checks |
| CV upload | Đã implement | PDF text layer bằng PyMuPDF, ảnh/PDF scan qua OCR nếu PaddleOCR có sẵn, giới hạn 10 MB |
| CV extraction | Đã implement | LLM tạo JSON theo schema, retry khi thiếu tên, lưu `CVRecord`, vector embedding best-effort |
| CV history/edit | Đã implement | `GET /extraction/cvs`, `PUT /extraction/cvs/{cv_id}` để user review dữ liệu trích xuất |
| CV optimization | Đã implement | LangGraph multi-agent, deterministic scorecard, lưu `optimized_data`, `audit_score`, `status` |
| Template/PDF | Đã implement | Render JSON template, stream PDF qua WeasyPrint; fallback trả JSON bytes nếu renderer không tạo PDF thật |
| Job matching | Đã implement | Hybrid score: frequency, position, semantic; LLM feedback và fallback deterministic gap |
| Job listings | Đã implement | List/detail job listing từ DB, TopCV crawler worker có parser và embedding best-effort |
| Recommendations | Đã implement | Dựa trên embedding search; trả rỗng nếu vector/embedding chưa sẵn sàng |
| Interview REST | Đã implement | Tạo session, lập kế hoạch câu hỏi từ CV/JD, list report, get report |
| Interview WebSocket | Đã implement | Token first-message, PCM Int16 16 kHz, VAD, STT, LLM streaming, TTS PCM 24 kHz |
| STT/TTS | Đã implement có điều kiện | STT ưu tiên Groq Whisper nếu có key, fallback faster-whisper; TTS Edge/Piper/VieNeu |
| LLM connector | Đã implement | Ollama local, self-hosted OpenAI-compatible, Groq, NVIDIA NIM, streaming và semantic cache |
| Rate limit | Đã implement | SlowAPI theo từng endpoint, có cấu hình trusted forwarded-for |
| Test suite | Đã có | `171/178` tests được collect mặc định sau khi loại integration marker |

## Tech Stack

| Tầng | Công nghệ |
|---|---|
| Backend API | FastAPI, Uvicorn, Pydantic v2 |
| Auth | bcrypt, PyJWT |
| Database | PostgreSQL, SQLAlchemy 2 async, asyncpg |
| Migration | Alembic |
| Worker | Celery, Redis |
| Vector DB | ChromaDB hoặc Qdrant |
| Knowledge graph | Neo4j |
| LLM | Ollama, self-hosted OpenAI-compatible endpoint, Groq, NVIDIA NIM |
| LLM cache | PostgreSQL table `llm_response_cache` với prompt hash và embedding similarity |
| CV/PDF | PyMuPDF, WeasyPrint, python-docx |
| OCR | PaddleOCR lazy-load nếu cài; production Docker hiện loại Paddle để giảm image size |
| STT | Groq Whisper API hoặc faster-whisper local |
| VAD | silero-vad, energy fallback |
| TTS | edge-tts, Piper, VieNeu |
| Frontend | React 18, React Router 6, Vite |
| Testing | pytest, pytest-asyncio, Ruff, mypy |
| Package managers | uv cho Python, npm cho frontend |

## Cài Đặt Nhanh

### 1. Yêu cầu

- Python 3.11+
- uv
- Node.js 22 khuyến nghị cho frontend hiện tại
- Docker và Docker Compose
- Ollama nếu muốn chạy LLM local
- ffmpeg nếu dùng TTS/audio local ngoài Docker

### 2. Clone và tạo env

```bash
git clone https://github.com/zeepaulus/LancerAI.git
cd LancerAI
cp .env.example .env
cp frontend/.env.example frontend/.env
```

Trong local dev, nên chỉnh:

```env
AUTH_SECRET_KEY=<chuoi-random-it-nhat-32-ky-tu>
AUTH_ALLOW_WEAK_SECRET=true
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lancerai
NEO4J_PASSWORD=deochodau123
VECTOR_DB_HOST=http://localhost
VECTOR_DB_PORT=8001
FRONTEND_BASE_URL=http://localhost:3000
```

Nếu dùng file `.env.example` nguyên bản để demo local, `AUTH_ALLOW_WEAK_SECRET=true` cho phép secret yếu. Không dùng cấu hình này ở production.

### 3. Khởi động hạ tầng dev

`docker-compose.yml` chỉ chạy hạ tầng: PostgreSQL, Redis, ChromaDB, Neo4j.

```bash
docker compose up -d
docker compose ps
```

### 4. Backend

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Các URL hữu ích:

- API root: http://localhost:8000/
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

### 5. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend chạy tại http://localhost:3000.

### 6. LLM local tùy chọn

```bash
ollama pull qwen2.5:3b
```

Backend mặc định gọi Ollama tại `http://localhost:11434`. Nếu cấu hình Groq/NVIDIA/self-hosted, các tác vụ nặng có thể ưu tiên cloud theo logic trong `app/core/llm_connector.py`.

### 7. Worker tùy chọn

```bash
uv run celery -A app.workers.celery_app worker --loglevel=info -P threads -c 2
```

Worker hiện dùng cho:

- `crawl_job_listings`: crawl TopCV, lưu job listings và embedding best-effort.
- `generate_document`: xuất CV PDF/DOCX dưới dạng base64.

## Biến Môi Trường Quan Trọng

| Biến | Ý nghĩa |
|---|---|
| `APP_ENV`, `APP_DEBUG` | Môi trường chạy và mức debug |
| `AUTH_SECRET_KEY` | Secret ký JWT, bắt buộc mạnh ở production |
| `AUTH_ALLOW_WEAK_SECRET` | Chỉ bật cho local dev |
| `ALLOWED_ORIGINS` | Danh sách CORS origins cho frontend |
| `FRONTEND_BASE_URL` | Base URL dùng để tạo link phòng phỏng vấn |
| `DATABASE_URL` | PostgreSQL async URL |
| `REDIS_URL` | Redis cho cache/hạ tầng phụ trợ |
| `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND` | Redis DB cho Celery |
| `VECTOR_DB_BACKEND` | `chroma` hoặc `qdrant` |
| `VECTOR_DB_HOST`, `VECTOR_DB_PORT`, `VECTOR_DB_COLLECTION` | Cấu hình vector store |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Knowledge graph |
| `LLM_LOCAL_BASE_URL`, `LLM_LOCAL_MODEL` | Ollama local |
| `LLM_HOSTED_BASE_URL`, `LLM_HOSTED_MODEL` | Endpoint OpenAI-compatible tự host |
| `LLM_CLOUD_API_KEY`, `LLM_CLOUD_BASE_URL`, `LLM_CLOUD_MODEL` | Groq fallback |
| `LLM_NVIDIA_API_KEY`, `LLM_NVIDIA_MODEL` | NVIDIA NIM |
| `LLM_CACHE_ENABLED`, `LLM_CACHE_SIMILARITY_THRESHOLD` | Semantic response cache |
| `STT_MODEL_SIZE`, `STT_MODEL_PATH`, `STT_DEVICE` | faster-whisper local |
| `TTS_ENGINE`, `TTS_VOICE`, `TTS_MODEL_PATH` | Edge/Piper/VieNeu TTS |
| `VAD_SILENCE_THRESHOLD_MS`, `VAD_MIN_SPEECH_DURATION_MS` | Turn detection |
| `VITE_API_BASE_URL` | Frontend gọi backend; để rỗng khi proxy same-origin |

## API Chính

Tất cả endpoint nghiệp vụ dùng prefix `/api/v1`.

| Nhóm | Method | Path | Mô tả |
|---|---|---|---|
| System | GET | `/` | Banner service và danh sách endpoint |
| System | GET | `/health` | Health check nhẹ |
| System | GET | `/ready` | Kiểm tra database `SELECT 1` |
| Auth | POST | `/api/v1/auth/signup` | Tạo tài khoản |
| Auth | POST | `/api/v1/auth/login` | Đăng nhập, trả JWT |
| Auth | GET | `/api/v1/auth/me` | Lấy profile hiện tại |
| Auth | PATCH | `/api/v1/auth/me` | Cập nhật display name |
| Auth | PUT | `/api/v1/auth/password` | Đổi mật khẩu |
| Extraction | GET | `/api/v1/extraction/cvs` | Lịch sử CV của user |
| Extraction | POST | `/api/v1/extraction/cvs` | Upload PDF/PNG/JPEG/WebP |
| Extraction | GET | `/api/v1/extraction/cv/{cv_id}` | Lấy CV đã trích xuất |
| Extraction | PUT | `/api/v1/extraction/cvs/{cv_id}` | Cập nhật dữ liệu CV đã review |
| Optimization | POST | `/api/v1/optimization/cvs/{cv_id}/optimizations` | Chạy pipeline tối ưu CV |
| Optimization | POST | `/api/v1/optimization/cvs/{cv_id}/render` | Render template JSON |
| Optimization | GET | `/api/v1/optimization/cvs/{cv_id}/pdf` | Stream file PDF hoặc JSON fallback |
| Jobs | GET | `/api/v1/jobs/listings` | List job listings active |
| Jobs | GET | `/api/v1/jobs/listings/{job_id}` | Chi tiết job listing |
| Jobs | POST | `/api/v1/jobs/matches` | So khớp CV với JD text hoặc URL |
| Jobs | GET | `/api/v1/jobs/recommendations/{cv_id}` | Gợi ý job qua vector search |
| Interview | GET | `/api/v1/interview/health` | Health riêng module interview |
| Interview | GET | `/api/v1/interview/scrape-jd?url=...` | Crawl và cấu trúc JD qua LLM |
| Interview | POST | `/api/v1/interview/sessions` | Tạo session phỏng vấn |
| Interview | GET | `/api/v1/interview/sessions` | List session/report của user |
| Interview | GET | `/api/v1/interview/sessions/{session_id}/report` | Report STAR và transcript |
| Interview | WS | `/api/v1/interview/ws` | Kênh phỏng vấn voice real-time |

Hầu hết endpoint nghiệp vụ yêu cầu header:

```http
Authorization: Bearer <access_token>
```

WebSocket interview yêu cầu message JSON đầu tiên:

```json
{"token":"<jwt>","session_id":"<session_id>","duration_minutes":5}
```

Sau đó client gửi audio binary PCM Int16 mono 16 kHz, hoặc JSON action như `stop`, `text_answer`, `behavior_event`.

## Cấu Trúc Project

```text
LancerAI_remote_latest/
|-- app/                       Backend FastAPI
|   |-- main.py                App entrypoint, middleware, system endpoints
|   |-- core/                  Settings, DB, connectors, providers, security, rate limit
|   |-- models/                SQLAlchemy ORM models
|   |-- schema/                Pydantic request/response contracts
|   |-- repository/            Relational, vector, graph, LLM cache repositories
|   |-- router/v1/             REST/WebSocket API routers
|   |-- service/               Auth, extraction, optimization, matching, interview logic
|   `-- workers/               Celery app, crawler worker, document worker
|-- frontend/                  React + Vite SPA
|   `-- src/
|       |-- api/               API wrappers
|       |-- pages/             App routes/pages
|       |-- components/        Shared UI components
|       |-- store/             Theme context
|       `-- assets/            Images, icons, lottie assets
|-- migration/                 Alembic migration environment
|-- docs/                      System docs, flow reports, team plan
|-- infra/                     Deployment notes
|-- tests/                     pytest suite
|-- docker-compose.yml         Local infra stack
|-- docker-compose.prod.yml    Production stack with backend/frontend/nginx/worker
|-- Dockerfile                 Multi-stage backend and frontend images
|-- pyproject.toml             Python dependencies and tooling config
|-- frontend/package.json      Frontend dependencies and scripts
`-- README.md
```

## Chạy Test Và Quality Gate

```bash
uv run pytest
uv run pytest -v
uv run pytest -k auth
uv run pytest --collect-only -q
```

Theo cấu hình `pyproject.toml`, integration tests có marker `integration` được loại khỏi lệnh mặc định.

Quality gates:

```bash
uv run ruff check app tests
uv run mypy app tests
cd frontend && npm run build
```

## Docker Và Triển Khai

### Local infra

```bash
docker compose up -d
docker compose down
```

`docker-compose.yml` dành cho dev local và chỉ chạy hạ tầng.

### Production compose

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

`docker-compose.prod.yml` chạy:

- PostgreSQL
- Redis
- ChromaDB
- Neo4j
- Backend FastAPI
- Celery worker
- Frontend static build qua Nginx
- Nginx reverse proxy

Production cần `.env` thật, đặc biệt:

- `APP_ENV=production`
- `APP_DEBUG=false`
- `AUTH_SECRET_KEY` mạnh
- `AUTH_ALLOW_WEAK_SECRET=false`
- `POSTGRES_PASSWORD`
- `NEO4J_AUTH` hoặc `NEO4J_PASSWORD`
- `ALLOWED_ORIGINS`
- API keys LLM nếu không dùng local Ollama

## Ghi Chú Vận Hành

- PaddleOCR không được cài trong production image hiện tại để giảm dung lượng. CV PDF có text layer vẫn đọc bằng PyMuPDF; ảnh hoặc scan cần môi trường có OCR.
- Các flow LLM/STT/TTS phụ thuộc model/API ngoài repo. Nếu Ollama, Groq, NVIDIA, faster-whisper hoặc TTS local chưa sẵn sàng, một số flow sẽ fallback hoặc lỗi theo từng module.
- Recommendations cần job corpus đã crawl và embedding đã lưu trong vector DB.
- Browser microphone/camera yêu cầu HTTPS, trừ localhost.
- `AUTH_SECRET_KEY` ngắn chỉ dùng local khi `AUTH_ALLOW_WEAK_SECRET=true`; production sẽ bị chặn.
- `VECTOR_DB_HOST` nên có scheme `http://localhost` khi dùng Chroma HTTP server để tránh Chroma tạo folder local ngoài ý muốn.
- JD URL fetch có kiểm tra SSRF cơ bản: chỉ cho `http/https`, chặn localhost và IP private/reserved.

## Tài Liệu Liên Quan

| Tài liệu | Nội dung |
|---|---|
| [docs/README.md](docs/README.md) | Mục lục tài liệu project |
| [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md) | Kiến trúc tổng thể và luồng dữ liệu |
| [docs/FLOW_STUDY_CASES.md](docs/FLOW_STUDY_CASES.md) | Study cases, failure modes, backlog ưu tiên |
| [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md) | Báo cáo hiện trạng project |
| [docs/TEAM_PLAN.md](docs/TEAM_PLAN.md) | Phân công và kế hoạch tiếp theo |
| [DESIGN.md](DESIGN.md) | Tổng quan định hướng UI/UX |
| [app/README.md](app/README.md) | Tổng quan backend package |
| [app/router/v1/README.md](app/router/v1/README.md) | API v1 chi tiết |
| [app/service/README.md](app/service/README.md) | Business logic layer |
| [tests/README.md](tests/README.md) | Cấu trúc test suite |
| [migration/README.md](migration/README.md) | Alembic migration |
| [infra/README.md](infra/README.md) | Ghi chú triển khai |
| [TODO.md](TODO.md) | Backlog kỹ thuật |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Quy trình đóng góp |

## License

MIT. Xem [LICENSE](LICENSE).
