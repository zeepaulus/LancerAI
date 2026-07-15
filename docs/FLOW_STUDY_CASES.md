# LancerAI Flow And Study Cases

Cập nhật: 2026-07-10.

Tài liệu này tổng hợp các flow người dùng chính, hành vi hiện tại, failure modes và backlog ưu tiên. Nội dung được đối chiếu từ `app/`, `frontend/src/`, `tests/`, Docker và cấu hình môi trường.

## 1. Bản Đồ Hệ Thống

```text
Browser
  -> React page
  -> frontend/src/api wrapper
  -> FastAPI router
  -> auth dependency + rate limit
  -> service layer
  -> repository/connector
  -> DB/vector/graph/LLM/STT/TTS
```

| Tầng | Thư mục | Vai trò |
|---|---|---|
| Frontend | `frontend/src/pages`, `frontend/src/api` | UI, REST calls, WebSocket room |
| Router | `app/router/v1` | Validate, auth, rate limit, call service |
| Service | `app/service` | Business logic |
| Repository | `app/repository` | PostgreSQL, vector DB, Neo4j, LLM cache |
| Connector | `app/core` | LLM, OCR, STT, TTS, settings, security |
| Models | `app/models` | ORM schema |
| Schemas | `app/schema` | Pydantic contracts |
| Workers | `app/workers` | Celery crawler/export tasks |

## 2. Auth Flow

```text
Signup/Login
  -> AuthPage
  -> POST /api/v1/auth/signup hoặc /login
  -> AuthService
  -> User table
  -> JWT access token
  -> frontend stores token
```

Study cases:

| Case | Current behavior | Risk | Recommended handling |
|---|---|---|---|
| Sai mật khẩu | 401 | Low | UI hiển thị lỗi đăng nhập |
| Token hết hạn/sai | 401 | Low | Frontend logout hoặc redirect login |
| Signup trùng email | 400/409 theo service behavior | Low | Giữ message user-friendly |
| Brute force login | Có rate limit route | Medium | Thêm lockout theo email/IP nếu cần |
| Email format xấu | `email` hiện là `str` | Medium | Thêm `pydantic[email]` và `EmailStr` |

## 3. CV Upload And Extraction

```text
CVUploadPage
  -> uploadCV(file)
  -> POST /api/v1/extraction/cvs
  -> validate MIME + size
  -> PDF: PyMuPDF text layer, OCR fallback for low-density pages
  -> Image: OCR
  -> LLM JSON extraction
  -> CVRecord
  -> vector embedding best-effort
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| PDF có text layer | Extract text, LLM parse, save | Normal | Cho user review/edit extracted data |
| PDF scan | Render page to PNG, OCR if available | Normal | Có progress/async job cho file lớn |
| Ảnh CV | OCR then LLM | Normal | Gợi ý ảnh rõ, đủ sáng |
| File > 10 MB | FE/BE chặn | Low | Giữ hiện tại |
| MIME không hỗ trợ | 415 | Low | Đồng bộ FE/BE accepted types |
| Spoof MIME | BE chưa magic-byte check | High | Add file signature validation |
| PDF encrypted/corrupt | Có thể thành 500 generic | Medium | Catch và trả 422 rõ nghĩa |
| Raw text quá ít | Có thể vẫn tạo record rỗng | Medium | Reject unreadable CV hoặc mark partial |
| LLM JSON invalid | Fallback empty schema | Medium | Retry + partial status, tránh silent success |
| Vector DB down | Log warning, extraction vẫn thành công | Low | Hiển thị semantic search degraded |

## 4. CV Review And Update

```text
CVExtractionResultPage / CVReviewPage
  -> GET /api/v1/extraction/cv/{cv_id}
  -> user chỉnh structured fields
  -> PUT /api/v1/extraction/cvs/{cv_id}
  -> reset optimized_data/audit_score/status
  -> update embedding best-effort
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| User sửa dữ liệu trước optimize | Supported | Normal | Nên khuyến khích review trước matching/interview |
| User sửa CV đã optimized | Optimized data reset | Normal | UI cảnh báo cần chạy optimize lại |
| Embedding update fail | Non-fatal | Low | Retry background nếu cần |

## 5. CV Optimization

```text
POST /api/v1/optimization/cvs/{cv_id}/optimizations
  -> ownership check
  -> LangGraph initial state
  -> retrieval_agent
  -> roast_agent
  -> rewrite_agent
  -> audit_agent
  -> build_cv_scorecard
  -> persist optimized_data + audit_score
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| CV đủ dữ liệu | Scorecard + issues/rewrite | Normal | UI phân biệt issue high/critical |
| CV thiếu thông tin | Agents có guardrails/fallback | Medium | Thêm inquiry loop để hỏi user |
| LLM down | Pipeline có thể 500 | High | Fallback deterministic scorecard |
| Rewrite bịa số liệu | Audit/guardrail chặn claim số mới | Medium | Mở rộng audit cho scope/role/tech |
| `mode` lạ | Schema vẫn là `str` | Medium | Đổi thành `Literal["standard","roast"]` |
| Update DB bị ngắt giữa chừng | Có nhiều commit | Medium | Gom transaction hoặc recovery logic |

## 6. Template Render And Document Export

```text
POST /api/v1/optimization/cvs/{cv_id}/render
  -> source = optimized_data or extracted_data
  -> CVTemplateRenderer.render_cv
  -> RenderedCVResponse

GET /api/v1/optimization/cvs/{cv_id}/pdf
  -> CVTemplateRenderer.render_pdf
  -> StreamingResponse
```

Worker:

```text
generate_document(cv_data, template, output_format)
  -> PDF via CVTemplateRenderer/WeasyPrint
  -> DOCX via python-docx
  -> base64 output
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| Template invalid | 422 | Low | UI dropdown từ template whitelist |
| PDF renderer không tạo PDF thật | API dùng media type JSON fallback | Medium | UI label fallback, expose download JSON |
| Export lớn | Worker tránh block API | Low | Lưu artifact vào object storage |

## 7. Job Matching And Recommendations

```text
POST /api/v1/jobs/matches
  -> body: cv_id + jd_text hoặc jd_url
  -> ownership check
  -> safe JD fetch if URL
  -> frequency + position + semantic score
  -> LLM missing skills feedback
  -> Neo4j related-skill adjustment best-effort
  -> save JobMatchResult
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| JD text trực tiếp | Supported | Normal | Giữ text preview |
| JD URL public | Fetch qua Jina/direct fallback | Normal | Show crawl failure clearly |
| URL private/localhost | Rejected by safety check | High mitigated | Consider allowlist/pinned IP transport |
| Embedding unavailable | Semantic excluded, score renormalized | Low | UI label "semantic unavailable" |
| LLM feedback fail | Deterministic gap fallback | Low | Mark feedback source |
| Fresh DB no jobs | Recommendations empty | Medium | Provide crawler/seed job runbook |

## 8. Job Crawler

```text
Celery crawl_job_listings(source="topcv", max_pages=5)
  -> approved TopCV URL builder
  -> static HTML fetch
  -> Playwright fallback when needed
  -> detail parser
  -> upsert JobListing by source_url
  -> embedding best-effort
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| TopCV blocks request | Task stops safely/status returned | Medium | Backoff schedule and ops alert |
| Parser sees duplicate URL | Upsert/update | Low | Good current behavior |
| Non-IT listing | Filtered by IT keywords/skills | Low | Periodic sampling QA |
| Embedding fail | Job still saved | Low | Retry embedding job |

## 9. Interview Session And Voice

REST:

```text
POST /api/v1/interview/sessions
  -> CV ownership check
  -> optional JD text/URL/job_listing_id
  -> interview plan
  -> InterviewSession row
```

WebSocket:

```text
WS /api/v1/interview/ws
  -> first JSON token/session_id
  -> server validates JWT + ownership
  -> pipeline start
  -> binary PCM from browser
  -> VAD -> STT -> LLM -> TTS
  -> JSON events + audio bytes to client
  -> stop persists final evaluation
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| Missing token/session_id | Close 1008 | Low | UI map to auth/session message |
| Other user's session | Close 1008 | Low | Good current behavior |
| Mic permission denied | Frontend should handle media error | Low | Clear browser permission copy |
| User speaks too quietly | STT may return empty | Medium | Send `no_speech_detected` event |
| Long speech no silence | Buffer can grow | Medium | Add max utterance seconds |
| STT/TTS model missing | Voice flow fails | High | Preflight/warm-up |
| LLM latency high | Delayed response | Medium | Show "thinking", stream text |
| Disconnect mid-session | Finally block attempts stop/persist | Medium | Incremental transcript persistence |
| Behavior event spam | Client throttles only | Medium | Server-side throttle |

## 10. Interview Report

```text
GET /api/v1/interview/sessions/{session_id}/report
  -> verify user owns session
  -> read star_scores JSON
  -> read transcript rows
  -> InterviewReportResponse
```

Study cases:

| Case | Current behavior | Severity | Recommended handling |
|---|---|---:|---|
| Report before completion | Status can be incomplete | Low | UI label incomplete |
| Scorecard fallback | Report still possible | Medium | Mark `generated_by=fallback` |
| Persist final eval fails | Session may remain incomplete | High | Retry job or incremental save |

## 11. Cross-Cutting Failure Modes

| Failure | Impact | Current behavior | Recommended handling |
|---|---|---|---|
| Database down | App unusable | `/ready` returns 503 | Health UI and ops alert |
| Redis down | Workers unavailable | API mostly still runs | Mark async features degraded |
| Vector DB down | Semantic/recommendation weaker | Best-effort warnings | Retry embeddings |
| Neo4j down | Related skill adjustment skipped | Best-effort warnings | Optional graph health |
| LLM down | AI flows fail or fallback | Depends on module | Degraded state and fallback scorecards |
| STT/TTS missing | Voice interview fails | Runtime errors/warnings | Preflight check |
| CORS misconfig | Browser cannot call API | Production warning if empty | Deployment checklist |
| Weak JWT secret | Security risk | Production validation blocks weak secret | Keep validation |

## 12. Priority Backlog

### P0

1. Magic-byte validation for upload.
2. Reject/mark unreadable CV extraction.
3. STT/TTS/LLM/vector/OCR preflight endpoint.
4. Interview incremental transcript persistence.
5. Max utterance seconds and server-side behavior-event throttle.

### P1

1. Upload timeout/retry in frontend.
2. Interview state events for no-speech/STT/LLM/TTS.
3. Mark AI outputs as `llm`, `fallback`, or `cached`.
4. Validate optimization mode with `Literal`.
5. Clear PDF/OCR user-facing errors.

### P2

1. Background extraction job for large OCR/LLM workloads.
2. Full-text search/indexes for job listings.
3. Admin observability for AI latency and fallback rates.
4. Skill graph seed and management scripts.
5. Rich match/report history dashboards.

## 13. Suggested Test Matrix

| Area | Tests |
|---|---|
| Auth | duplicate signup, wrong password, invalid/expired token, profile update, password change |
| CV upload | valid PDF, valid image, >10 MB, unsupported MIME, spoof MIME, corrupt/encrypted PDF, unreadable scan |
| Extraction | LLM invalid JSON, missing name retry, vector DB down |
| Optimization | strong CV, vague CV, invented metric guardrail, LLM unavailable |
| Matching | JD text, JD URL, private URL, embedding down, LLM feedback down |
| Jobs | TopCV URL builder, parser, duplicate upsert, empty crawl |
| Interview | WS auth failure, ownership denial, low-volume audio, long speech, TTS/STT missing, disconnect |
| Frontend | auth guard, upload retry, error sanitizer, route navigation, report incomplete state |

## 14. Quick File Reference

| Area | Main files |
|---|---|
| Auth | `app/router/v1/auth_api.py`, `app/service/auth/service.py`, `app/core/providers/auth.py` |
| CV extraction | `app/router/v1/extraction_api.py`, `app/service/extraction/service.py`, `frontend/src/pages/CVUploadPage.jsx` |
| CV optimization | `app/router/v1/optimization_api.py`, `app/service/optimization/*`, `app/service/cv_analysis/scorecard.py` |
| Matching | `app/router/v1/job_matching_api.py`, `app/service/matching/service.py` |
| Jobs/crawler | `app/workers/crawler_worker.py`, `app/models/job_listing.py` |
| Interview | `app/router/v1/interview_api.py`, `app/service/interview/pipeline.py`, `app/service/interview/service.py` |
| STT/TTS | `app/core/voice_stt_connector.py`, `app/core/voice_tts_connector.py` |
| LLM/cache | `app/core/llm_connector.py`, `app/models/llm_cache.py`, `app/repository/llm_cache_repository.py` |
| Frontend API | `frontend/src/api/*.js` |
| Tests | `tests/*.py` |
