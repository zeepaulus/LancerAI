# UI Usability Improvement Plan

Date: 2026-07-07

## Implementation Priorities

1. Add collapsible desktop sidebar/workspace behavior.
2. Remove manual typed answer UI from the live Interview page.
3. Add clearer voice-first AI state guidance.
4. Add a dashboard feature launcher so users understand the main product areas quickly.
5. Tighten visual and responsive details without changing API contracts.

## Page / Component Plan

### `frontend/src/components/Layout/Navbar.jsx`

- Current issue: fixed sidebar cannot collapse; users cannot focus on dense content.
- Proposed improvement: add localStorage-backed collapsed state, toggle button, icon-only compact mode, route titles, active-state retention.
- Risk level: medium, because sidebar affects every protected page.
- Expected UX benefit: more flexible workspace and less horizontal crowding.

### `frontend/src/index.css`

- Current issue: page margin/topbar left are tied to fixed `--sidebar-width`.
- Proposed improvement: add `--sidebar-collapsed-width`, collapsed selectors, transition rules, hidden labels in compact mode, adjusted page width.
- Risk level: medium.
- Expected UX benefit: smooth resizing without overlap.

### `frontend/src/pages/ChatPage.jsx`

- Current issue: manual text answer form makes the live interview feel text-first.
- Proposed improvement: remove typed answer state/form/submit handler, update status copy, add voice-only guidance panel and clearer phase language.
- Risk level: low-medium; backend text-answer support remains untouched.
- Expected UX benefit: voice-first interview behavior is obvious.

### `frontend/src/components/Common/AppUI.jsx`

- Current issue: feature-action cards are repeated ad hoc across pages.
- Proposed improvement: add a small `FeatureActionCard` primitive.
- Risk level: low.
- Expected UX benefit: consistent feature discoverability and action layout.

### `frontend/src/pages/MainDashboard.jsx`

- Current issue: dashboard metrics are useful but first-time users may not know what to do next.
- Proposed improvement: add feature launcher cards for Voice Interview, Question Bank, CV Analysis, CV Optimization, Job Matching, Reports, and Practice History.
- Risk level: low.
- Expected UX benefit: clearer onboarding and retention loop.

### `frontend/src/pages/QuestionBankPage.jsx`

- Current issue: functional, but depends on sidebar visibility for discoverability.
- Proposed improvement: sidebar nav entry already exists; dashboard launcher will expose it more clearly.
- Risk level: low.
- Expected UX benefit: users find practice questions faster.

### `frontend/src/pages/JobMatchingPage.jsx`

- Current issue: flow is improved, but dashboard needs to explain why users should go there.
- Proposed improvement: dashboard feature card and action handoffs remain primary improvements.
- Risk level: low.
- Expected UX benefit: job matching becomes part of the practice loop.

## Validation Checklist

- `npm run build`
- Ensure `/question-bank`, `/interview`, `/chat`, `/job-matching`, `/dashboard` still compile.
- Grep live interview page for removed manual input terms: `typedAnswer`, `textForm`, `text_answer`, `Typed answer`.
- Check sidebar collapsed selectors in CSS.
- Confirm no content is hidden under sidebar/topbar in collapsed state.

