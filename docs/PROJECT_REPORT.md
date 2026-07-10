# LancerAI Project Report

Cập nhật: 2026-07-10.

Tài liệu này tóm tắt hiện trạng project sau khi đối chiếu các file chính trong `app/`, `frontend/src/`, `migration/`, `tests/`, Docker và cấu hình môi trường.

## 1. Executive Summary

LancerAI hiện không còn là bản mock đơn giản. Backend đã có implementation thật cho auth, CV extraction, CV optimization, job matching, job listings, interview session/report, WebSocket voice pipeline, LLM routing, semantic cache và worker crawler/export. Một số phần vẫn phụ thuộc hạ tầng/model ngoài repo, nên trạng thái vận hành thực tế tùy vào `.env`, Docker services, model local và API keys.

Frontend đã có các route chính cho user journey: landing, auth, dashboard, upload CV, review CV, optimize CV, job matching, recommendations, interview, reports, profile/settings và chat/interview room.

## 2. Module Status

| Module | Status | Evidence |
|---|---|---|
| Auth | Production-like baseline | `auth_api.py`, `AuthService`, tests auth/security |
| CV extraction | Implemented with AI dependency | `ExtractionService`, PyMuPDF, OCR fallback, LLM JSON parse, vector store best-effort |
| CV review/edit | Implemented | `GET /extraction/cvs`, `PUT /extraction/cvs/{cv_id}`, frontend review flow |
| CV optimization | Implemented | LangGraph builder, retrieval/roast/rewrite/audit agents, deterministic scorecard |
| Template render/PDF | Implemented | `CVTemplateRenderer`, API streams PDF/JSON fallback, document worker |
| Job matching | Implemented | Hybrid scoring, SSRF-guarded JD URL fetch, LLM feedback fallback |
| Job crawler | Implemented for TopCV | `crawler_worker.py`, parser tests, embedding best-effort |
| Recommendations | Implemented with data dependency | vector search against stored jobs |
| Interview REST | Implemented | session planning, reports, session list |
| Interview WebSocket | Implemented | first-message JWT, VAD, STT, LLM streaming, TTS, final persistence |
| Frontend | Implemented app shell and pages | `frontend/src/App.jsx`, `api/*.js`, pages under `frontend/src/pages` |
| Tests | Active suite | `uv run pytest --collect-only -q` collected `171/178` default tests after deselecting integration tests |

## 3. Main Deliverables

### Backend API

- System health and readiness endpoints.
- Auth with signup, login, current profile, profile update, password change.
- CV upload, history, fetch and user-reviewed update.
- CV optimization with multi-agent pipeline.
- Template render and PDF export endpoint.
- Job listing browse/detail.
- CV-to-JD matching and recommendations.
- Interview JD scraping, session creation, session list, report and WebSocket.

### Frontend

- Public landing/about/auth pages.
- Auth-guarded candidate/dashboard pages.
- CV upload, extraction result, review and optimization pages.
- Job matching and recommendation pages.
- Interview/chat/report pages.
- Profile and account settings.
- API wrappers with Bearer token handling and user-facing error sanitization.

### Infrastructure

- Local `docker-compose.yml` for PostgreSQL, Redis, ChromaDB, Neo4j.
- Production `docker-compose.prod.yml` with backend, Celery worker, frontend static build and Nginx.
- Multi-stage `Dockerfile` for backend and frontend.
- Alembic migrations for current ORM schema.

## 4. Current Risks

| Risk | Impact | Current mitigation | Recommended next step |
|---|---|---|---|
| CV upload trusts multipart content type | Spoofed files can hit PDF/OCR parser | Size/type allowlist | Add magic-byte validation and clearer corrupt/encrypted PDF errors |
| OCR availability differs between local and production Docker | Image/scanned CV may not work in prod image | PyMuPDF text layer still works | Document/install OCR profile or move scan OCR to worker image |
| LLM/STT/TTS runtime depends on external services/models | AI flows can fail at runtime | Fallback chains and warnings | Add startup/preflight checks and UI degraded-state messaging |
| WebSocket transcript persistence occurs at final stop | Data loss on crash/disconnect edge cases | `finally` attempts `stop()` and persist | Persist transcript turns incrementally |
| Job recommendations need populated vector corpus | Empty recommendations for fresh DB | Crawler worker can populate DB/vector | Add seed/crawl runbook and admin status |
| Email schema is plain `str` | Weak email validation | Auth service normalizes/checks duplicate | Add `pydantic[email]` and `EmailStr` |

## 5. Test And Quality Snapshot

Command run during documentation audit:

```bash
uv run pytest --collect-only -q
```

Result summary:

- `171/178` tests collected under default marker config.
- `7` integration tests deselected by `addopts = "-m 'not integration'"`.
- One Starlette/httpx deprecation warning from FastAPI test client.

Recommended quality commands before merge:

```bash
uv run pytest
uv run ruff check app tests
uv run mypy app tests
cd frontend && npm run build
```

## 6. Recommended Roadmap

### P0 - Demo/production hardening

1. Add file signature validation for CV uploads.
2. Add explicit unreadable/empty CV handling instead of saving low-quality extraction silently.
3. Add preflight checks for LLM, STT, TTS, vector DB and OCR availability.
4. Persist interview transcript incrementally during WebSocket session.
5. Add frontend degraded-state banners when AI/vector services are unavailable.

### P1 - Reliability and UX

1. Add timeout to multipart `uploadCV`.
2. Add explicit interview events: `no_speech_detected`, `stt_started`, `llm_thinking`, `tts_started`, `tts_error`.
3. Mark report/optimization outputs with source metadata: `llm`, `fallback`, `cached`.
4. Validate optimization `mode` as a `Literal`.
5. Add admin/ops command for TopCV crawler dry-run and job corpus health.

### P2 - Product depth

1. User-editable CV data before every downstream flow.
2. Saved jobs/apply workflow endpoints exposed to frontend.
3. Better analytics dashboard for CV scores, match history and interview trend.
4. Multi-template CV export UX with PDF/DOCX downloads.
5. Seeded skill graph and domain-specific skill taxonomy.

## 7. Decision Log

- Backend keeps module boundaries by router/service/repository/core connector.
- Auth ownership is enforced at endpoints using user-scoped fetches.
- AI connectors are lazy-loaded to reduce startup cost.
- Vector DB backend is configurable: ChromaDB by default, Qdrant supported.
- LLM connector supports local-first and cloud fallback rather than hardcoding one provider.
- WebSocket uses first-message auth to keep browser connection setup simple.

## 8. Useful Links

- [../README.md](../README.md)
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
- [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md)
- [TEAM_PLAN.md](TEAM_PLAN.md)
- [../tests/README.md](../tests/README.md)
