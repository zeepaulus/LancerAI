# `app/` - LancerAI Backend Application

`app/` là package backend FastAPI của LancerAI. Đây là entrypoint cho API server, WebSocket interview, service layer, persistence và background worker integration.

## Responsibilities

- Khởi tạo `FastAPI` instance trong `main.py`.
- Cấu hình CORS, rate limit middleware, lifespan hook và exception handler.
- Cung cấp system endpoints: `GET /`, `GET /health`, `GET /ready`.
- Mount API v1 routers dưới prefix `/api/v1`.
- Tách rõ các lớp: core, router, service, repository, models, schema, workers.

## Entry Point

| File | Vai trò |
|---|---|
| `main.py` | Tạo `app`, wire middleware, include routers, system health/readiness |
| `__init__.py` | Đánh dấu package |

Run local:

```bash
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## High-Level Dependency Graph

```text
main.py
  -> core/settings.py
  -> core/lifespan.py
  -> core/rate_limit.py
  -> router/v1/*
      -> service/*
          -> repository/*
          -> core connectors
              -> PostgreSQL / Redis / Vector DB / Neo4j / LLM / STT / TTS
```

## Subpackages

| Package | Purpose |
|---|---|
| [`core/`](core/README.md) | Settings, database, providers, security, rate limit, logging, AI connectors |
| [`models/`](models/README.md) | SQLAlchemy ORM models |
| [`schema/`](schema/README.md) | Pydantic request/response contracts |
| [`repository/`](repository/README.md) | Data access layer for relational/vector/graph/cache data |
| [`router/`](router/README.md) | FastAPI route declarations |
| [`service/`](service/README.md) | Business logic by module |
| [`workers/`](workers/README.md) | Celery app and background tasks |

## Mounted Routers

All business routers are included in `main.py` with prefix `/api/v1`.

| Router | Prefix | Module |
|---|---|---|
| `auth_api` | `/auth` | Auth/profile/password |
| `extraction_api` | `/extraction` | CV upload/history/fetch/update |
| `optimization_api` | `/optimization` | CV optimization/template/PDF |
| `job_matching_api` | `/jobs` | Job listings, matching, recommendations |
| `interview_api` | `/interview` | JD scrape, interview sessions, reports, WebSocket |

## Core Technologies

| Area | Libraries |
|---|---|
| API | FastAPI, Uvicorn, Pydantic v2 |
| Auth | bcrypt, PyJWT |
| DB | SQLAlchemy async, asyncpg, PostgreSQL |
| Migration | Alembic |
| Rate limit | SlowAPI |
| Worker | Celery, Redis |
| AI orchestration | LangGraph |
| Vector | ChromaDB, Qdrant |
| Graph | Neo4j async driver |
| Voice | faster-whisper, silero-vad, edge-tts, Piper, VieNeu |
| Documents | PyMuPDF, WeasyPrint, python-docx |

## Notes

- Production requires a strong `AUTH_SECRET_KEY`; weak secrets are blocked unless explicitly allowed in local development.
- `/ready` currently verifies primary database connectivity.
- Heavy connectors are lazy-loaded through providers to reduce startup cost.
