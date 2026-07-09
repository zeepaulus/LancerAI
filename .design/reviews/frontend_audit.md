# LancerAI Frontend Audit

Date: July 7, 2026  
Scope: React 18 + Vite frontend, routes, shared UI primitives, CSS tokens, visual placeholders, and API usage.

## Current Strengths

- The app already has a strong SaaS shell: fixed sidebar, topbar, navigation groups, active route states, profile menu, and theme toggle.
- Shared primitives exist in `frontend/src/components/Common/AppUI.jsx`: `Page`, `PageHeader`, `Panel`, `MetricCard`, `StatusBadge`, `EmptyState`, `ScoreBar`, and skeleton rows.
- Visual placeholders exist in `frontend/src/components/Common/Visuals.jsx` and are lightweight, original, and product-specific.
- Dashboard, Interview queue, Candidate, Reports, CV Upload, and Job Matching already use the new shell and reusable primitives.
- API calls are centralized in `frontend/src/api/*`, and current route contracts are preserved.
- Loading, empty, and error states exist in most high-traffic flows.

## Current Weaknesses

- `CVOptimizationPage.jsx` and `InterviewReportPage.jsx` still use a legacy narrow layout, many inline one-off styles, mixed Vietnamese/English labels, and less consistent report hierarchy.
- `ChatPage.jsx` is functional and ambitious, but live error/status messages are mostly visual and need stronger accessibility semantics.
- Form labels in the interview creation modal are visual wrappers rather than explicit `htmlFor` labels.
- Some pages still rely on derived/local data because backend APIs for first-class candidates, jobs, and analytics are not available.
- Navigation is desktop-first; mobile behavior is acceptable but not fully optimized for dense workflow screens.
- Several detailed pages use local color literals that can fight the dark/light theme.

## High-Priority UI/UX Problems

- Voice Interview must clearly communicate state: connecting, listening, processing, speaking, ended, error, and report-ready.
- AI outputs need evidence framing so users understand generated content as guidance, not automatic truth.
- Reports need faster scanning: score summary, behavior signals, scorecard, STAR, transcript, and next actions.
- CV Optimization needs a stronger “review before accepting” flow for rewrite suggestions and issues.
- Error states need `role="alert"` or `aria-live` where users are blocked.

## Pages / Components Needing Redesign

- Major polish: `InterviewReportPage.jsx`, `CVOptimizationPage.jsx`
- Focused polish: `ChatPage.jsx`, `InterviewPage.jsx`
- Preserve with minor future improvements: `MainDashboard.jsx`, `CandidatePage.jsx`, `ReportsPage.jsx`, `CVUploadPage.jsx`, `JobMatchingPage.jsx`, `JobRecommendationsPage.jsx`
- Preserve core shell: `Navbar.jsx`, `AppUI.jsx`, `Visuals.jsx`

## Pages / Components To Preserve

- `Navbar.jsx`: good Linear-inspired app shell.
- `AppUI.jsx`: good primitive layer; extend instead of replacing.
- `Visuals.jsx`: good lightweight product visuals; no stock assets needed.
- `MainDashboard.jsx`: good operational overview.
- `InterviewPage.jsx`: good session setup and queue model.
- `JobMatchingPage.jsx`: clear AI scoring and gap explanation.

## Risks Before Implementation

- The working tree already contains frontend changes; edits should build on them and avoid reverting unrelated work.
- No new UI libraries should be added, so improvements must use CSS, existing components, and inline styles where practical.
- Live interview code touches WebSocket/audio/camera behavior; changes should avoid business logic and keep UI-only where possible.
- Backend contracts must remain unchanged; candidate/job analytics screens must not invent unsupported API calls.
- Vite dependency currently requires a modern Node version; build validation is required after UI work.
