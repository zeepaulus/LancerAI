# `app/service/` — Business Logic Layer

Package chứa toàn bộ business logic của hệ thống, được tổ chức theo 4 product modules. Đây là tầng trung gian giữa routers (HTTP interface) và repositories (data access). Service layer nhận dependencies qua constructor injection (không qua `Depends` trực tiếp).

## Structure

```
service/
├── auth_service.py          # Module 0: Authentication
├── extraction_service.py    # Module 1: CV Extraction
├── optimization_service.py  # Module 2: CV Intelligence (orchestrator)
├── matching_service.py      # Module 3: Job Matching
├── interview_service.py     # Module 4: Interview (REST companion)
├── agents/                  # Module 2: LangGraph multi-agent pipeline
└── interview/               # Module 4: Real-time voice pipeline
```

## Top-level Services

### `auth_service.py` — Authentication
Xử lý signup, login, và token resolution.

| Method | Description |
|---|---|
| `signup(db, email, password, display_name, tenant_id)` | Hash password, tạo `User` record |
| `login(db, email, password)` | Verify password, issue JWT |
| `resolve_token(db, token)` | Decode JWT → lookup `User` (dùng bởi `get_current_user` dependency) |

Dependencies: `RelationalRepository[User]`, `Settings` (JWT secret + algorithm).

---

### `extraction_service.py` — Module 1: CV Extraction
Pipeline: File upload → Text/OCR extraction → LLM entity parsing → Persist.

| Method | Description |
|---|---|
| `extract_from_pdf(file_bytes, filename, user_id, session)` | PyMuPDF text extraction, fallback OCR khi text density thấp |
| `extract_from_image(file_bytes, filename, user_id, session)` | Pure PaddleOCR pipeline |

**Flow:**
```
File bytes → OCRProcessor (nếu cần) → raw text
           → LLMConnector.generate(json_mode=True) → CVExtractionResponse schema
           → RelationalRepository.create() → CVRecord (PostgreSQL)
           → VectorRepository.store_embedding() → ChromaDB/Qdrant
```

Dependencies: `OCRProcessor`, `LLMConnector`, `VectorRepository`, `RelationalRepository[CVRecord]`.

---

### `optimization_service.py` — Module 2: CV Intelligence
Orchestrates the **LangGraph multi-agent pipeline** và template rendering.

| Method | Description |
|---|---|
| `analyze_cv(cv_id, cv_data, target_job_title, target_industry, session)` | Chạy pipeline `retrieval → roast → rewrite → audit`, persist `optimized_data` |
| `render_template_cv(cv_data, template)` | LLM project CV vào Harvard / Stanford / Modern template (JSON) |
| `render_template_pdf(cv_data, template)` | WeasyPrint render HTML → PDF bytes |

Service này là **public entry point duy nhất** cho Module 2 — routers không được gọi LangGraph trực tiếp.

Dependencies: `LLMConnector`, `VectorRepository`, `RelationalRepository[CVRecord]`.

---

### `matching_service.py` — Module 3: Job Matching
Implements **Hybrid Scoring algorithm**:

```
final_score = 0.20 × frequency_score
            + 0.30 × position_score
            + 0.50 × semantic_score
```

| Method | Description |
|---|---|
| `match_cv_to_jd(cv_data, jd_text, jd_url)` | Score CV vs JD, trả về breakdown + skill gaps |
| `get_recommendations(cv_data, limit)` | Top-N job từ crawled corpus (vector similarity) |

- `frequency_score`: keyword overlap (CPU, deterministic).
- `position_score`: keyword xuất hiện ở vị trí quan trọng (title, summary, current role).
- `semantic_score`: vector similarity (CV embedding vs JD embedding) + LLM deep analysis.

Dependencies: `LLMConnector`, `VectorRepository`, `RelationalRepository[JobListing]`.

---

### `interview_service.py` — Module 4: Interview (REST Companion)
REST-side companion của real-time WebSocket pipeline. Không xử lý conversation — chỉ quản lý session lifecycle.

| Method | Description |
|---|---|
| `persist_session(payload)` | Chuyển `InterviewState` hoàn chỉnh → `InterviewSession` row (PostgreSQL) |
| `get_report(session_id)` | Assemble response shape cho frontend analytics dashboard |

Dependencies: `LLMConnector`, `VoiceSTTConnector`, `VoiceTTSConnector`, `RelationalRepository[InterviewSession]`.

---

## Sub-packages

### [`agents/`](agents/README.md) — LangGraph CV Optimization Pipeline
Multi-agent pipeline cho Module 2. Xem README riêng.

### [`interview/`](interview/README.md) — Real-time Voice Interview Pipeline
WebSocket-driven voice interview cho Module 4. Xem README riêng.

## Technology

| Component | Library |
|---|---|
| LLM inference | `LLMConnector` (Ollama / Groq) |
| Multi-agent orchestration | **LangGraph** |
| Async DB | SQLAlchemy `AsyncSession` |
| Vector search | `VectorRepository` (ChromaDB / Qdrant) |
| PDF rendering | **WeasyPrint** |
| Background tasks | **Celery** (gián tiếp qua `workers/`) |
