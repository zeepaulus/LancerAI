# TODO — LancerAI

Checklist triển khai theo module. `[ ]` chưa xong, `[~]` đang làm một phần, `[x]` đã xong.

---

## M0 — Authentication

**Files:** `app/service/auth/service.py`, `app/core/security.py`, `app/core/providers/auth.py`, `app/router/v1/auth_api.py`

- [x] `security.hash_password`, `verify_password`, `create_access_token`, `decode_access_token` (bcrypt, PyJWT)
- [x] `AuthService.signup`, `login`, `resolve_token` — real implementation
- [x] Gắn endpoint trong `auth_api.py` (signup/login/me — production code)
- [x] Integration test: đăng ký → đăng nhập → `GET /auth/me`
- [ ] (Tuỳ chọn) `tenants`, RBAC chi tiết, audit log

---

## M1 — CV extraction

**Files:** `app/core/ocr_processor.py`, `app/core/llm_connector.py`, `app/service/extraction/service.py`, `app/router/v1/extraction_api.py`

- [ ] `OCRProcessor.extract_text` / `extract_text_grouped` (ví dụ PaddleOCR)
- [ ] `ExtractionService.extract_from_pdf` — PyMuPDF khi có text layer; OCR khi scan
- [ ] `ExtractionService.extract_from_image`
- [ ] LLM cấu trúc hoá raw text → schema `CVExtractionResponse`
- [x] Lưu `cv_records` (đọc/ghi theo `user_id`) — MVP mock persists deterministic structured data
- [ ] Lưu embedding CV qua `BaseVectorRepository` (phục vụ M2/M3)
- [x] Gắn `extraction_api` với service — MVP mock returns structured CV
- [x] Upload validates content-type + size → 415 / 413
- [x] GET CV validates ownership → 404 if not found

---

## M2 — CV optimization (LangGraph)

**Files:** `app/service/optimization/` (service, graph, state, `*_agent.py`), `app/service/optimization/template_renderer.py`, `app/router/v1/optimization_api.py`

- [ ] `LLMConnector` gọi Ollama / OpenAI-compatible (generate, chat, streaming)
- [ ] `retrieval_agent` — vector DB → `industry_benchmarks`, `keyword_frequency_map`
- [ ] `roast_agent` — `RoastIssue`
- [ ] `rewrite_agent` — `RewrittenSection`
- [ ] `audit_agent` — `AuditFlag`, merge `optimized_cv`
- [ ] `OptimizationService.analyze_cv` — chạy graph đã compile, persist `optimized_data`
- [ ] `CVTemplateRenderer.render_cv` / `render_pdf`
- [x] Gắn `optimization_api` — MVP mock returns deterministic optimized_data
- [x] Ownership check: cv_id must belong to user
- [ ] PDF export (WeasyPrint) — currently 501

---

## M3 — Job matching

**Files:** `app/service/matching/service.py`, `app/repository/vector_repository.py`, `app/router/v1/job_matching_api.py`

- [ ] MatchingService dùng `BaseVectorRepository` + LLM đúng lifecycle CV/JD
- [ ] `match_cv_to_jd` — Hybrid Scoring (tần suất / vị trí / semantic theo spec)
- [ ] Crawl JD từ URL (rate limit) — có thể gọi worker
- [ ] Cache parse JD (hash nội dung)
- [ ] `get_recommendations` — semantic search trên `job_listings` (currently 501)
- [x] Gắn `job_matching_api` — MVP mock returns deterministic scores + gap list
- [x] Ownership check: cv_id must belong to user

---

## M4 — Voice interview

**Files:** `app/core/voice_stt_connector.py`, `app/core/voice_tts_connector.py`, `app/service/interview/pipeline.py`, `app/service/interview/service.py`, `app/router/v1/interview_api.py`

- [ ] `VoiceSTTConnector.transcribe` / `stream_transcribe`
- [ ] `VoiceTTSConnector.synthesize` / `synthesize_stream`
- [ ] `InterviewPipeline.start` / `feed_audio` / `stop`
- [ ] `InterviewService.persist_session`, `get_report`, `create_session` — replace MVP mock with real implementation
- [x] POST /interview/sessions — MVP mock returns deterministic session
- [x] GET /interview/sessions/{session_id}/report — MVP mock returns STAR scores
- [x] WebSocket JWT auth validated; audio processing stub
- [ ] Frontend: PCM capture 16 kHz (mic) + playback 24 kHz (TTS) via WebSocket audio channel

---

## M5 — Background workers

**Files:** `app/workers/celery_app.py`, `app/workers/crawler_worker.py`, `app/workers/document_worker.py`

- [x] Celery app + Redis broker/backend — configured
- [ ] `crawl_job_listings` — Scrapy/Playwright
- [ ] `generate_document` — PDF/DOCX
- [ ] Celery Beat — lịch crawl
- [ ] Endpoint admin trigger crawl (sau M0 RBAC)

---

## Lưu trữ & graph

**Files:** `app/repository/vector_repository.py`, `app/repository/graph_repository.py`

- [x] `ChromaVectorRepository` / `QdrantVectorRepository` + factory
- [ ] `GraphRepository` Neo4j — `get_related_skills`, `get_skill_importance`
- [ ] (Tuỳ chọn) tenant routing trong `RelationalRepository`
- [x] Migration Alembic bao phủ toàn bộ model (see `migration/alembic/versions/`)

---

## Frontend

**Files:** `frontend/src/`

- [ ] Đăng nhập / đăng ký — JWT storage
- [ ] Upload CV — multipart, hiển thị extraction
- [ ] Optimization — trigger phân tích, xem roast/rewrite, tải PDF
- [ ] Job matching — JD URL / paste, điểm + gap
- [ ] Phỏng vấn — WebSocket + audio
- [ ] Dashboard lịch sử / STAR
- [ ] Routing tổng thể

---

## DX

- [x] `tests/conftest.py` — fixture SQLite async
- [x] Integration tests: 123 passed (auth + extraction + optimization + matching + interview)
- [x] ruff check: All checks passed
- [x] mypy: no issues found in 79 source files
- [ ] Pre-commit: ruff, mypy
- [x] CI — lint + test (`.github/workflows/ci.yml`): ruff, mypy, pytest, frontend build
- [ ] OpenAPI: `response_model` nhất quán
- [ ] `EmailStr` cho email đăng ký nếu bật validation
