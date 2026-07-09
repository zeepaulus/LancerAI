# LancerAI Frontend Redesign Plan

Date: July 7, 2026  
Stack: React 18, Vite, React Router DOM, JavaScript ES Modules.

## Assumptions

- Do not add UI/state libraries.
- Do not change backend logic or API contracts.
- Preserve existing routes.
- Existing dirty frontend work is treated as the current baseline.
- Candidate/job analytics must use existing APIs and local state only.

## Global Shell / Shared Components

- Current problem: Good shell exists, but detailed pages still bypass some shared primitives.
- Design goal: Make all app pages feel like one AI SaaS product.
- Components to update: `AppUI`, `Visuals`, page-level usage.
- Components to create: only small primitives if they reduce duplicate alert/AI panel patterns.
- Files likely to change: `frontend/src/components/Common/AppUI.jsx`, `frontend/src/index.css`.
- Risk: Low.
- Expected improvement: Consistent panels, states, and report surfaces.

## Dashboard

- Current problem: Mostly resolved; future charting can improve analytics depth.
- Design goal: Preserve operational overview.
- Components to update: none in this pass.
- Components to create: future chart primitive.
- Files likely to change: `MainDashboard.jsx` only if polishing.
- Risk: Low.
- Expected improvement: Already strong.

## Voice Interview Flow

- Current problem: Setup page is strong; live room needs better a11y and state semantics.
- Design goal: Make the live AI interview feel controlled, transparent, and report-ready.
- Components to update: `ChatPage`, `InterviewPage` modal labels/errors.
- Components to create: none required.
- Files likely to change: `ChatPage.jsx`, `InterviewPage.jsx`.
- Risk: Medium because WebSocket/audio/camera logic must remain untouched.
- Expected improvement: Clearer AI state, better error recovery, better keyboard/screen-reader support.

## Candidate / Interview Management

- Current problem: Candidate rows are derived from interview sessions because no candidate API exists.
- Design goal: Keep a professional pipeline surface without inventing backend data.
- Components to update: none in this pass unless build issues appear.
- Components to create: none.
- Files likely to change: `CandidatePage.jsx`.
- Risk: Low.
- Expected improvement: Already acceptable for demo.

## CV Analysis / Optimization

- Current problem: Upload page is polished; optimization detail page still looks legacy.
- Design goal: Make CV optimization evidence-first with clear review-before-accepting sections.
- Components to update: `CVOptimizationPage`.
- Components to create: use existing `Panel`, `StatusBadge`, `ScoreBar`, and `MetricCard`.
- Files likely to change: `CVOptimizationPage.jsx`.
- Risk: Medium because it calls optimization/download APIs.
- Expected improvement: Better scanability, stronger AI guidance framing, cleaner loading/error states.

## Job Matching

- Current problem: Main matching page is strong; recommendations page is simpler.
- Design goal: Preserve current flow, future polish recommendations.
- Components to update: none in this pass.
- Components to create: none.
- Files likely to change: `JobMatchingPage.jsx`, `JobRecommendationsPage.jsx`.
- Risk: Low.
- Expected improvement: Already acceptable.

## Reports / Analytics

- Current problem: Report library is good; report detail page is still legacy and narrow.
- Design goal: Make interview reports feel like evidence-backed analytics.
- Components to update: `InterviewReportPage`.
- Components to create: use existing panels/metrics/score bars.
- Files likely to change: `InterviewReportPage.jsx`.
- Risk: Medium because route can receive either `report` or `sessionId`.
- Expected improvement: Faster report scanning and clearer AI confidence/evidence structure.

## Navigation / Layout Consistency

- Current problem: Mostly solved by sidebar/topbar; some legacy pages use custom containers.
- Design goal: Use `Page`, `PageHeader`, `Panel`, and shared classes consistently.
- Components to update: detail pages.
- Components to create: none.
- Files likely to change: `CVOptimizationPage.jsx`, `InterviewReportPage.jsx`.
- Risk: Low.
- Expected improvement: Less visual drift.

## Validation Plan

- Run `npm run build` in `frontend`.
- Fix broken imports/routes/build errors.
- Check dynamic error regions and labels in the touched forms.
- Avoid backend test/build changes unless frontend build reveals contract misuse.
