# `app/` — LancerAI Backend Application

Root package của FastAPI application. Đây là entry point duy nhất mà infrastructure (uvicorn, Docker) trỏ vào.

## Responsibilities

- Khởi tạo `FastAPI` instance với metadata (title, version, lifespan hook).
- Mount toàn bộ API routers dưới prefix `/api/v1`.
- Cấu hình `CORSMiddleware` theo môi trường (`debug` → `allow_origins=["*"]`, production → rỗng).
- Phơi bày hai system endpoints không yêu cầu auth: `GET /` (service banner) và `GET /health`.

## Entry Point

| File | Role |
|---|---|
| `main.py` | Tạo `app = FastAPI(...)`, wire middleware, include routers |
| `__init__.py` | Đánh dấu package; re-export `app` object cho uvicorn (`app.main:app`) |

## Dependency Graph (high-level)

```
main.py
  └── core/lifespan.py        (startup / shutdown hooks)
  └── core/settings.py        (env config)
  └── router/v1/
        ├── auth_api.py
        ├── extraction_api.py
        ├── optimization_api.py
        ├── job_matching_api.py
        └── interview_api.py
```

## Sub-packages

| Package | Purpose |
|---|---|
| [`core/`](core/README.md) | Infrastructure primitives: settings, DB, connectors, DI |
| [`models/`](models/README.md) | SQLAlchemy ORM models (PostgreSQL schema) |
| [`schema/`](schema/README.md) | Pydantic request / response schemas |
| [`repository/`](repository/README.md) | Data access layer (relational, vector, graph) |
| [`router/`](router/README.md) | FastAPI routers — HTTP + WebSocket endpoint declarations |
| [`service/`](service/README.md) | Business logic layer: services, agents, pipelines |
| [`workers/`](workers/README.md) | Celery background tasks |

## Technology

- **FastAPI** (ASGI framework) + **Uvicorn** (server)
- **pydantic-settings** for environment-driven config
- **SQLAlchemy 2.0+** async ORM (PostgreSQL via `asyncpg`)
- **LangGraph** for multi-agent CV optimization pipeline
- **Celery** + **Redis** for background task queue
