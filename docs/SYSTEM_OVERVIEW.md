# LancerAI System Overview

Tài liệu này mô tả kiến trúc tổng thể của LancerAI, cách frontend và backend giao tiếp, các lớp trong backend, các service bên ngoài và luồng dữ liệu chính.

Cập nhật: 2026-07-10.

## 1. Tổng Quan

LancerAI là hệ thống hỗ trợ ứng viên chuẩn bị ứng tuyển, gồm:

- `frontend/`: React + Vite SPA, chạy UI cho candidate.
- `app/`: FastAPI backend, xử lý API, WebSocket, business logic, database và connector AI.
- `migration/`: Alembic migration cho PostgreSQL.
- `workers/`: Celery tasks cho crawler job và export document.
- `docs/`, `app/*/README.md`: tài liệu kiến trúc và vận hành.

Sơ đồ tổng quát:

```text
Browser
  -> React SPA
  -> REST API / WebSocket
  -> FastAPI app
  -> Router layer
  -> Service layer
  -> Repository / Connector layer
  -> PostgreSQL / Redis / Vector DB / Neo4j / LLM / STT / TTS
```

## 2. Runtime Components

| Thành phần | Vai trò | Local default |
|---|---|---|
| Frontend | React SPA | `http://localhost:3000` |
| Backend | FastAPI API server | `http://localhost:8000` |
| PostgreSQL | User, CV, interview, job, cache data | `localhost:5432` |
| Redis | Celery broker/result backend | `localhost:6379` |
| ChromaDB | Vector search mặc định | `localhost:8001` |
| Qdrant | Vector backend thay thế | Theo `VECTOR_DB_BACKEND=qdrant` |
| Neo4j | Skill knowledge graph | `localhost:7687` |
| Ollama | LLM local | `localhost:11434` |
| Celery worker | Background jobs | Chạy riêng |

## 3. Backend Layering

Backend dùng các lớp rõ ràng:

```text
router/v1
  -> service
  -> repository / core connector
  -> database / vector DB / graph DB / external AI
```

| Layer | Thư mục | Trách nhiệm |
|---|---|---|
| App entry | `app/main.py` | FastAPI instance, middleware, system endpoints, include routers |
| Core | `app/core/` | Settings, DB session, security, rate limit, logging, connectors, DI providers |
| Router | `app/router/v1/` | Nhận request, validate input, auth/rate limit, gọi service |
| Service | `app/service/` | Business logic theo module |
| Repository | `app/repository/` | Data access cho PostgreSQL, vector DB, Neo4j, LLM cache |
| Models | `app/models/` | SQLAlchemy ORM tables |
| Schema | `app/schema/` | Pydantic request/response contracts |
| Workers | `app/workers/` | Celery app và background tasks |

Nguyên tắc:

- Router không chứa business logic dài.
- Service không phụ thuộc trực tiếp vào FastAPI `Depends`.
- Repository nhận `AsyncSession` theo method, transaction boundary nằm ở service/router.
- Connector nặng được lazy-load và inject qua `app/core/providers/`.
- Endpoint dùng `cv_id`, `session_id`, `job_id` phải kiểm tra ownership/user scope.

## 4. Frontend Organization

Frontend đặt trong `frontend/src`.

| Khu vực | Vai trò |
|---|---|
| `App.jsx` | React Router routes |
| `api/` | Wrapper REST API, token attach, timeout và error sanitizer |
| `pages/` | Landing, auth, dashboard, CV upload/review/optimization, matching, interview, reports |
| `components/` | Shared UI components và layout |
| `config/` | API base URL, storage keys |
| `store/` | Theme context |
| `assets/` | Logo, illustrations, icons, lottie |

Routes public:

- `/`
- `/login`
- `/signup`
- `/about`

Routes cần auth:

- `/dashboard`
- `/candidate`
- `/profile`
- `/settings`
- `/cv-upload`
- `/cv-extraction-result`
- `/cv-optimization`
- `/cv-review`
- `/job-matching`
- `/job-recommendations`
- `/interview`
- `/interview-report`
- `/question-bank`
- `/reports`
- `/chat`

## 5. Main Flows

### 5.1 Auth

```text
AuthPage
  -> POST /api/v1/auth/signup hoặc /login
  -> AuthService
  -> bcrypt password hash/verify
  -> JWT access token
  -> localStorage token
  -> Authorization: Bearer <token>
```

Endpoints:

- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `PUT /api/v1/auth/password`

### 5.2 CV Extraction

```text
CVUploadPage
  -> POST /api/v1/extraction/cvs
  -> content-type + 10 MB validation
  -> PyMuPDF text extraction for PDF
  -> OCR fallback for scanned page/image if OCR is available
  -> LLM JSON extraction
  -> CVRecord in PostgreSQL
  -> embedding best-effort into ChromaDB/Qdrant
  -> CVExtractionResponse
```

Supporting endpoints:

- `GET /api/v1/extraction/cvs`: CV history.
- `GET /api/v1/extraction/cv/{cv_id}`: full extracted CV.
- `PUT /api/v1/extraction/cvs/{cv_id}`: save user-reviewed extraction.

### 5.3 CV Optimization

```text
POST /api/v1/optimization/cvs/{cv_id}/optimizations
  -> ownership check
  -> OptimizationService
  -> LangGraph: retrieval -> roast -> rewrite -> audit
  -> deterministic scorecard
  -> update CVRecord.optimized_data, audit_score, status
  -> CVOptimizationResponse
```

Template/PDF:

- `POST /api/v1/optimization/cvs/{cv_id}/render`
- `GET /api/v1/optimization/cvs/{cv_id}/pdf?template=harvard`

### 5.4 Job Matching

```text
POST /api/v1/jobs/matches
  -> ownership check CV
  -> JD text direct hoặc fetch URL an toàn
  -> frequency score
  -> position score
  -> semantic embedding score
  -> LLM missing skills feedback
  -> graph-related skill adjustment best-effort
  -> persist JobMatchResult
```

Weights:

```text
overall = 0.20 * frequency + 0.30 * position + 0.50 * semantic
```

Nếu embedding unavailable, semantic score được loại khỏi tổng và điểm được renormalize theo các component deterministic.

Job listing endpoints:

- `GET /api/v1/jobs/listings`
- `GET /api/v1/jobs/listings/{job_id}`
- `GET /api/v1/jobs/recommendations/{cv_id}`

### 5.5 Interview Voice

REST setup:

```text
POST /api/v1/interview/sessions
  -> ownership check CV
  -> optional JD: text, URL, hoặc job_listing_id
  -> infer/normalize job title
  -> build interview plan
  -> create InterviewSession
  -> return session_id + meeting_url + plan
```

WebSocket:

```text
Client opens /api/v1/interview/ws
  -> first JSON: {"token":"...","session_id":"...","duration_minutes":5}
  -> server validates JWT and session ownership
  -> pipeline.start()
  -> client sends PCM Int16 mono 16 kHz bytes
  -> VAD detects turn boundary
  -> STT transcribes
  -> LLM evaluates/responds
  -> TTS sends PCM 24 kHz bytes
  -> stop persists STAR scores, behavior observations, transcript
```

Report endpoints:

- `GET /api/v1/interview/sessions`
- `GET /api/v1/interview/sessions/{session_id}/report`

## 6. Persistence Model

Core tables:

| Table | Model | Nội dung |
|---|---|---|
| `users` | `User` | Account, tenant boundary, role, password hash |
| `cv_records` | `CVRecord` | Raw/extracted/optimized CV data, score, status |
| `job_listings` | `JobListing` | Crawled job data |
| `job_match_results` | `JobMatchResult` | Match scores, missing skills, workflow status |
| `interview_sessions` | `InterviewSession` | Interview setup, status, STAR/report summary |
| `interview_transcripts` | `InterviewTranscript` | Turn-level transcript |
| `llm_response_cache` | `LLMResponseCache` | Semantic cache for LLM responses |

## 7. External AI Routing

LLM connector priority:

- Local Ollama for default local calls.
- Self-hosted OpenAI-compatible endpoint when configured.
- Groq cloud when `LLM_CLOUD_API_KEY` is real.
- NVIDIA NIM when `LLM_NVIDIA_API_KEY` is real.
- Fallback chain depends on `use_cloud`/`use_nvidia`.

Embedding priority:

- Ollama `/api/embeddings`.
- NVIDIA embedding endpoint if key exists.
- OpenAI-compatible embedding endpoint when cloud is requested.

STT:

- Groq Whisper API first if API key exists.
- faster-whisper local fallback.

TTS:

- `edge`: Microsoft Edge TTS.
- `piper`: local Piper CLI/model, fallback to Edge if missing.
- `vieneu`: local VieNeu SDK/CLI/GGUF; GGUF failures raise rather than silently using network TTS.

## 8. Security And Reliability Notes

- JWT is required for business endpoints; WebSocket validates token in the first message.
- `AUTH_SECRET_KEY` must be strong in production.
- Rate limit uses SlowAPI.
- `RATE_LIMIT_TRUST_FORWARDED_FOR` must stay false unless behind a trusted proxy.
- JD URL fetching blocks localhost/private/reserved IPs to reduce SSRF risk.
- File upload validates content type and size; magic-byte validation is still a recommended hardening item.
- Vector, graph, OCR, LLM and TTS failures are often treated as non-fatal where possible, but core AI flows can still fail if no backend is available.

## 9. Deployment Shape

Local dev:

```text
docker-compose.yml
  -> postgres, redis, chromadb, neo4j

local shell
  -> uvicorn backend
  -> Vite frontend
  -> optional Celery worker
```

Production compose:

```text
docker-compose.prod.yml
  -> postgres
  -> redis
  -> chromadb
  -> neo4j
  -> backend
  -> celery_worker
  -> frontend-prod
  -> nginx
```

## 10. References

- [../README.md](../README.md)
- [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md)
- [PROJECT_REPORT.md](PROJECT_REPORT.md)
- [TEAM_PLAN.md](TEAM_PLAN.md)
- [../app/README.md](../app/README.md)
- [../app/router/v1/README.md](../app/router/v1/README.md)
- [../app/service/README.md](../app/service/README.md)
