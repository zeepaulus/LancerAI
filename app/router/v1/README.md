# `router/v1/` — API v1

**FastAPI** — **REST** + **WebSocket** phỏng vấn. Validate bằng Pydantic, gọi service
qua `Depends`; không nhúng logic nghiệp vụ dài.

| Tệp | Prefix | Nội dung |
|-----|--------|----------|
| `auth_api.py` | `/auth` | Đăng ký, đăng nhập, **GET** `/me` |
| `extraction_api.py` | `/extraction` | Upload / đọc **CV** |
| `optimization_api.py` | `/optimization` | Phân tích, template, **PDF** |
| `job_matching_api.py` | `/jobs` | Match **CV**–**JD**, gợi ý |
| `interview_api.py` | `/interview` | Health, session, báo cáo, **WS** |

**Phụ thuộc:** `app/core/dependencies.py`, `app/core/database.py`

```bash
uv run uvicorn app.main:app --reload
curl -s http://localhost:8000/api/v1/interview/health
```
