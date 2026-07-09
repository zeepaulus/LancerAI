# Code Quality Review

Date: 2026-07-09  
Scope: high-signal quality issues affecting reliability and release confidence.

## Strengths

- Backend is modular by router/service/repository/schema layers.
- Alembic migration state is current.
- Auth dependency is applied to sensitive CV history endpoints.
- API base paths are centralized on the frontend.
- CV review/history now uses backend data instead of static mock content.

## Findings

### HIGH - Worker task is too tightly coupled to one helper return shape

`crawl_job_listings` currently assumes `_crawl_source_sync` always returns `(jobs, crawl_status)`. Tests and likely older callers still use `list[dict]`.

Impact: fragile task integration and failing test suite.

Recommendation: normalize helper output inside the worker boundary.

### MEDIUM - Frontend lacks automated quality gates

No frontend lint/test scripts are present.

Impact: UI regressions depend on manual review.

Recommendation: add linting and a small route smoke suite.

### MEDIUM - Error messaging is inconsistent across backend domains

Some endpoints return user-safe errors, while extraction generic failures return raw exception text.

Impact: users may see technical errors; sensitive internals may leak.

Recommendation: standardize API error envelopes and generic user-facing messages.

### LOW - Stale theme code remains after dark-only decision

`ThemeContext` and theme toggle CSS remain even though the UI no longer appears to expose a theme toggle.

Impact: maintenance confusion.

Recommendation: remove in a cleanup-only PR.

## Prompt Quality Notes

The prompt system has already been tightened to avoid over-criticizing weak signals such as GPA calculation details. Continue using evidence-first prompt rules:

- Do not penalize a CV for missing GPA formula unless a target job explicitly requires transcript/GPA verification.
- Prefer concrete, job-relevant feedback over speculative criticism.
- Separate "missing evidence" from "negative evidence".
- Avoid scoring language that sounds definitive when the CV simply lacks enough context.
