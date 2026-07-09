# Demo Blocker Fix Plan

Date: 2026-07-09  
Scope: only demo blockers, 500-causing bugs, broken user flows, serious UX confusion, and broken build/import/test issues.

## Priority 0 - Must Be Green For Demo

### P0.1 - Backend test/build/import baseline

Status: fixed and verified.

Evidence:

- Full backend suite now passes.
- Frontend production build passes.
- Backend import smoke passes.

Action:

- Keep this as the release gate for every demo build.

### P0.2 - CV history flow must show real uploaded CV records

Status: fixed and verified by API regression test.

Problem:

- QA confirmed `GET /api/v1/extraction/cvs` exists and frontend calls it.
- The user reported that "Lich su phan tich" did not show previous CV uploads.
- There was no focused regression test proving upload -> history visibility.

Safe fix:

- Add integration coverage for `POST /api/v1/extraction/cvs` followed by `GET /api/v1/extraction/cvs`.
- Verify the uploaded `cv_id`, filename, candidate name, and summary fields are returned for the authenticated user.

Result:

- Added `TestExtractionRoutes.test_uploaded_cv_appears_in_history`.
- Full backend suite now passes with the new regression included.

Out of scope for this pass:

- Data migration for old records created before authenticated ownership existed. This needs explicit product/data decision.

### P0.3 - Unexpected CV extraction failures must not expose raw internals

Status: fixed and verified.

Problem:

- Unexpected extraction exceptions previously returned raw exception text.

Fix already applied:

- Log server-side and return a generic user-safe error.

## Priority 1 - Demo Risk, But Not Code-Fixable In This Pass

### P1.1 - Browser smoke testing is blocked by missing Playwright Chromium

Status: environment blocker.

Problem:

- Python Playwright is installed, but browser binary is missing.

Recommended action before demo:

- Install Chromium for Playwright in the demo/test environment.
- Run route smoke for login, dashboard, CV upload, CV history, CV optimization, job matching, interview, reports, and settings.

Reason not fixed as app code:

- This is local environment setup, not an application bug.

### P1.2 - Valid real-CV upload still needs manual/browser verification

Status: pending after automated API regression.

Problem:

- Tests use mocked extraction for deterministic backend validation.
- A real PDF/image with OCR/LLM dependencies still needs a demo-environment check.
- The mocked API regression now proves persistence/history wiring for authenticated users.

Recommended action before demo:

- Use one stable sample CV and confirm upload -> analysis -> history in the running app.

## Deferred

These are intentionally not fixed in this pass:

- Dead theme infrastructure.
- Frontend lint/e2e script additions.
- LocalStorage auth hardening.
- Production CORS/secrets hardening.
- Low-priority visual polish.
- Product redesign or layout changes.
