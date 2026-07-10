# Team Implementation Plan - LancerAI

Cập nhật: 2026-07-10.

Kế hoạch này phản ánh trạng thái code hiện tại: nhiều module đã có implementation thật, nên trọng tâm tiếp theo là hardening, UX hoàn chỉnh, kiểm thử tích hợp và vận hành production-like.

## 1. Phân Công Đề Xuất

| Nhóm | Owner/Role | Scope |
|---|---|---|
| Backend/API/DB | Backend Lead | FastAPI routers, service boundary, Alembic, PostgreSQL, auth, rate limit |
| AI Platform | ML/AI Engineer | LLM routing, prompt quality, semantic cache, embedding, OCR/STT/TTS readiness |
| CV Intelligence | Backend + AI | Extraction quality, review loop, optimization agents, scorecard, PDF/DOCX export |
| Job Matching | Backend + Data | TopCV crawler, job corpus, matching score, recommendations, skill taxonomy |
| Interview Voice | Backend + AI + FE | WebSocket protocol, VAD/STT/TTS, report persistence, frontend room UX |
| Frontend/Product | Frontend Dev | Candidate journey, error/degraded states, report/dashboard polish, accessibility |
| QA/Ops | QA/DevOps | Test matrix, Docker/prod compose, observability, deployment checklist |

## 2. Workstreams

### A. Backend Hardening

| Priority | Task | Output |
|---|---|---|
| P0 | Magic-byte validation for CV files | Reject spoofed/corrupt uploads before parser |
| P0 | Better PDF error handling | 422 for encrypted/corrupt/unreadable PDFs |
| P0 | Startup/preflight checks | `/ready` or admin check includes DB/vector/LLM/STT/TTS/OCR status |
| P1 | Validate `OptimizationRequest.mode` | `Literal["standard","roast"]` |
| P1 | Consolidate CV optimization DB updates | Fewer partial-commit states |

### B. AI/Model Reliability

| Priority | Task | Output |
|---|---|---|
| P0 | LLM fallback telemetry | Know which backend generated each output |
| P0 | STT/TTS availability check | Fail early with clear message |
| P1 | Mark fallback/cached outputs | Better user trust in reports |
| P1 | Tune extraction prompt with examples | Fewer empty/misaligned CV fields |
| P2 | Skill graph seed data | Better related-skill adjustment |

### C. Frontend UX

| Priority | Task | Output |
|---|---|---|
| P0 | Degraded-state UI | Explain when AI/vector/voice services are down |
| P0 | Upload timeout/retry | Avoid hanging multipart requests |
| P1 | CV review before downstream flows | User can fix extraction before optimize/match/interview |
| P1 | Interview event feedback | Show listening, transcribing, thinking, speaking, no-speech |
| P2 | Match/report history dashboards | Better long-term candidate tracking |

### D. Workers/Data

| Priority | Task | Output |
|---|---|---|
| P0 | TopCV crawler runbook | Safe repeatable job corpus build |
| P1 | Crawler health metrics | Jobs seen/added/updated/skipped visible |
| P1 | Document export persistence | Store PDF/DOCX in object storage or local artifact store |
| P2 | Additional job sources | ITviec or curated seed jobs |

## 3. Quality Gates

Before merging backend changes:

```bash
uv run pytest
uv run ruff check app tests
uv run mypy app tests
```

Before merging frontend changes:

```bash
cd frontend
npm run build
```

Before demo/prod-like deployment:

```bash
docker compose up -d
uv run alembic upgrade head
uv run pytest
cd frontend && npm run build
```

For integration tests:

```bash
uv run pytest -m integration
```

## 4. Release Checklist

- `.env` has strong `AUTH_SECRET_KEY`.
- `AUTH_ALLOW_WEAK_SECRET=false` in production.
- `ALLOWED_ORIGINS` points to real frontend domains.
- `FRONTEND_BASE_URL` points to deployed frontend.
- PostgreSQL migrations applied.
- Redis reachable for Celery.
- Vector DB reachable and collection writable.
- Neo4j credentials valid or graph-dependent fallbacks accepted.
- At least one LLM backend is reachable.
- Voice mode has STT/TTS path configured.
- Browser media works over HTTPS, except localhost.
- Nginx proxy routes `/api/` and WebSocket upgrades correctly.

## 5. Suggested Sprint Order

1. Hardening upload + AI readiness checks.
2. Interview persistence and event UX.
3. CV review/edit loop polish.
4. Job corpus runbook and recommendations health.
5. Export/document flow persistence.
6. Dashboard/report polish and analytics.

## 6. References

- [../README.md](../README.md)
- [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)
- [FLOW_STUDY_CASES.md](FLOW_STUDY_CASES.md)
- [PROJECT_REPORT.md](PROJECT_REPORT.md)
