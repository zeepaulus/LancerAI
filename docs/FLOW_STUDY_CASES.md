# LancerAI Flow and Study Cases

Tai lieu nay tong hop cach he thong di qua tung buoc, cac study case nguoi dung co the tao ra, loi/rui ro co the gap, va huong xu ly theo muc do. Noi dung duoc doc tu code hien tai trong `app/`, `frontend/src/`, `tests/`.

## 1. Ban Do He Thong

### 1.1 Thanh phan chinh

| Tang | Thu muc | Vai tro |
|---|---|---|
| Frontend | `frontend/src/pages`, `frontend/src/api` | UI React, goi REST API va WebSocket |
| Router | `app/router/v1` | Nhan request, validate input, auth, rate limit, goi service |
| Service | `app/service` | Business logic: CV extraction, optimization, matching, interview |
| Repository | `app/repository` | Doc/ghi PostgreSQL, vector DB, Neo4j |
| Connector | `app/core` | LLM, OCR, STT, TTS, settings, auth, rate limit |
| Models | `app/models` | SQLAlchemy ORM cho PostgreSQL |
| Schemas | `app/schema` | Pydantic request/response contracts |

### 1.2 Luong request chung

```text
Browser
  -> React page / api wrapper
  -> FastAPI router
  -> auth dependency + rate limit
  -> service layer
  -> connector/repository
  -> database/vector/LLM/STT/TTS
  -> response JSON/WebSocket event
```

### 1.3 Nguyen tac bao ve hien co

- REST endpoint chinh yeu cau `Authorization: Bearer <JWT>` qua `get_current_user`.
- WebSocket interview yeu cau token trong JSON message dau tien.
- Endpoint co `cv_id`/`session_id` deu co ownership check bang `user_id`.
- Rate limit dung SlowAPI, mac dinh theo `request.client.host`; chi tin `X-Forwarded-For` neu bat `RATE_LIMIT_TRUST_FORWARDED_FOR`.
- Frontend sanitize mot so technical error message trong `apiJson`.

## 2. Auth Flow

### 2.1 Signup

```text
AuthPage
  -> POST /api/v1/auth/signup
  -> AuthSignupRequest validate password/display_name
  -> AuthService.signup()
  -> normalize email, check duplicate
  -> hash password
  -> create User
  -> response user profile
```

### 2.2 Login

```text
AuthPage
  -> POST /api/v1/auth/login
  -> AuthService.login()
  -> find user by email/display_name
  -> verify bcrypt password
  -> create JWT access token
  -> frontend stores token in localStorage
```

### 2.3 Study cases

| Case | Current behavior | Risk | Xu ly nen co |
|---|---|---|---|
| Sai password | 401 `Invalid email or password` | Low | UI hien loi dang nhap ro rang |
| Token het han | 401 | Low | Frontend logout/redirect login |
| Client gui `tenant_id` khi signup | Server ignore, tenant = user_id | Low | Dung hien tai |
| Brute force login | Co rate limit default/global, nhung chua thay limit rieng login trong router snippet | Medium | Them limit chat hon cho login, lockout tam thoi theo email/IP |
| Email format xau | `email` hien la string, chua `EmailStr` | Medium | Them `pydantic[email]`, validate email |

## 3. CV Upload and Extraction Flow

### 3.1 Frontend

File: `frontend/src/pages/CVUploadPage.jsx`

```text
User chon/drag CV
  -> validate type: PDF/JPG/PNG/WebP
  -> validate size <= 10 MB
  -> uploadCV(file)
  -> POST /api/v1/extraction/cvs multipart/form-data
  -> navigate /cv-optimization voi cvId
```

### 3.2 Backend

Files:

- `app/router/v1/extraction_api.py`
- `app/service/extraction/service.py`

```text
POST /api/v1/extraction/cvs
  -> auth user
  -> rate limit 10/minute
  -> check file.content_type in application/pdf, image/png, image/jpeg, image/webp
  -> read full bytes
  -> check <= 10 MB
  -> PDF: PyMuPDF extract text
      -> if page text density < 5 chars, render page to PNG and OCR
  -> Image: OCRProcessor.extract_text_grouped
  -> _build_extraction_prompt(raw_text[:8000])
  -> LLM generate JSON with _CV_EXTRACTION_SYSTEM
  -> parse into CVExtractionResponse
  -> retry with simpler prompt if missing name
  -> persist CVRecord with raw_text + structured data
  -> best-effort embedding store in vector DB
  -> return CVExtractionResponse
```

### 3.3 Study cases: file upload

| Case | Current behavior | Severity | Possible bug/risk | Xu ly |
|---|---|---:|---|---|
| Upload PDF hop le co text layer | Extract text, LLM parse, save DB | Normal | LLM co the parse sai/missing field | Validate warnings, cho user review/edit CV data sau extraction |
| Upload scanned PDF | Render low-density pages, OCR | Normal | OCR cham, co the loi voi PDF nhieu page | Gioi han page count/time, async job cho file lon |
| Upload image CV | OCR image, LLM parse | Normal | OCR chat luong thap neu anh mo | UI goi y upload PDF/anh ro, hien raw text preview |
| File > 10 MB | FE chan; BE tra 413 | Low | Neu bypass FE van bi BE chan | Dung hien tai |
| File type khong ho tro | FE chan; BE tra 415 | Low | `image/jpg` FE cho nhung BE chi cho `image/jpeg`; browser thuong gui jpeg, nhung van co lech | Them `image/jpg` vao BE hoac FE bo `image/jpg` |
| Doi extension `.pdf` nhung content la exe | BE chi check `content_type` multipart | High | MIME spoof, PyMuPDF/OCR co the crash/DoS | Magic-byte sniffing, verify PDF header/image decoder, reject mismatch |
| PDF rat nhieu page nhung <10 MB | BE doc/render sync trong thread | Medium | CPU/memory spike, request timeout | Limit page count, background job, per-page OCR timeout |
| PDF encrypted/password | PyMuPDF co the fail -> 500 generic | Medium | User khong biet ly do | Catch encrypted PDF, tra 422 "PDF bi khoa mat khau" |
| CV rong/anh khong doc duoc | LLM nhan raw_text rong, co the tao empty schema | Medium | User tuong upload thanh cong nhung data trong | Neu raw_text < threshold, tra 422 yeu cau file ro hon |
| LLM JSON invalid | `_parse_extraction_response` fallback empty schema | Medium | Silent failure, van tao CV record rong | Neu parse fail + raw_text co noi dung, nen retry; neu van fail tra 502/partial status |
| Vector DB down | Log warning, extraction van thanh cong | Low | Recommendations sau do co the rong | UI/ops canh bao "semantic search unavailable"; retry background |

## 4. CV Optimization Flow

### 4.1 Entry point

Files:

- `app/router/v1/optimization_api.py`
- `app/service/optimization/service.py`
- `app/service/optimization/graph.py`
- `app/service/optimization/*_agent.py`

```text
POST /api/v1/optimization/cvs/{cv_id}/optimizations
  -> auth user
  -> ownership check via ExtractionService.get_cv
  -> OptimizationService.analyze_cv
  -> load extracted_data
  -> build LangGraph initial state
  -> retrieval_agent: role benchmarks
  -> roast_agent: evidence-first CV issues
  -> rewrite_agent: rewrite high/critical issues only
  -> audit_agent: approve/reject rewrites
  -> build deterministic CV scorecard
  -> persist optimized_data, audit_score, status=optimized
  -> return CVOptimizationResponse
```

### 4.2 Prompt guardrails hien co

- `roast_agent` bo qua low-impact issue, GPA/thang diem/noise.
- `rewrite_agent` chi rewrite critical/high, khong invent number, bo rewrite low-value.
- `audit_agent` chan rewrite them metric/scope/role khong co trong CV goc.

### 4.3 Study cases: CV optimization

| Case | Current behavior | Severity | Possible bug/risk | Xu ly |
|---|---|---:|---|---|
| CV co data tot | It issue, scorecard deterministic | Normal | LLM co the van tao issue lan man | Backend filter da co; tiep tuc test prompt guardrails |
| CV thieu kinh nghiem/du an | Issue co `needs_clarification` | Normal | Chua co UI inquiry loop day du | UI nen hoi them thong tin truoc rewrite |
| LLM down | Router tra 500 pipeline failed | Medium | User mat context | Fallback deterministic scorecard + "AI suggestions unavailable" |
| LLM tao rewrite bia so lieu | `_has_new_numeric_claim` va audit filter | Medium | Van co claim dinh tinh thoi phong | Mo rong audit cho role/scope/tech stack |
| User dung `cv_id` cua nguoi khac | 404 access denied | Low | Dung hien tai |
| `mode` bat ky string | Schema hien `mode: str`, service pass through | Medium | Prompt/graph co the xu ly mode la | Doi schema thanh Literal hoac validate allowed values |
| Optimized data update thanh cong nhung audit_score update loi | Co 2 commit rieng | Medium | CV co optimized_data nhung status/audit_score chua update | Gom transaction hoac rollback/compensating update |

## 5. Template Render / PDF Flow

```text
POST /api/v1/optimization/cvs/{cv_id}/render
  -> ownership check
  -> source = optimized_data or extracted_data
  -> CVTemplateRenderer.render_cv(source, template)
  -> return RenderedCVResponse

GET /api/v1/optimization/cvs/{cv_id}/pdf
  -> ownership check
  -> render_pdf
  -> stream PDF or JSON fallback bytes
```

### Study cases

| Case | Current behavior | Severity | Xu ly |
|---|---|---:|---|
| Template name invalid | 422 | Low | UI dropdown only known templates |
| PDF renderer missing/fails | 500 | Medium | Return 501/422 with actionable message; fallback JSON download |
| User tries other user's CV | 404 | Low | Dung hien tai |

## 6. Job Matching Flow

### 6.1 Manual JD match

Files:

- `app/router/v1/job_matching_api.py`
- `app/service/matching/service.py`

```text
POST /api/v1/jobs/matches
  -> auth user
  -> body requires cv_id + (jd_text or jd_url)
  -> ownership check CV
  -> if jd_url and no jd_text: _fetch_jd_from_url
  -> tokenize JD/CV
  -> frequency score
  -> position score
  -> semantic score via embeddings
  -> if embedding unavailable, exclude semantic and renormalize deterministic scores
  -> LLM feedback missing_skills/improvement_feedback
  -> Neo4j related skill adjustment if available
  -> save JobMatchResult
  -> return JobMatchResponse
```

### 6.2 JD URL fetch security

`_fetch_jd_from_url` calls `_is_public_http_url` before fetching:

- only `http`/`https`
- reject localhost
- reject private/loopback/link-local/multicast/reserved/unspecified IP
- resolve hostname and require all resolved IPs public
- Jina Reader first, direct fetch fallback

### 6.3 Study cases: matching

| Case | Current behavior | Severity | Possible bug/risk | Xu ly |
|---|---|---:|---|---|
| `jd_text` empty and no URL | Pydantic validator 422 | Low | Dung hien tai | UI require JD source |
| URL private/internal | `_is_public_http_url` rejects, fetch returns "" -> 422 empty JD | High mitigated | DNS rebinding still possible between resolve and request | Pin resolved IP/custom transport or prefer server-side allowlist |
| URL huge page | Text truncated 12000/8000 | Medium | Bandwidth/time cost | Limit content length, timeout already co 10/20s |
| Embedding unavailable | Semantic excluded, score deterministic | Low | Score less accurate | UI label "semantic unavailable" |
| LLM feedback fails | Deterministic skill gaps fallback | Low | Feedback generic | Good fallback, add logging/monitoring |
| Job listings query with `%` broad | Limit max 100 | Low | Expensive ilike on large table | Add indexes/full-text search later |

## 7. Interview Session Flow

### 7.1 Create interview session

Files:

- `app/router/v1/interview_api.py`
- `app/service/interview/service.py`
- `app/service/interview/planning.py`

```text
POST /api/v1/interview/sessions
  -> auth user
  -> validate InterviewSessionRequest
  -> ownership check CV
  -> choose cv.optimized_data else extracted_data
  -> build JD data from jd_text/jd_url/job_listing_id
  -> infer/normalize IT job title
  -> build_interview_plan(cv, jd, mode, focus_area, duration)
  -> create InterviewSession row
  -> store setup/interview_plan in star_scores JSON
  -> return session_id + meeting_url + plan
```

### 7.2 WebSocket protocol

Endpoint: `WS /api/v1/interview/ws`

```text
Client opens WS
  -> server accepts
  -> first message must be JSON:
     {"token": "...", "session_id": "...", "duration_minutes": 5}
  -> validate JWT
  -> load session by session_id + user_id
  -> load CV ownership
  -> create InterviewPipeline
  -> pipeline.start(...)
  -> server sends JSON events:
     session_started, phase_change, transcript, assistant_text, session_ended, error
  -> client sends binary PCM Int16 mono 16kHz
  -> client may send JSON actions:
     stop, behavior_event, text_answer
```

### 7.3 Live interview pipeline

File: `app/service/interview/pipeline.py`

```text
start
  -> build system prompt from CV/JD/plan
  -> if new session: phase SPEAKING, generate greeting question
  -> if resume: phase LISTENING

feed_audio
  -> only accept during LISTENING
  -> buffer PCM
  -> VAD checks 512-sample windows
  -> silence threshold crossed
  -> _process_user_turn

_process_user_turn
  -> phase PROCESSING
  -> STT transcribe buffered utterance
  -> if empty: phase LISTENING
  -> send transcript event
  -> evaluate latest answer with LLM
  -> decide follow_up/ask/wrap_up
  -> phase SPEAKING
  -> generate LLM interviewer response stream
  -> split sentences
  -> TTS each sentence and send PCM bytes
  -> append assistant_text
  -> phase LISTENING or stop

stop
  -> final evaluation + scorecard
  -> persist_session writes scores/transcripts
```

### 7.4 Audio connectors

STT:

- `VoiceSTTConnector`
- faster-whisper lazy-loaded
- `STT_MODEL_PATH` can point to local model
- skip very short/low-RMS audio
- language fixed `vi`

TTS:

- `VoiceTTSConnector`
- engine `vieneu` can load local GGUF + codec ONNX
- current local VieNeu path: `models/tts/vieneu-turbo/vieneu-tts-v2-turbo.gguf`
- local VieNeu no longer falls back to Edge TTS when GGUF fails

### 7.5 Study cases: interview

| Case | Current behavior | Severity | Possible bug/risk | Xu ly |
|---|---|---:|---|---|
| WS first message missing token/session_id | Close 1008 | Low | UI may show generic disconnect | Map 1008 to auth/session message |
| User opens WS for another user's session | Close 1008 | Low | Dung hien tai |
| Mic permission denied | Frontend shows media error, closes socket | Low | Dung hien tai |
| Browser sends audio while AI speaking | Pipeline drops audio unless LISTENING | Normal | User starts too early, answer lost | UI disable/indicate "wait until AI finishes"; optional barge-in support later |
| User speaks too quietly/too short | STT skips low energy/short audio, returns listening | Medium | User thinks ignored | Send event `no_speech_detected` to UI |
| VAD never detects silence | Buffer grows during long speech | Medium | Memory growth/delay | Add max utterance seconds and force flush |
| STT local model missing | Runtime error during transcribe | High | Interview unusable | Startup health check/warm-up, UI preflight |
| LLM latency high | Processing long after transcript | Medium | Poor UX | Disable realtime evaluate_node, smaller model, streaming partial event |
| TTS local VieNeu timeout | Pipeline logs TTS sentence failed, no audio for sentence | Medium | Text may appear later, audio missing | Send `tts_error`, fallback to text-only, warm-up VieNeu |
| Client disconnects mid-session | finally calls pipeline.stop and persist final evaluation | Medium | If stop evaluation fails, session incomplete | Persist partial transcript incrementally |
| Reconnect existing session | Existing transcript loaded, phase LISTENING | Medium | Duplicate transcripts possible after multiple stops | Check existing turn hash/turn_number before insert |
| Behavior event spam | Client throttles; backend records events | Low/Medium | Malicious client can spam JSON events | Server-side throttle per event kind/session |
| User sends `text_answer` while speaking | `feed_text` only accepts LISTENING/PROCESSING | Low | Text ignored if phase SPEAKING | UI disable input until LISTENING |

## 8. Interview Report Flow

```text
GET /api/v1/interview/sessions/{session_id}/report
  -> auth user
  -> verify session.user_id
  -> InterviewService.get_report
  -> parse stored star_scores JSON
  -> attach transcript turns
  -> return InterviewReportResponse
```

Report is built from:

- per-answer `star_scores`
- final `scorecard`
- behavior score/observations
- persisted transcript
- setup title/focus/interview plan

### Study cases

| Case | Current behavior | Severity | Xu ly |
|---|---|---:|---|
| Report before interview completed | May return incomplete report/list status incomplete | Low | UI label incomplete |
| Session not owned by user | 404 | Low | Dung hien tai |
| Scorecard LLM fails during stop | fallback_scorecard | Medium | Report less detailed; mark generated_by=fallback |
| Persist final evaluation fails | Logged in WS finally | High | Session may remain incomplete | Retry job/background persistence, incremental transcript save |

## 9. Frontend Error Handling

### 9.1 REST API wrapper

`frontend/src/api/http.js`:

- attaches Bearer token by default
- JSON timeout default 120s
- sanitizes technical messages containing `sqlalchemy`, `traceback`, `websocket`, etc.

### 9.2 Upload-specific wrapper

`frontend/src/api/extraction.js` uses raw `fetch` without timeout. Large/slow upload can hang until browser/network decides.

Recommendation:

- add `AbortController` timeout to `uploadCV`
- share `detailToMessage`
- show retry action

## 10. Cross-Cutting Failure Modes

| Failure | Current behavior | Impact | Recommended handling |
|---|---|---|---|
| Database down | `/ready` 503; endpoints fail 500 | App unusable | Health checks, clear maintenance UI |
| Redis down | Celery/background affected | Background jobs unavailable | Mark async features degraded |
| Vector DB down | Extraction/matching log fallback | Recommendations may be empty | Non-blocking alert, retry embedding store |
| Neo4j down | Matching graph adjustment skipped | Skill relation weaker | Non-blocking |
| Ollama/API LLM down | Extraction/optimization/interview may fail | Core AI flows fail | Per-module fallback + user-facing degraded status |
| Local STT/TTS model missing | Interview audio fails | Voice interview unusable | Startup preflight and model path validation |
| CORS misconfig | Browser cannot call API | Full frontend break | Production startup warning exists; enforce deploy checklist |
| Rate limit false IP behind proxy | Limits all users as proxy or can be spoofed if XFF trusted wrongly | Availability/security | Configure trusted proxy correctly |

## 11. Priority Backlog By Severity

### P0/P1 - Should fix before production-like demo

1. Magic-byte/file signature validation for CV upload.
2. Raw text threshold: reject unreadable CV instead of saving empty extraction silently.
3. Interview partial persistence: save transcript turns incrementally, not only at WS close.
4. Startup/preflight health for STT/TTS model paths and local assets.
5. Server-side throttling for WebSocket behavior events and max audio buffer duration.

### P2 - Important UX/reliability

1. Add timeout to `uploadCV`.
2. Send explicit interview events: `no_speech_detected`, `stt_started`, `llm_thinking`, `tts_started`, `tts_error`.
3. Mark report scorecard as `llm` or `fallback`.
4. Validate `OptimizationRequest.mode` as Literal.
5. Improve user-facing errors for encrypted/corrupt PDFs.

### P3 - Nice to have / later

1. Background queue for heavy CV OCR/LLM extraction.
2. Full-text search indexes for job listings.
3. Admin observability dashboard for LLM/STT/TTS latency.
4. User-editable extracted CV before optimization/matching/interview.

## 12. Suggested Test Matrix

### Auth

- Signup duplicate email.
- Login wrong password.
- Expired/invalid JWT.
- Access other user's CV/session.

### CV upload

- Valid PDF text-layer.
- Valid scanned PDF.
- Valid PNG/JPEG/WebP.
- File > 10 MB.
- Unsupported MIME.
- Spoofed MIME vs real bytes.
- Encrypted/corrupt PDF.
- Empty image/unreadable scan.

### Optimization

- CV with strong evidence: no noisy low-value issues.
- CV with vague project bullets: high-value issues + rewrites.
- GPA-only education case: no rewrite like "da hoc tap... GPA 8.0".
- LLM invalid JSON: fallback behavior.

### Matching

- JD text only.
- JD URL public.
- JD URL localhost/private IP.
- Embedding unavailable.
- LLM feedback unavailable.

### Interview

- WS auth missing/invalid.
- Session ownership denied.
- Mic permission denied.
- Low-volume audio.
- Long speech without silence.
- TTS local model missing.
- Client disconnect before stop.
- Reconnect existing session.

## 13. Quick Reference: Main Files

| Area | Main files |
|---|---|
| Auth | `app/router/v1/auth_api.py`, `app/service/auth/service.py`, `app/core/providers/auth.py` |
| CV upload/extraction | `app/router/v1/extraction_api.py`, `app/service/extraction/service.py`, `frontend/src/pages/CVUploadPage.jsx` |
| CV optimization | `app/router/v1/optimization_api.py`, `app/service/optimization/*` |
| Job matching | `app/router/v1/job_matching_api.py`, `app/service/matching/service.py` |
| Interview REST/WS | `app/router/v1/interview_api.py`, `app/service/interview/pipeline.py`, `app/service/interview/service.py` |
| STT/TTS | `app/core/voice_stt_connector.py`, `app/core/voice_tts_connector.py` |
| LLM routing | `app/core/llm_connector.py`, `app/core/providers/connectors.py`, `.env` |
| Frontend API | `frontend/src/api/*.js` |

