# `app/router/v1/` - API v1

API v1 exposes LancerAI's REST and WebSocket surface. All paths below are mounted under `/api/v1`, except system endpoints in `app/main.py`.

## Router Files

| File | Prefix | Scope |
|---|---|---|
| `auth_api.py` | `/auth` | Signup, login, current user, profile update, password change |
| `extraction_api.py` | `/extraction` | CV history, upload, fetch, user-reviewed update |
| `optimization_api.py` | `/optimization` | CV optimization, template render, PDF stream |
| `job_matching_api.py` | `/jobs` | Job listings, CV-JD matching, recommendations |
| `interview_api.py` | `/interview` | Interview health, JD scrape, sessions, reports, voice WebSocket |

## Auth

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/auth/signup` | No | Create account |
| POST | `/auth/login` | No | Return JWT access token |
| GET | `/auth/me` | Bearer | Current user profile |
| PUT | `/auth/password` | Bearer | Change password |

## Extraction

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/extraction/cvs` | Bearer | Recent CV records for current user |
| POST | `/extraction/cvs` | Bearer | Upload PDF/PNG/JPEG/WebP, max 10 MB |
| GET | `/extraction/cv/{cv_id}` | Bearer | Fetch one extracted CV with ownership check |
| PUT | `/extraction/cvs/{cv_id}` | Bearer | Save user-reviewed structured CV data |

Implementation notes:

- PDF text layer uses PyMuPDF.
- Low-density PDF pages and images use OCR when available.
- LLM structures text into `CVExtractionResponse`.
- Vector embedding storage is best-effort.

## Optimization

| Method | Path | Auth | Description |
|---|---|---|---|
| POST | `/optimization/cvs/{cv_id}/optimizations` | Bearer | Run LangGraph CV optimization pipeline |
| POST | `/optimization/cvs/{cv_id}/render` | Bearer | Render structured CV into JSON template |
| GET | `/optimization/cvs/{cv_id}/pdf` | Bearer | Stream PDF or JSON fallback bytes |

The optimization route verifies CV ownership, then delegates to `OptimizationService`.

## Jobs

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/jobs/listings` | Bearer | List active job listings with filters |
| GET | `/jobs/listings/{job_id}` | Bearer | Fetch one active job listing |
| POST | `/jobs/matches` | Bearer | Score CV against JD text or safe public URL |
| GET | `/jobs/recommendations/{cv_id}` | Bearer | Vector-based job recommendations |

Matching uses hybrid scoring: frequency, position and semantic similarity. If semantic embeddings are unavailable, deterministic scores are renormalized.

## Interview

| Method | Path | Auth | Description |
|---|---|---|---|
| GET | `/interview/health` | No | Lightweight module health |
| GET | `/interview/scrape-jd?url=...` | Bearer | Fetch and structure a JD URL |
| POST | `/interview/sessions` | Bearer | Create interview session and plan |
| GET | `/interview/sessions` | Bearer | List current user's interview reports/sessions |
| GET | `/interview/sessions/{session_id}/report` | Bearer | Fetch report and transcript |
| WS | `/interview/ws` | Token first JSON | Real-time voice interview |

WebSocket first message:

```json
{"token":"<jwt>","session_id":"<session_id>","duration_minutes":5}
```

Subsequent client messages:

- Binary PCM Int16 mono 16 kHz audio.
- JSON `{"action":"stop"}`.
- JSON `{"action":"text_answer","text":"..."}`.
- JSON `{"action":"behavior_event","event":{...}}`.

Server sends JSON state/transcript/text events and binary PCM 24 kHz TTS audio.
