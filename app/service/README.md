# `app/service/` — Business logic

Tầng điều phối nghiệp vụ giữa router và repository/connector. Service nhận dependency qua constructor (không dùng `Depends` bên trong body).

## Cấu trúc

```
service/
├── auth/service.py          M0: AuthService
├── extraction/service.py    M1: ExtractionService
├── matching/service.py      M3: MatchingService
├── optimization/            M2: bounded context
│   ├── service.py           OptimizationService — orchestrator (MVP mock; LangGraph connector contract)
│   ├── template_renderer.py CVTemplateRenderer — JSON/PDF (stub)
│   ├── graph.py             LangGraph assembly stub
│   ├── state.py             CVOptimizationState (TypedDict) + sub-schemas
│   ├── retrieval_agent.py   Agent 1: context retrieval (stub)
│   ├── roast_agent.py       Agent 2: issue detection (stub)
│   ├── rewrite_agent.py     Agent 3: section rewrite (stub)
│   └── audit_agent.py       Agent 4: truthfulness check (stub)
└── interview/               M4: bounded context
    ├── service.py           InterviewService (REST: session lifecycle, report)
    ├── pipeline.py          WebSocket orchestrator (audio processing stub)
    ├── agents.py            Question / evaluate / wrap-up node functions (stub)
    └── state.py             InterviewState + sub-schemas
```

## M0 — `auth/service.py`

| Method | Mô tả |
|--------|--------|
| `signup` | Hash password, tạo `User` |
| `login` | Verify password, trả JWT |
| `resolve_token` | Decode JWT → `User` (dùng bởi `get_current_user`) |

Dependencies: `RelationalRepository[User]`, `Settings`.

---

## M1 — `extraction/service.py`

Pipeline: file → OCR/text → LLM structured → `CVRecord` + vector.

| Method | Mô tả |
|--------|--------|
| `extract_from_pdf` | PyMuPDF khi có text; fallback OCR |
| `extract_from_image` | OCR |

Dependencies: `OCRProcessor`, `LLMConnector`, `BaseVectorRepository`, `RelationalRepository[CVRecord]`.

---

## M3 — `matching/service.py`

Hybrid scoring (tần suất / vị trí / semantic) — tham số cụ thể trong code khi implement.

| Method | Mô tả |
|--------|--------|
| `match_cv_to_jd` | Điểm CV vs JD + gap |
| `get_recommendations` | Top-N từ corpus |

Dependencies: `LLMConnector`, `BaseVectorRepository`, `RelationalRepository[JobListing]`.

---

## M2 — `optimization/`

Chi tiết: [`optimization/README.md`](optimization/README.md).

- `OptimizationService.analyze_cv` — MVP mock; LangGraph graph is wired but `analyze_cv` returns deterministic data. Replace with real graph invocation when connectors are implemented.
- Template render: `CVTemplateRenderer` (JSON/PDF), inject via `get_template_renderer`, separate from `OptimizationService`.

---

## M4 — `interview/`

Chi tiết: [`interview/README.md`](interview/README.md).

| Thành phần | Vai trò |
|-------------|---------|
| `InterviewService` | REST: session shell, persist, report |
| `InterviewPipeline` | WebSocket: STT / LLM / TTS |

## Công nghệ (tham chiếu)

| Thành phần | Thư viện / module |
|-------------|-------------------|
| LLM | `LLMConnector` |
| Multi-agent | LangGraph |
| DB async | SQLAlchemy `AsyncSession` |
| Vector | `BaseVectorRepository` |
| PDF | WeasyPrint (khi implement renderer) |
| Hàng đợi | Celery (`workers/`) |
