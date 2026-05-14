# `router/v1/` — API v1

**FastAPI** — **REST** + **WebSocket** phỏng vấn. Validate bằng Pydantic, gọi service
qua `Depends`; không nhúng logic nghiệp vụ dài.

| File | Prefix | Description |
|-----|--------|-------------|
| `auth_api.py` | `/auth` | Signup, login, `GET /me` (real baseline) |
| `extraction_api.py` | `/extraction` | CV upload + fetch (MVP mock) |
| `optimization_api.py` | `/optimization` | CV analysis, template render, PDF (MVP mock / 501) |
| `job_matching_api.py` | `/jobs` | CV–JD matching, job recommendations (MVP mock / 501) |
| `interview_api.py` | `/interview` | Health, session, report, WebSocket voice (MVP mock / stub) |

**Phụ thuộc:** `app/core/providers/`, `app/core/database.py`

```bash
uv run uvicorn app.main:app --reload
curl -s http://localhost:8000/api/v1/interview/health
```
