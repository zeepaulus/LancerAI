# Integration Flow Report

Date: 2026-07-09  
Scope: frontend/backend/API integration readiness for main user journeys.

## Flow Status

| Flow | Status | Notes |
| --- | --- | --- |
| Signup/login | Pass by API smoke | Created a test user and received access token. |
| Authenticated CV history | Pass by API smoke | Fresh user receives `[]`; ownership protection returns 401 without token. |
| Unsupported CV upload | Pass by API smoke | Returns 415 with allowed types. |
| Valid CV upload -> analysis -> history | Not fully verified | Needs sample CV and browser or API fixture upload. |
| CV upload -> optimization | Partially verified by source | Recent code routes toward optimization, but full browser flow is pending. |
| Job crawler worker | Pass with blocked source | External 403 is handled gracefully. |
| Interview health | Pass by API smoke | Health endpoint returns OK. |
| Frontend route rendering | Blocked | Playwright browser binary missing. |

## Integration Risks

### HIGH - CV history issue reported by user still needs end-to-end reproduction

The backend endpoint exists and returns account-owned CV records. The frontend history page calls it. However, the user's history-not-showing report can only be closed after validating a real uploaded CV owned by the logged-in user appears in the history list.

Recommended verification:

1. Login as a known user.
2. Upload a valid CV.
3. Confirm `POST /api/v1/extraction/cvs` returns `cv_id`.
4. Confirm `GET /api/v1/extraction/cvs` includes that `cv_id`.
5. Confirm `/cv-review` displays the record.

### MEDIUM - LocalStorage auth is convenient but raises XSS blast radius

The frontend stores access token and user profile in localStorage. This is common for prototypes, but any future XSS could read the token.

Recommendation: for production, consider httpOnly secure cookies or strict XSS hardening plus short token TTL.

### MEDIUM - API base URL setup is good but production must explicitly configure it

Frontend defaults to `http://127.0.0.1:8000` when `VITE_API_BASE_URL` is undefined. This is fine for local dev. Production builds should set proxy-relative or deployed API URL explicitly.
