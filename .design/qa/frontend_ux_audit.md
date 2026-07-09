# Frontend UX Audit

Date: 2026-07-09  
Method: source-level UX review plus production build. Browser interaction smoke was blocked by missing Playwright Chromium.

## Product Direction Check

The app is moving in the right direction after recent cleanup: unnecessary dashboard metric tiles and generic profile filler have mostly been removed or reduced. The strongest UX principle for LancerAI should be:

> Show only information that helps the user decide the next action.

Decorative or "confidence-looking" numbers without real user data should not be shown.

## Findings

### HIGH - Some user-facing history depends on real backend data, but this needs browser verification

`CVReviewPage` now calls `getCVHistory({ limit: 50 })` and the backend exposes authenticated `GET /api/v1/extraction/cvs`. API smoke with a newly created test user returned `[]`, which is correct for a fresh account.

Risk: the user's reported case says previous CV uploads did not appear. That may be caused by old records without matching authenticated `user_id`, previous local mock state, failed persistence during upload, or browser/session mismatch. This cannot be fully confirmed without a browser run and a real valid CV upload.

Recommendation: after Playwright is available, test one complete flow: login -> upload a valid PDF -> analyze -> open CV history -> confirm the same record appears.

### MEDIUM - Setup forms in Interview are acceptable, but should stay clearly separate from answer input

`InterviewPage` contains text inputs/textareas for session setup, JD paste, and practice focus. No typed answer UI was found in the visible answer flow by source search.

Recommendation: keep interview answers voice-first. If a fallback typed answer is ever added, label it as an accessibility fallback and do not make it the primary path.

### MEDIUM - Question bank is closer to a library than a workflow launcher

The question bank code presents filters and a detail modal. No direct interview-start action was found in the page source, which aligns with the requested behavior.

Recommendation: keep question bank actions limited to browse, filter, inspect, and save/copy. Starting practice should remain in the Interview module.

### LOW - Dead theme infrastructure remains

`ThemeContext` still forces dark theme and writes `theme=dark` to localStorage; CSS also contains theme-toggle styles. No visible dark/light toggle was found in navigation source.

Impact: low user impact, but stale theme code can confuse future maintenance.

Recommendation: remove or archive unused theme toggle infrastructure when doing a cleanup pass.

### LOW - Visual validation still pending

The frontend build passes, but layout, mobile responsiveness, focus states, hover states, and page transitions were not browser-verified in this pass.

## UX Recommendations

- Prefer one clear primary action per screen.
- Replace generic dashboard summaries with recent user activity, missing setup actions, or real next actions.
- Avoid progress percentages unless they measure a real user task.
- Empty states should be short and actionable; avoid explaining system internals.
- Keep CV upload focused on "upload -> analyze -> actionable feedback"; do not show extracted raw categories as the main value.
- Keep report pages concise: score, evidence-backed strengths, evidence-backed improvements, and next actions.
