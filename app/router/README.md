# `app/router/` — API Route Declarations

Package chứa FastAPI routers — điểm tiếp nhận HTTP requests và WebSocket connections. Routers có trách nhiệm duy nhất: validate input, delegate đến service layer, và serialize response. Không có business logic ở đây.

## Structure

```
router/
├── __init__.py       # Re-export routers; mount vào main.py
└── v1/               # API version namespace
    ├── __init__.py
    ├── auth_api.py
    ├── extraction_api.py
    ├── interview_api.py
    ├── job_matching_api.py
    └── optimization_api.py
```

Tất cả routers được mount với prefix `/api/v1` trong `main.py`. Versioning nằm ở directory level — khi cần `/api/v2`, chỉ cần thêm `v2/` mà không ảnh hưởng v1.

---

## `v1/` — Version 1 Endpoints

### `auth_api.py` — `/auth`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/auth/signup` | No | Đăng ký tài khoản mới |
| `POST` | `/auth/login` | No | Xác thực credentials, trả về JWT |
| `GET` | `/auth/me` | Bearer JWT | Profile của user hiện tại |

Tất cả 3 endpoint đều hoạt động đầy đủ: signup hash password (bcrypt), login trả JWT, me resolve user từ `get_current_user` dependency.

### `extraction_api.py` — `/extraction`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/extraction/cvs` | Bearer JWT | Upload file CV (PDF/image), validate + persist, return extracted data |
| `GET` | `/extraction/cv/{cv_id}` | Bearer JWT | Fetch extracted CV data theo ID (ownership check) |

Input: `multipart/form-data` (`file` field). Validates content-type (PDF/PNG/JPEG/WebP) and size (10 MB). MVP MOCK: persists `CVRecord` with deterministic data.

### `optimization_api.py` — `/optimization`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/optimization/cvs/{cv_id}/optimizations` | Bearer JWT | Chạy multi-agent CV intelligence pipeline (MVP MOCK) |
| `POST` | `/optimization/cvs/{cv_id}/render` | Bearer JWT | Render CV vào template (JSON) — body `RenderTemplateRequest` (MVP MOCK) |
| `GET` | `/optimization/cvs/{cv_id}/pdf` | Bearer JWT | Stream PDF — query param `template` (501 — out of MVP) |

`OptimizationService` + `CVTemplateRenderer` inject qua `get_optimization_service` / `get_template_renderer`.

### `job_matching_api.py` — `/jobs`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/jobs/matches` | Bearer JWT | So khớp CV với một JD cụ thể (URL hoặc raw text) — MVP MOCK |
| `GET` | `/jobs/recommendations/{cv_id}` | Bearer JWT | Top-N job recommendations từ crawled corpus |

Delegate đến `MatchingService` (Hybrid Scoring algorithm).

### `interview_api.py` — `/interview`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `GET` | `/interview/health` | No | Module health check |
| `POST` | `/interview/sessions` | Bearer JWT | Tạo interview session shell (REST-tracked) |
| `GET` | `/interview/sessions/{session_id}/report` | Bearer JWT | Fetch STAR-scored report sau phiên |
| `WebSocket` | `/interview/ws` | Token (first JSON message) | Real-time voice interview channel |

**WebSocket protocol** (target, chưa implement):
```
Client → bytes  : PCM Int16 mono @ 16kHz (mic audio)
Client → json   : {"type": "start_session", "cv_id": "...", "mode": "..."}
                  {"type": "end_session"}
Server → json   : transcripts, AI text, status events
Server → bytes  : TTS PCM @ 24kHz mono
```

## Technology

| Component | Library |
|---|---|
| HTTP framework | **FastAPI** (`APIRouter`, `Depends`, `HTTPException`) |
| WebSocket | FastAPI `WebSocket` |
| Request validation | Pydantic v2 (auto-injected từ `schema/`) |
| Auth | `get_current_user` (`providers/auth.py`), service getters (`dependencies` re-export) |
| DI | `Depends()` — singleton trong `app/core/providers/` |
