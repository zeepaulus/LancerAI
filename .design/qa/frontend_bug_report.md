# Frontend Bug Report

Date: 2026-07-09  
Method: build validation, route inventory, source inspection. Browser execution blocked by missing Playwright Chromium.

## Verified

- `npm run build` passes.
- Main protected routes are registered in `frontend/src/App.jsx`.
- API base URL is centralized in `frontend/src/config/env.js`.
- Auth token use is centralized enough for normal JSON calls through `frontend/src/api/http.js`.
- CV history page calls the backend history endpoint instead of relying on local mock data.

## Issues

### MEDIUM - No automated frontend test/lint command

Repro:

1. Inspect `frontend/package.json`.
2. Observe scripts only include `dev`, `build`, and `preview`.

Impact: no repeatable frontend regression check for copy cleanup, route rendering, accessibility, or component state.

Recommendation: add at least `lint` and a smoke/e2e script once Playwright browser binaries are part of setup.

### MEDIUM - Browser route smoke is currently blocked

Repro:

1. Attempt to launch Playwright Chromium from Python.
2. Launch fails because the browser binary does not exist locally.

Impact: page transitions, responsive layout, runtime console errors, and actual user flows were not validated.

Recommendation: install Playwright Chromium and run authenticated route smoke tests for dashboard, CV upload, CV review/history, optimization, job matching, interview, reports, and settings.

### LOW - Stale dark theme toggle infrastructure

Evidence:

- `frontend/src/store/ThemeContext.jsx` forces dark mode.
- CSS still contains `.lancer-theme-toggle` styles.

Impact: no visible user-facing bug found, but this is maintenance noise.

Recommendation: remove unused theme toggle code when doing a low-risk cleanup.

## Not Reproduced

- "Find focused IT" copy was not found.
- Visible dark/light toggle was not found.
- Direct recruiter/employer/auto-apply CTAs were not found in job matching source search.
- Question bank did not show a direct start-interview action in source search.
