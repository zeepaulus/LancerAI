# Release Readiness Checklist

Date: 2026-07-09

## Checklist

| Item | Status | Notes |
| --- | --- | --- |
| Frontend production build passes | Pass | `npm run build` succeeded. |
| Backend imports cleanly | Pass | FastAPI app import succeeded. |
| Database migration current | Pass | Alembic current is at head. |
| Core health endpoints pass | Pass | `/health`, `/ready`, interview health OK. |
| Authenticated extraction history endpoint works | Pass | Fresh user received 200 `[]`. |
| Full backend tests pass | Pass after fix | `162 passed, 7 deselected, 2 warnings`. |
| Browser route smoke tests pass | Blocked | Playwright Chromium is not installed. |
| Valid CV upload persistence verified | Not complete | Needs sample valid CV flow. |
| No static meaningless dashboard metrics | Mostly pass by code review | Recent cleanup removed obvious fixed filler; browser review pending. |
| No CV extracted category preview on upload | Partially verified | Source flow changed toward analysis; browser review pending. |
| No export CV template panel | Partially verified | Source cleanup previously completed; browser review pending. |
| CV history uses real backend data | Pass by source/API | End-to-end with real uploaded CV still pending. |
| Security review complete | Pass with findings | See security/privacy report. |

## Release Decision

Not ready for production release yet.

Ready for internal demo if:

- Demo environment has stable DB/Redis.
- Stakeholders accept that browser automation and valid CV upload persistence are still pending verification.

Production release requires:

- Browser route smoke tests.
- Valid CV upload -> analysis -> history verification.
- Production secret/CORS/API URL review.
