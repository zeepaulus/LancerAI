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

`GET /auth/me` là endpoint duy nhất đã hoạt động — resolve user từ `get_current_user` dependency. Signup và login là stubs trả về `HTTP 501`.

### `extraction_api.py` — `/extraction`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/extraction/upload` | Bearer JWT | Upload file CV (PDF/image), trigger extraction pipeline |
| `GET` | `/extraction/cv/{cv_id}` | Bearer JWT | Fetch extracted CV data theo ID |

Input: `multipart/form-data` (file + `CVUploadRequest` metadata). Delegate đến `ExtractionService`.

### `optimization_api.py` — `/optimization`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/optimization/analyze` | Bearer JWT | Chạy multi-agent CV intelligence pipeline |
| `POST` | `/optimization/render_template` | Bearer JWT | Render CV data vào named template (JSON) |
| `GET` | `/optimization/render_template_pdf` | Bearer JWT | Xuất PDF từ template (streaming binary) |

Delegate đến `OptimizationService` — orchestrator cho LangGraph pipeline.

### `job_matching_api.py` — `/jobs`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `POST` | `/jobs/match` | Bearer JWT | So khớp CV với một JD cụ thể (URL hoặc raw text) |
| `GET` | `/jobs/recommendations/{cv_id}` | Bearer JWT | Top-N job recommendations từ crawled corpus |

Delegate đến `MatchingService` (Hybrid Scoring algorithm).

### `interview_api.py` — `/interview`

| Method | Path | Auth Required | Description |
|---|---|---|---|
| `GET` | `/interview/health` | No | Module health check |
| `POST` | `/interview/sessions` | Bearer JWT | Tạo interview session shell (REST-tracked) |
| `GET` | `/interview/sessions/{session_id}/report` | Bearer JWT | Fetch STAR-scored report sau phiên |
| `WebSocket` | `/interview/ws` | Token (query param) | Real-time voice interview channel |

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
| Auth | `get_current_user` dependency từ `core/dependencies.py` |
| DI | FastAPI `Depends()` — service instances từ `core/dependencies.py` |
