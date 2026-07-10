# TODO - LancerAI

Checklist này phản ánh trạng thái code hiện tại sau đợt rà soát tài liệu ngày 2026-07-10.

Ký hiệu:

- `[x]` đã có implementation hoặc test cơ bản.
- `[~]` đã có một phần, còn phụ thuộc hạ tầng/model hoặc cần hardening.
- `[ ]` chưa làm hoặc nên làm tiếp.

## P0 - Hardening Trước Demo/Production-Like

- [ ] Thêm magic-byte/file signature validation cho CV upload.
- [ ] Trả lỗi rõ cho PDF encrypted/corrupt/unreadable thay vì 500 generic.
- [ ] Reject hoặc mark partial khi raw text trích xuất quá ít.
- [ ] Thêm preflight/health cho LLM, vector DB, OCR, STT, TTS.
- [ ] Persist interview transcript incrementally trong WebSocket session.
- [ ] Thêm max utterance duration để tránh buffer audio tăng không giới hạn.
- [ ] Thêm server-side throttle cho `behavior_event`.
- [ ] Thêm frontend degraded-state khi AI/vector/voice service unavailable.

## M0 - Authentication

Files: `app/service/auth/service.py`, `app/core/security.py`, `app/core/providers/auth.py`, `app/router/v1/auth_api.py`

- [x] Hash/verify password bằng bcrypt.
- [x] JWT create/decode bằng PyJWT.
- [x] Signup/login/me.
- [x] Update profile bằng `PATCH /auth/me`.
- [x] Change password bằng `PUT /auth/password`.
- [x] Auth dependency `get_current_user`.
- [x] WebSocket token validation helper.
- [~] Email hiện là `str`.
- [ ] Thêm `pydantic[email]` và `EmailStr`.
- [ ] RBAC/tenant organization flow chi tiết.
- [ ] Audit log cho hành động nhạy cảm.

## M1 - CV Extraction

Files: `app/service/extraction/service.py`, `app/core/ocr_processor.py`, `app/router/v1/extraction_api.py`

- [x] Upload endpoint với content-type allowlist.
- [x] Giới hạn file 10 MB.
- [x] PyMuPDF đọc PDF text layer.
- [x] OCR fallback cho PDF scan/image khi PaddleOCR có sẵn.
- [x] LLM structured extraction theo `CVExtractionResponse`.
- [x] Retry extraction khi thiếu tên.
- [x] Lưu `CVRecord` theo `user_id`.
- [x] List CV history.
- [x] Fetch CV theo ownership.
- [x] Update reviewed extracted data.
- [x] Store/update embedding best-effort.
- [~] Production Docker hiện loại PaddleOCR để giảm image size.
- [ ] Magic-byte validation.
- [ ] UX phân biệt extraction partial/fallback.
- [ ] Background extraction job cho file scan lớn.

## M2 - CV Optimization

Files: `app/service/optimization/`, `app/service/cv_analysis/scorecard.py`, `app/router/v1/optimization_api.py`

- [x] LangGraph graph assembly.
- [x] Retrieval agent.
- [x] Roast agent.
- [x] Rewrite agent.
- [x] Audit agent.
- [x] Deterministic CV scorecard.
- [x] Persist `optimized_data`, `audit_score`, `optimization_mode`, `status`.
- [x] Render template JSON.
- [x] PDF endpoint with streaming response.
- [x] Document worker PDF export path.
- [~] `OptimizationRequest.mode` vẫn là `str`.
- [ ] Đổi `mode` sang `Literal["standard","roast"]`.
- [ ] Gom transaction hoặc recovery cho nhiều DB updates.
- [ ] Metadata output source: `llm`, `fallback`, `cached`.
- [ ] Inquiry loop để hỏi thêm dữ liệu trước rewrite.

## M3 - Job Matching And Job Corpus

Files: `app/service/matching/service.py`, `app/router/v1/job_matching_api.py`, `app/workers/crawler_worker.py`

- [x] Hybrid scoring: frequency, position, semantic.
- [x] Renormalize score khi semantic embedding unavailable.
- [x] LLM missing skills feedback.
- [x] Deterministic fallback feedback/gaps.
- [x] Safe public URL checks cho JD fetch.
- [x] Persist `JobMatchResult`.
- [x] List/detail job listings.
- [x] Recommendations via vector search.
- [x] TopCV crawler worker.
- [x] TopCV parser tests.
- [~] Recommendations cần job corpus và embeddings đã populate.
- [ ] Job corpus seed/runbook cho demo.
- [ ] Full-text search index cho job listings.
- [ ] Saved/applied/rejected workflow endpoints exposed to frontend.
- [ ] Admin trigger/status endpoint cho crawler.

## M4 - Voice Interview

Files: `app/service/interview/`, `app/core/voice_stt_connector.py`, `app/core/voice_tts_connector.py`, `app/router/v1/interview_api.py`

- [x] Create interview session.
- [x] Build interview plan from CV/JD.
- [x] JD scrape endpoint.
- [x] List sessions.
- [x] Get report.
- [x] WebSocket first-message JWT/session validation.
- [x] PCM audio intake.
- [x] VAD/turn detection.
- [x] STT via Groq or faster-whisper.
- [x] LLM streaming interviewer response.
- [x] TTS via Edge/Piper/VieNeu.
- [x] Behavior event scoring.
- [x] STAR/final scorecard persistence on stop.
- [~] Transcript persistence mostly final-stop based.
- [ ] Incremental transcript persistence.
- [ ] Explicit events: `no_speech_detected`, `stt_started`, `llm_thinking`, `tts_started`, `tts_error`.
- [ ] Preflight check for local STT/TTS model paths.
- [ ] Server-side behavior-event throttle.

## M5 - Background Workers

Files: `app/workers/celery_app.py`, `app/workers/crawler_worker.py`, `app/workers/document_worker.py`

- [x] Celery app configured.
- [x] Redis broker/result backend config.
- [x] TopCV crawler worker.
- [x] Job upsert by `source_url`.
- [x] Job embedding best-effort.
- [x] Document worker PDF export.
- [x] Document worker DOCX export.
- [ ] Celery Beat schedule.
- [ ] Persist generated documents to object storage/local artifact store.
- [ ] Retry queue for failed embeddings.

## Storage And Graph

- [x] `RelationalRepository` generic CRUD.
- [x] ChromaDB vector repository.
- [x] Qdrant vector repository.
- [x] Vector repository factory.
- [x] Neo4j `GraphRepository` with related skill and importance queries.
- [x] LLM response cache model/repository.
- [x] Alembic migrations for current schema.
- [ ] Seed skill graph data.
- [ ] pgvector or external ANN strategy for large LLM cache if needed.

## Frontend

Files: `frontend/src/`

- [x] Landing/about/auth routes.
- [x] Auth guard.
- [x] Dashboard/candidate/profile/settings routes.
- [x] CV upload route.
- [x] CV extraction result/review routes.
- [x] CV optimization route.
- [x] Job matching/recommendations routes.
- [x] Interview/chat/report routes.
- [x] API wrappers for auth/extraction/optimization/matching/interview.
- [x] JSON API timeout and error sanitizer.
- [~] Multipart upload wrapper has no timeout.
- [ ] Add `AbortController` timeout/retry to `uploadCV`.
- [ ] Strong degraded-state UI for AI/vector/voice service outages.
- [ ] Show interview state events clearly.
- [ ] More complete reports dashboard.

## DX / QA

- [x] `uv run pytest --collect-only -q` collected `171/178` default tests after integration deselect.
- [x] Unit/integration-style tests for auth, routes, models, schemas, security, vector, graph, matching, interview, workers.
- [x] CI workflow exists under `.github/workflows/ci.yml`.
- [ ] Run full quality gate after docs/code changes:

```bash
uv run pytest
uv run ruff check app tests
uv run mypy app tests
cd frontend && npm run build
```

- [ ] Add frontend lint/test setup if project needs stricter FE CI.
