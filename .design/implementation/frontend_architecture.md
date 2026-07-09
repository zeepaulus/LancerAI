# LancerAI Frontend Architecture

Date: July 5, 2026  
Source documents:

- `.design/analysis/reference_research.md`
- `.design/design-system/design-system.md`
- `.design/implementation/component_plan.md`

## Purpose

This document defines the frontend architecture for the LancerAI redesign before implementation. It covers folder structure, route structure, shared layouts, shared components, design tokens, hooks, state management, and component ownership.

This is an architecture proposal only. It does not include React implementation.

## Current Frontend Context

The current frontend is a Vite React application using:

- React 18
- React Router
- CSS in `src/index.css`
- API modules under `src/api`
- Pages under `src/pages`
- A `ThemeContext` under `src/store`

Current routing is mostly flat, with pages such as Dashboard, CV Upload, Job Matching, Interview, Interview Report, Chat, Profile, and Settings.

The redesign should move toward a scalable, feature-oriented architecture that keeps shared primitives stable while allowing AI features to expand.

## Architecture Principles

1. **Feature Ownership With Shared Foundations**  
   Product domains own their page-specific components, hooks, and API adapters. Shared primitives stay in a central design system layer.

2. **Routes Are Thin**  
   Route files should compose layouts and feature containers. Business logic should live in feature hooks, services, and state modules.

3. **AI Is a Platform Layer**  
   AI chat, streaming, evidence, evaluation status, prompt suggestions, and audit events should be reusable across Interview, Candidate, CV Analysis, Job Matching, Reports, and Dashboard.

4. **Object-Centric Modeling**  
   Candidate, Job, Interview, Evaluation, CV, Match, Report, and User should be first-class frontend domains.

5. **Server State and UI State Stay Separate**  
   API data, cache, and mutations should not be mixed with transient UI state such as selected rows, open drawers, filters, and layout density.

6. **Design Tokens Drive Styling**  
   Colors, spacing, typography, shadows, radius, and motion should come from token files rather than page-specific values.

7. **Responsive Behavior Is Planned Per Component**  
   Tables, inspectors, dashboards, transcript viewers, and AI panels must define desktop, tablet, and mobile behavior at the component level.

## Target Folder Structure

```text
frontend/
  public/
  src/
    app/
      App.jsx
      router.jsx
      providers.jsx
      routeGuards.jsx
      errorBoundary.jsx
    assets/
      images/
      logos/
      icons/
    config/
      env.js
      storageKeys.js
      featureFlags.js
      navigation.js
    design-system/
      tokens/
        colors.css
        typography.css
        spacing.css
        radius.css
        shadows.css
        motion.css
        breakpoints.css
        index.css
      primitives/
        Button/
        IconButton/
        Input/
        Textarea/
        Select/
        Checkbox/
        Toggle/
        Badge/
        Tooltip/
        Avatar/
        Modal/
        Drawer/
        DropdownMenu/
        Tabs/
        Table/
        Card/
        Skeleton/
        Toast/
      patterns/
        PageHeader/
        FilterBar/
        CommandMenu/
        EmptyState/
        LoadingState/
        ErrorState/
        MetricCard/
        ChartPanel/
        ActivityTimeline/
        RightInspectorPanel/
        EvidenceCitation/
        AIComposer/
      index.js
    layouts/
      PublicLayout/
      AuthLayout/
      AppShell/
      SettingsLayout/
      SplitInspectorLayout/
      DashboardLayout/
      ConversationLayout/
    routes/
      publicRoutes.jsx
      appRoutes.jsx
      settingsRoutes.jsx
      reportRoutes.jsx
    features/
      auth/
        api/
        components/
        hooks/
        pages/
        state/
        types/
      dashboard/
        api/
        components/
        hooks/
        pages/
        state/
      candidates/
        api/
        components/
        hooks/
        pages/
        state/
      interviews/
        api/
        components/
        hooks/
        pages/
        state/
      cv-analysis/
        api/
        components/
        hooks/
        pages/
        state/
      job-matching/
        api/
        components/
        hooks/
        pages/
        state/
      reports/
        api/
        components/
        hooks/
        pages/
        state/
      settings/
        api/
        components/
        hooks/
        pages/
        state/
      ai/
        api/
        components/
        hooks/
        state/
        prompts/
        utils/
      notifications/
        api/
        components/
        hooks/
        state/
    entities/
      candidate/
        model.js
        normalizers.js
        permissions.js
      job/
      interview/
      evaluation/
      cv/
      match/
      report/
      user/
      workspace/
    services/
      apiClient.js
      endpoints.js
      websocketClient.js
      fileUploadClient.js
      analyticsClient.js
    hooks/
      useBreakpoint.js
      useDebouncedValue.js
      useDisclosure.js
      useLocalStorage.js
      useUrlState.js
      useKeyboardShortcut.js
      usePagination.js
      useSelection.js
      useTableState.js
    state/
      appStore.js
      themeStore.js
      layoutStore.js
      commandMenuStore.js
      userPreferencesStore.js
    utils/
      formatters.js
      validation.js
      dates.js
      scores.js
      accessibility.js
      errors.js
    styles/
      reset.css
      globals.css
      themes.css
    main.jsx
```

## Folder Responsibilities

### `app`

Owns application bootstrapping:

- Router setup.
- Global providers.
- Auth guards.
- Error boundaries.
- Top-level app shell composition.

### `design-system`

Owns reusable UI language:

- Design tokens.
- Primitive components.
- Reusable product patterns.
- Accessibility behavior for shared components.

Feature teams should not fork primitives inside feature folders.

### `layouts`

Owns page-level structure:

- Public marketing/auth layout.
- Protected application shell.
- Settings layout.
- Dashboard layout.
- Split inspector layout.
- Conversation/AI layout.

Layouts should not know feature business logic.

### `features`

Owns domain-specific UX:

- Pages.
- Feature components.
- Feature hooks.
- Feature API adapters.
- Feature-local state.
- Feature-specific empty/loading/error states.

### `entities`

Owns cross-feature data models and helpers:

- Candidate shape and display helpers.
- Interview state definitions.
- Evaluation status rules.
- Match scoring helpers.
- Report permissions.

This layer prevents each feature from inventing its own meaning for shared objects.

### `services`

Owns infrastructure clients:

- HTTP client.
- Endpoint map.
- WebSocket client.
- File upload client.
- Analytics/event client.

### `hooks`

Owns generic reusable hooks that are not tied to a product domain.

### `state`

Owns global client state:

- Theme.
- Layout preferences.
- Command menu visibility.
- User preferences.
- Global selected workspace.

## Route Structure

Use React Router with nested protected routes. The target route model should align with the seven main product areas while preserving public and auth pages.

```text
/
  PublicLayout
    /                       Landing
    /about                  About
    /login                  Login
    /signup                 Signup

/app
  AuthGuard
  AppShell
    /app/dashboard
    /app/interviews
    /app/interviews/:interviewId
    /app/interviews/:interviewId/report
    /app/candidates
    /app/candidates/:candidateId
    /app/candidates/:candidateId/cv
    /app/candidates/:candidateId/interviews
    /app/candidates/:candidateId/evaluation
    /app/candidates/:candidateId/matches
    /app/cv-analysis
    /app/cv-analysis/:cvId
    /app/job-matching
    /app/job-matching/jobs/:jobId
    /app/job-matching/candidates/:candidateId
    /app/reports
    /app/reports/new
    /app/reports/:reportId
    /app/settings
    /app/settings/workspace
    /app/settings/users
    /app/settings/interview
    /app/settings/ai-evaluation
    /app/settings/integrations
    /app/settings/privacy
    /app/settings/notifications
    /app/settings/billing
    /app/settings/audit-logs
```

### Route Rules

- Redirect legacy routes such as `/dashboard`, `/interview`, `/job-matching`, and `/settings` to `/app/...`.
- Keep public pages outside `AppShell`.
- Keep authenticated product pages inside `AppShell`.
- Candidate, interview, report, and CV detail routes should support direct links.
- Route params should identify objects, not UI tabs when possible.
- Tabs inside a detail page can be represented as nested routes when deep linking matters.

## Shared Layouts

### `PublicLayout`

Used by landing, about, login, and signup pages.

Responsibilities:

- Public navbar.
- Public footer when needed.
- Minimal design system dependency.

### `AuthLayout`

Used by login and signup.

Responsibilities:

- Auth card or split auth screen.
- OAuth action placement.
- Auth error states.

### `AppShell`

Used by all protected app routes.

Responsibilities:

- PrimarySidebar.
- TopBar.
- GlobalSearch.
- CommandMenu trigger.
- Notification entry.
- Global AI composer entry.
- Main content outlet.
- Global overlays.

### `DashboardLayout`

Used by dashboard and analytics-heavy reports.

Responsibilities:

- 12-column responsive grid.
- Date range and filter bar placement.
- KPI/chart/table composition.

### `SplitInspectorLayout`

Used by candidates, interviews, CV analysis, and job matching.

Responsibilities:

- Main work area.
- Optional right inspector panel.
- Drawer behavior on tablet/mobile.
- Resizable panel rules on desktop.

### `ConversationLayout`

Used by AI-heavy surfaces such as contextual assistant, interview preparation, and candidate Q&A.

Responsibilities:

- Context header.
- Message/response area.
- Sticky composer.
- Evidence panel.

### `SettingsLayout`

Used by settings routes.

Responsibilities:

- Settings category navigation.
- Main settings form area.
- Sticky save bar.
- Mobile category drawer.

## Shared Components

### Primitives

Primitives should be small, accessible, and style-token driven:

- Button
- IconButton
- Input
- Textarea
- Select
- Combobox
- Checkbox
- RadioGroup
- Toggle
- Badge
- Avatar
- Tooltip
- Modal
- Drawer
- DropdownMenu
- Tabs
- Table
- Card
- Skeleton
- Toast

### Product Patterns

Patterns combine primitives into recurring LancerAI workflows:

- AppSidebar
- TopBar
- PageHeader
- PageToolbar
- FilterBar
- ViewSwitcher
- CommandMenu
- EmptyState
- LoadingState
- ErrorState
- MetricCard
- ChartPanel
- DrillDownTable
- ActivityTimeline
- RightInspectorPanel
- EvidenceCitation
- ConfidenceIndicator
- StatusBadge
- AIComposer
- StreamingResponse
- ProcessingPhaseIndicator
- FileUploadDropzone
- TranscriptViewer
- ScoreBreakdown

### Feature Components

Feature components should stay inside their owning feature:

- CandidateTable
- CandidateBoard
- CandidateDetailPanel
- InterviewSessionView
- VoiceSessionPanel
- EvaluationReportPanel
- CVAnalysisWorkspace
- MatchResultsTable
- ReportBuilderPanel
- SettingsRubricEditor

If a feature component becomes useful in three or more product areas, promote it to `design-system/patterns`.

## Design Tokens

Design tokens should live under `src/design-system/tokens` and compile into global CSS variables.

### Token Categories

- Colors.
- Typography.
- Spacing.
- Radius.
- Shadows.
- Motion.
- Breakpoints.
- Z-index.
- Component sizing.

### Token Naming

Use semantic names, not product references:

- Good: `--color-bg-surface`, `--color-text-primary`, `--color-status-warning`
- Avoid: `--linear-bg`, `--chatgpt-green`, `--vercel-black`

### Token Layers

```text
primitive tokens
  raw values such as spacing scale, font sizes, color values

semantic tokens
  meaning such as background, border, text, success, warning

component tokens
  button height, table row height, sidebar width, panel width
```

### Theme Rules

- Dark mode is primary.
- Light mode should be supported through semantic token overrides.
- Feature components should never hardcode colors.
- Status colors must pair with labels/icons.
- AI states should use shared processing/confidence tokens.

## Hooks

### Global Utility Hooks

These live in `src/hooks`:

- `useBreakpoint` for responsive decisions.
- `useDebouncedValue` for search and filters.
- `useDisclosure` for modals/drawers.
- `useLocalStorage` for persisted preferences.
- `useUrlState` for filters and tabs in URLs.
- `useKeyboardShortcut` for command menu and productivity actions.
- `usePagination` for paginated data.
- `useSelection` for bulk table selection.
- `useTableState` for sorting, filters, density, and columns.

### Feature Hooks

These live in each feature folder:

- `useDashboardMetrics`
- `useCandidateList`
- `useCandidateDetail`
- `useCandidateActions`
- `useInterviewQueue`
- `useInterviewSession`
- `useTranscript`
- `useEvaluation`
- `useCVAnalysis`
- `useJobMatching`
- `useReportBuilder`
- `useSettingsForm`

### AI Hooks

These live in `features/ai/hooks`:

- `useAIComposer`
- `useStreamingResponse`
- `usePromptSuggestions`
- `useEvidenceCitations`
- `useAIProcessingState`
- `useAIAuditTrail`
- `useVoiceTurnState`

AI hooks should be context-aware. They should accept candidate, job, interview, CV, report, or dashboard context without being tied to one page.

## State Management

### Recommended State Categories

| State Type | Examples | Owner |
| --- | --- | --- |
| Server state | candidates, jobs, interviews, evaluations, reports | feature API/query layer |
| Global UI state | theme, sidebar collapsed, command menu open | global app state |
| Feature UI state | selected rows, open panels, local filters | feature state/hooks |
| URL state | active tab, filters, search, date range | route/query params |
| AI session state | composer draft, streaming output, active context | AI feature state |
| Form state | settings, report builder, rubric editor | feature form hooks |

### State Rules

- Keep API data out of global UI stores.
- Keep filters that should be shareable in the URL.
- Keep temporary modal/drawer state local unless multiple unrelated components need it.
- Persist user preferences such as theme, density, sidebar collapse, and last selected workspace.
- AI streaming state should support cancellation, retry, and resumable context where backend support exists.

### Suggested Libraries

The current app has minimal dependencies. For scale, consider:

- React Query or TanStack Query for server state.
- Zustand or a small Context-based store for global UI state.
- React Hook Form for complex settings and report forms.

Do not introduce all state libraries at once. Add them when implementation scope requires them.

## API Architecture

### API Layer Structure

Each feature should expose intent-based API functions:

```text
features/candidates/api/
  candidatesApi.js
features/interviews/api/
  interviewsApi.js
features/ai/api/
  aiApi.js
services/
  apiClient.js
  endpoints.js
  websocketClient.js
```

### API Rules

- `services/apiClient` owns auth headers, base URL, timeouts, errors, and response parsing.
- `services/endpoints` owns route construction.
- Feature API modules own domain-specific calls.
- Normalizers in `entities` convert backend payloads to frontend-ready shapes.
- WebSocket and streaming concerns should live in service or AI feature layers, not page components.

## AI Feature Scalability

AI features should be designed as a cross-cutting layer.

### AI Context Model

An AI context should describe what the assistant is working with:

- `workspace`
- `candidate`
- `job`
- `interview`
- `cv`
- `evaluation`
- `report`
- `dashboard`

Every contextual AI action should declare:

- Current object context.
- Allowed tools/actions.
- Available evidence.
- User intent.
- Output target.

### AI Surface Types

- Global assistant drawer.
- Candidate assistant.
- Interview assistant.
- CV analysis assistant.
- Job matching assistant.
- Report summarizer.
- Dashboard insight generator.
- Voice interview assistant.

### AI Components

AI components should be reusable:

- AIComposer
- PromptSuggestionList
- StreamingResponse
- AIProcessingPhase
- EvidenceCitationList
- ConfidenceIndicator
- HumanOverrideControl
- AIAuditEvent
- SourceAttachmentList

### AI State Requirements

- Streaming output.
- Processing phase.
- Cancellation.
- Retry.
- Error recovery.
- Evidence mapping.
- Human feedback.
- Audit history.
- Generated artifact versioning.

### AI Governance Requirements

- Always show confidence for evaluations and matches.
- Always show evidence for hiring-related recommendations.
- Track human overrides.
- Keep generated reports versioned.
- Separate AI recommendation from human decision.
- Avoid hidden AI mutations; show before applying AI-generated changes.

## Component Ownership

### Design System Team/Layer

Owns:

- Tokens.
- Primitive components.
- Shared patterns.
- Accessibility behavior.
- Visual consistency.
- Component documentation.

Examples:

- Button.
- Table.
- Modal.
- Badge.
- AIComposer shell.
- RightInspectorPanel.
- EmptyState.

### Dashboard Feature

Owns:

- Dashboard page.
- Dashboard metric composition.
- Recruiting funnel widgets.
- AI quality dashboard widgets.
- Dashboard-specific filters.

Shared ownership with Reports for chart/table primitives.

### Interviews Feature

Owns:

- Interview queue.
- Interview session view.
- Voice controls.
- Transcript viewer domain behavior.
- Interview evaluation review.
- Interview report entry points.

Shared ownership with AI for voice/processing states.

### Candidates Feature

Owns:

- Candidate table.
- Candidate board.
- Candidate detail panel.
- Candidate timeline.
- Candidate actions and bulk actions.
- Candidate comparison.

Shared ownership with CV Analysis, Interview, and Job Matching for embedded panels.

### CV Analysis Feature

Owns:

- CV upload flow.
- Parsed profile view.
- Skills matrix.
- Experience timeline.
- CV evidence mapping.
- CV-to-job analysis workspace.

Shared ownership with AI for extraction/explanation states.

### Job Matching Feature

Owns:

- Matching mode controls.
- Match result table.
- Criteria weighting.
- Match explanation.
- Alternative roles.
- Match decision bar.

Shared ownership with Candidates for shortlist/reject/invite actions.

### Reports Feature

Owns:

- Report library.
- Report builder.
- Report preview.
- Export/share/schedule flows.
- Saved report history.

Shared ownership with Dashboard for chart blocks and summary panels.

### Settings Feature

Owns:

- Workspace settings.
- Users and roles.
- Interview defaults.
- AI evaluation configuration.
- Integrations.
- Privacy and retention.
- Notifications.
- Billing.
- Audit logs.

Shared ownership with AI for rubric/evaluation configuration.

## Navigation Architecture

### Navigation Source of Truth

Navigation should be config-driven from `src/config/navigation.js`.

Each nav item should define:

- Label.
- Route.
- Icon.
- Permission requirement.
- Badge source.
- Feature flag.
- Active route matcher.

### Navigation Rules

- Sidebar navigation should not be hardcoded per page.
- Badge counts should come from a shared notification/review queue source.
- Saved views and pinned jobs should be user-specific dynamic sections.
- Settings navigation should be separate from primary app navigation.
- Mobile navigation should prioritize Dashboard, Candidates, Interviews, and Inbox/Review.

## Route-Level Data & Error Handling

### Loading

Use route-level loading states for full-page fetches:

- Dashboard skeleton.
- Candidate table skeleton.
- Interview session loading.
- Report preview loading.

### Errors

Use consistent route-level error surfaces:

- Unauthorized.
- Not found.
- Network unavailable.
- AI service unavailable.
- Permission denied.

### Empty States

Every route should define an empty state:

- No candidates.
- No interviews.
- No CV uploaded.
- No matches.
- No reports.
- No settings data.

## Responsive Architecture

### Breakpoint Behavior

- Desktop: sidebar + main + optional inspector.
- Tablet: sidebar collapses; inspector becomes drawer.
- Mobile: bottom navigation or compact menu; detail routes become full pages.

### Component-Level Rules

- Tables become cards on mobile.
- Boards scroll horizontally on tablet and mobile.
- Right inspectors become drawers below desktop.
- Dashboard grids stack by priority.
- Live interview controls remain sticky.
- AI composer remains reachable without covering critical evidence.

## Accessibility Architecture

Accessibility should be owned at both primitive and feature levels.

### Primitive Responsibilities

- Keyboard support.
- Focus management.
- ARIA labels.
- Modal trapping.
- Tooltip labeling.
- Reduced motion support.

### Feature Responsibilities

- Evidence descriptions for AI recommendations.
- Chart summaries.
- Transcript speaker labeling.
- Voice state text equivalents.
- Table header semantics.
- High-stakes confirmation flows.

## Migration Plan

### Phase 1: Foundations

- Create target folders without changing behavior.
- Move app bootstrapping into `src/app`.
- Introduce token files.
- Add AppShell, PrimarySidebar, TopBar, PageHeader, and shared layout definitions.
- Keep existing routes working.

### Phase 2: Shared Design System

- Build primitives and shared patterns.
- Replace page-level ad hoc styling with tokens.
- Standardize buttons, cards, badges, tables, modals, loading, and empty states.

### Phase 3: Feature Reorganization

- Move existing pages into feature folders.
- Split large pages into feature components.
- Move API calls into feature API modules.
- Create entity helpers for candidates, jobs, interviews, CVs, evaluations, matches, and reports.

### Phase 4: AI Platform Layer

- Add `features/ai`.
- Standardize AI composer, streaming response, evidence citations, confidence indicators, and audit events.
- Connect AI layer to Candidate, Interview, CV Analysis, Job Matching, Dashboard, and Reports.

### Phase 5: Advanced Scale

- Add server-state caching library if needed.
- Add report builder architecture.
- Add saved views and URL-state filters.
- Add role-based permissions and feature flags.
- Add richer telemetry and analytics events.

## Future AI Feature Readiness

The architecture should support:

- AI-generated interview question sets.
- AI live interview assistance.
- Transcript-based scoring.
- Candidate/job Q&A.
- CV-to-role comparison.
- Match explanation and criteria weighting.
- Report summarization.
- Dashboard insight generation.
- Bias/risk review workflows.
- Human override and audit history.
- Multi-model or model-version evaluation tracking.

## Final Recommendation

The target frontend should evolve from a flat page-based app into a feature-owned, design-system-led application. The most important architectural decision is to treat AI as a reusable platform layer rather than a single chat page. That will let LancerAI scale from current CV, matching, and interview flows into a full hiring intelligence workspace without rewriting the frontend every time a new AI capability is added.
