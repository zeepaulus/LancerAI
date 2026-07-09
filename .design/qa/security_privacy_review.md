# Security & Privacy Review

Date: 2026-07-09  
Scope: auth, secrets/config, CV data privacy, API error leakage, local storage.

## Findings

### HIGH - CV extraction generic errors can leak internals - Fixed

Evidence: `app/router/v1/extraction_api.py` returns `Extraction failed: {exc}` for unexpected exceptions.

Risk: OCR, LLM, database, vector DB, or file parsing details could be exposed to users.

Fix applied: the endpoint now logs the exception server-side and returns a generic user-safe message.

### MEDIUM - Development weak-secret flag is present in `.env.example`

Evidence: `.env.example` contains `AUTH_ALLOW_WEAK_SECRET=true`.

Mitigation: `app/core/settings.py` prevents enabling weak secret in production.

Risk: users may copy dev settings into non-production-like demos.

Recommendation: keep the guard, but add stronger comments or a separate `.env.dev.example` later.

### MEDIUM - Neo4j password/config mismatch risk

Evidence: `.env.example` uses `NEO4J_PASSWORD=your-neo4j-password`; Docker Compose has a concrete Neo4j auth value in the local setup.

Risk: local setup confusion and accidental credential reuse.

Recommendation: move demo secrets into `.env`/documented dev-only values and keep Compose aligned with examples.

### MEDIUM - Access token stored in localStorage

Evidence: frontend auth code persists access token in localStorage.

Risk: any XSS can read the token.

Recommendation: for production hardening, use httpOnly secure cookies or stronger CSP/XSS controls and short token TTL.

### LOW - LLM parse failure logs may include raw model output snippets

Evidence: interview/CV review agents log snippets of raw LLM output on parse failure.

Risk: if raw model output echoes CV content, logs may contain personal data.

Recommendation: log correlation IDs and parse error classes instead of raw output snippets in production.

## Positive Controls

- Authenticated CV history endpoint correctly rejects unauthenticated access.
- Passwords are hashed server-side.
- Production settings guard prevents weak auth secret in production.
- Unsupported upload types are rejected before extraction work starts.
