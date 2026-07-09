# Backend API Bug Report

Date: 2026-07-09  
Method: live API smoke tests, OpenAPI inspection, backend import, pytest, Alembic current.

## Verified API Behavior

- `GET /health` returned healthy.
- `GET /ready` returned ready with database check OK.
- `GET /api/v1/interview/health` returned OK.
- `GET /openapi.json` returned 200 and documented extraction/auth/job/interview/optimization routes.
- Unauthenticated `GET /api/v1/extraction/cvs` returned 401.
- Authenticated `GET /api/v1/extraction/cvs` returned 200 with an empty list for a fresh user.
- Unsupported CV upload content type returned 415 with allowed file types.
- Alembic reports current revision at head.

## Issues

### HIGH - Worker test fails because crawler helper return contract changed - Fixed

Repro:

1. Run backend pytest.
2. Observe `tests/test_workers.py::test_crawler_worker_flow` failure.

Root cause: test mock returns `list[dict]`; `crawl_job_listings` expects `(jobs, crawl_status)`.

Impact before fix: test suite was not release-green.

Fix applied: `crawl_job_listings` accepts both old and new helper return shapes. Full backend suite now passes.

### MEDIUM - Extraction 500 responses expose raw exception details - Fixed

Evidence: `app/router/v1/extraction_api.py` returns `detail=f"Extraction failed: {exc}"` for generic exceptions.

Impact: internal OCR/LLM/storage errors may leak implementation details or sensitive filenames/messages to clients.

Fix applied: unexpected extraction failures are logged server-side and return a generic user-safe message.

### MEDIUM - Valid CV upload flow was not fully validated

Reason: no stable sample CV and no browser binary in the current pass. Unsupported type and auth behavior were validated.

Recommendation: add a small fixture PDF/image and test upload persistence through `GET /api/v1/extraction/cvs`.

## External Dependency Behavior

The TopCV crawler returned a graceful blocked status on 403. This is acceptable behavior for a public crawler and should not fail the application.
