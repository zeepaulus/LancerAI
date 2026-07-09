# LancerAI Design System Proposal

Date: July 5, 2026  
Basis: `.design/analysis/reference_research.md`  
Influence mix: 50% Linear, 30% ChatGPT, 20% Vercel

## Design Direction

LancerAI should feel like a high-trust AI hiring operations system: fast, calm, structured, and evidence-driven. The product should combine Linear's dense workflow clarity, ChatGPT's approachable AI interaction model, and Vercel's precise dashboard discipline.

The design language should not feel like a generic SaaS template. It should feel like a professional workbench for recruiters, hiring managers, and interview operators who need to move quickly while trusting AI-assisted decisions.

## Core Principles

1. **Operational First**  
   Candidates, jobs, interviews, evaluations, and matches are the core objects. The interface should make these objects easy to scan, filter, compare, and act on.

2. **AI Is Embedded, Not Separate**  
   AI should appear inside candidate timelines, evaluation reports, job matching views, and interview workflows. A global assistant is useful, but AI should not live only in a chat page.

3. **Evidence Before Recommendation**  
   Scores and recommendations must be paired with transcript excerpts, CV evidence, rubric criteria, confidence levels, and human override history.

4. **Calm Density**  
   Use compact layouts for work management, but preserve enough spacing for long reading sessions and AI-generated summaries.

5. **Status Is a First-Class UI Element**  
   Voice processing, transcript readiness, evaluation progress, match confidence, interview stage, and review risk should all have clear visual states.

6. **Dashboards Must Lead to Action**  
   Analytics should answer what needs attention, not only show charts.

## Color Tokens

The palette is neutral-first with meaningful semantic accents. It should be professional, slightly futuristic, and accessible. Avoid copying the black-and-white severity of Vercel or the exact dark mood of Linear; LancerAI gets its own "clinical graphite + signal teal" identity.

### Base Palette

| Token | Value | Usage |
| --- | --- | --- |
| `color-bg-app` | `#0E1116` | Primary dark app background |
| `color-bg-surface` | `#151A21` | Panels, sidebars, cards |
| `color-bg-surface-raised` | `#1B222B` | Elevated panels, popovers |
| `color-bg-muted` | `#202833` | Hover surfaces, inactive controls |
| `color-bg-inset` | `#0A0D12` | Deep canvases, transcript wells, code/log-like areas |
| `color-border-subtle` | `#26303B` | Default borders |
| `color-border-strong` | `#394656` | Active panels, table separators |
| `color-text-primary` | `#F3F6FA` | Main text |
| `color-text-secondary` | `#AAB4C0` | Secondary text |
| `color-text-muted` | `#737F8C` | Metadata, timestamps |
| `color-text-disabled` | `#4F5A66` | Disabled labels and controls |
| `color-white` | `#FFFFFF` | Pure contrast when required |
| `color-black` | `#000000` | Overlays and technical contrast |

### Brand & Accent Palette

| Token | Value | Usage |
| --- | --- | --- |
| `color-brand-primary` | `#35D0BA` | Primary action, active navigation, AI signal |
| `color-brand-primary-hover` | `#4ADFCC` | Primary hover |
| `color-brand-primary-muted` | `#153B38` | Soft selected backgrounds |
| `color-brand-secondary` | `#8FA7FF` | Secondary AI/context accent |
| `color-brand-secondary-muted` | `#242C55` | Secondary selected backgrounds |
| `color-accent-cv` | `#7CC7FF` | CV analysis |
| `color-accent-voice` | `#B58CFF` | Voice interview |
| `color-accent-match` | `#7EE787` | Job matching |
| `color-accent-analytics` | `#FFD166` | Analytics and insights |

### Semantic Palette

| Token | Value | Usage |
| --- | --- | --- |
| `color-success` | `#4FD17A` | Passed, completed, ready |
| `color-warning` | `#F5C451` | Needs review, medium confidence |
| `color-danger` | `#FF6B6B` | Failed, rejected, blocked, high risk |
| `color-info` | `#65B7FF` | Informational states |
| `color-processing` | `#B58CFF` | AI processing, transcription, evaluation running |
| `color-neutral` | `#8B97A5` | Unknown, not started, no data |

### Light Mode Palette

Light mode should support review-heavy workflows and presentations, but dark mode should be the primary design target.

| Token | Value | Usage |
| --- | --- | --- |
| `color-light-bg-app` | `#F7F8FA` | Primary light background |
| `color-light-bg-surface` | `#FFFFFF` | Cards and panels |
| `color-light-bg-muted` | `#EEF1F5` | Hover and muted regions |
| `color-light-border-subtle` | `#DDE3EA` | Borders |
| `color-light-text-primary` | `#111827` | Main text |
| `color-light-text-secondary` | `#4B5563` | Secondary text |
| `color-light-text-muted` | `#7A8491` | Metadata |

### Color Usage Rules

- Use neutral surfaces for most UI. Accent color should identify state, ownership, or action.
- Use teal for LancerAI intelligence and primary action only.
- Use purple for active AI processing and voice workflows.
- Use green only for positive completion or strong match signals.
- Use warning and danger sparingly; hiring risk indicators must be noticeable but not alarmist.
- Never rely on color alone. Pair semantic color with text, icon, or status label.

## Typography Scale

Typography should support dense operations and readable AI-generated content. Use a neutral sans-serif with excellent UI legibility. Recommended families: Inter, Geist, or a similar modern system UI font. Use a monospace font only for transcripts with timestamps, IDs, audit logs, API-like events, or structured evidence.

### Font Families

| Token | Value | Usage |
| --- | --- | --- |
| `font-sans` | Inter or system sans | Main UI |
| `font-mono` | Geist Mono, JetBrains Mono, or system mono | Logs, IDs, timestamps, transcript markers |

### Type Scale

| Token | Size | Line Height | Weight | Usage |
| --- | ---: | ---: | ---: | --- |
| `text-display` | 32px | 40px | 650 | Page-level insight titles, not routine panels |
| `text-title-1` | 24px | 32px | 650 | Primary page titles |
| `text-title-2` | 20px | 28px | 600 | Section headers, modal titles |
| `text-title-3` | 18px | 26px | 600 | Panel headers, report titles |
| `text-body-lg` | 16px | 26px | 400 | AI summaries, long reading |
| `text-body` | 14px | 22px | 400 | Default UI body |
| `text-body-medium` | 14px | 22px | 550 | Important labels, row titles |
| `text-small` | 13px | 20px | 400 | Dense tables, sidebar labels |
| `text-caption` | 12px | 16px | 450 | Metadata, timestamps, helper text |
| `text-micro` | 11px | 14px | 550 | Badges, compact table labels |
| `text-mono` | 12px | 18px | 400 | Transcript timestamps, logs |

### Typography Rules

- Use `14px` as the default operational UI size.
- Use `16px` for AI-generated explanations, interview summaries, and evaluation narratives.
- Do not use hero-scale typography inside dashboards, sidebars, cards, tables, or interview controls.
- Keep letter spacing at `0` except uppercase micro labels, which may use `0.02em`.
- Use weight changes before size changes when creating hierarchy in compact surfaces.
- Long AI content should have comfortable line height and a max readable width.

## Spacing System

Use a 4px base spacing system with selected larger layout values.

| Token | Value | Usage |
| --- | ---: | --- |
| `space-0` | 0px | Reset |
| `space-1` | 4px | Tight icon/text gaps |
| `space-2` | 8px | Default compact gap |
| `space-3` | 12px | Row padding, form gaps |
| `space-4` | 16px | Card padding, toolbar groups |
| `space-5` | 20px | Panel padding |
| `space-6` | 24px | Section spacing |
| `space-8` | 32px | Page section spacing |
| `space-10` | 40px | Large layout spacing |
| `space-12` | 48px | Major page separation |
| `space-16` | 64px | Dashboard band spacing |

### Spacing Rules

- Dense lists and tables use `8px` to `12px` vertical rhythm.
- Cards and panels use `16px` to `20px` inner padding.
- Dashboard grids use `16px` gutters on desktop.
- AI reading surfaces use slightly larger vertical spacing than operational tables.
- Sidebar rows should remain compact: `32px` to `36px` high.
- Table rows should default to `40px` compact and `48px` comfortable.

## Border Radius

The radius language should be precise and professional. Avoid overly soft, pill-heavy SaaS styling.

| Token | Value | Usage |
| --- | ---: | --- |
| `radius-none` | 0px | Dividers, tables, full-bleed regions |
| `radius-xs` | 3px | Badges, status markers |
| `radius-sm` | 5px | Inputs, compact buttons, table controls |
| `radius-md` | 8px | Cards, panels, menus |
| `radius-lg` | 12px | Modals, assistant composer, larger overlays |
| `radius-pill` | 999px | Avatars, tiny status pills only |

### Radius Rules

- Default component radius is `5px` or `8px`.
- Use `12px` only for high-focus surfaces such as modals, command menus, and AI composer containers.
- Do not nest rounded cards inside rounded cards.
- Status badges may be pill-shaped only when compact and metadata-like.

## Shadows & Elevation

Use borders first, shadows second. The interface should feel layered but not floaty.

| Token | Value | Usage |
| --- | --- | --- |
| `shadow-none` | none | Default surfaces |
| `shadow-sm` | `0 1px 2px rgba(0, 0, 0, 0.24)` | Subtle raised controls |
| `shadow-md` | `0 8px 24px rgba(0, 0, 0, 0.28)` | Dropdowns, popovers |
| `shadow-lg` | `0 18px 48px rgba(0, 0, 0, 0.36)` | Modals, command palette |
| `shadow-focus` | `0 0 0 3px color-mix(in srgb, var(--color-brand-primary), transparent 72%)` | Keyboard focus ring |
| `shadow-danger-focus` | `0 0 0 3px rgba(255, 107, 107, 0.24)` | Destructive focus |

### Elevation Rules

- Default panels use a border, not a shadow.
- Popovers and command menus may use `shadow-md`.
- Modals may use `shadow-lg` plus a dim overlay.
- Focus states must be visible in both dark and light modes.

## Grid System

The grid should support operational dashboards, candidate lists, split detail views, and AI reading surfaces.

### Desktop Application Shell

| Region | Width |
| --- | ---: |
| Primary sidebar | 240px |
| Collapsed sidebar | 64px |
| Main content min | 720px |
| Right detail panel | 360px to 440px |
| Assistant/evidence panel | 400px to 520px |
| Page max width for reading | 960px |
| Dashboard max width | 1440px |

### Dashboard Grid

- Use a 12-column grid on desktop.
- Gutter: `16px`.
- Page padding: `24px` desktop, `16px` tablet, `12px` mobile.
- KPI cards: 3 columns on desktop, 2 on tablet, 1 on mobile.
- Charts: 6 or 8 columns depending on importance.
- Tables: full width unless paired with a compact insight panel.

### Work Surface Layouts

| Layout | Usage |
| --- | --- |
| `sidebar + main` | Default simple views |
| `sidebar + main + detail` | Candidate, job, interview detail |
| `sidebar + board` | Candidate pipeline |
| `sidebar + table + inspector` | Bulk review and triage |
| `centered conversation` | AI assistant and interview prep |
| `split AI artifact` | AI chat plus evaluation report, script, or CV summary |
| `dashboard grid` | Analytics and executive overview |

## Component Variants

### Buttons

| Variant | Usage |
| --- | --- |
| Primary | Main action: start interview, invite candidate, generate evaluation |
| Secondary | Common actions: edit job, add note, export |
| Ghost | Toolbar and low-emphasis actions |
| Tertiary icon | Compact row actions, panel controls |
| Destructive | Reject candidate, delete interview, remove file |
| AI Action | Generate, summarize, analyze, recommend; uses brand accent and sparkle/AI icon sparingly |

Rules:

- Primary buttons should be rare per surface.
- Button labels should be action verbs.
- Icon-only buttons require tooltips.
- Destructive actions require confirmation when irreversible.

### Inputs & Forms

Variants:

- Text input.
- Search input.
- Textarea.
- Select.
- Multi-select.
- Combobox.
- Date/time picker.
- Toggle.
- Checkbox.
- Radio group.
- File upload/dropzone.
- Voice input control.

Rules:

- Use inline validation for missing or invalid values.
- Use helper text for high-stakes fields like evaluation rubrics.
- Long setup flows should be divided into sections, not decorative cards.
- AI-fill actions should show what changed before applying.

### Cards

Variants:

- Candidate card.
- Job card.
- Interview session card.
- Evaluation card.
- KPI card.
- Insight card.
- Empty state card.
- AI evidence card.

Rules:

- Cards must represent a real object or insight.
- Cards should not be used as generic page wrappers.
- Candidate cards should show name, role, stage, match score, owner, next action, and risk/review state.
- Evaluation cards should always show confidence and evidence access.

### Tables

Variants:

- Candidate table.
- Job table.
- Interview table.
- Evaluation table.
- Audit log table.
- Analytics drill-down table.

Required table features:

- Sort.
- Filter.
- Search.
- Column visibility.
- Row selection.
- Bulk actions.
- Sticky header for long datasets.
- Empty, loading, and error states.

Rules:

- Use compact density by default for operations.
- Provide comfortable density for executive or review modes.
- Use status and score columns consistently.
- Avoid hiding critical decision data behind hover-only controls.

### Status Badges

Core statuses:

- `Not started`
- `Invited`
- `Scheduled`
- `In interview`
- `Transcribing`
- `Evaluating`
- `Needs review`
- `Shortlisted`
- `Rejected`
- `Offer`
- `Hired`
- `Archived`

AI statuses:

- `Ready`
- `Processing`
- `Low confidence`
- `Evidence missing`
- `Human overridden`
- `Rerun available`

Rules:

- Badges combine text, color, and optional icon.
- Use muted backgrounds with readable foregrounds.
- Never use a score color without a label.

### AI Composer

Variants:

- Global assistant composer.
- Candidate-specific composer.
- Job-specific composer.
- Evaluation review composer.
- Voice interview prompt composer.

Rules:

- Composer should accept text, file context, and candidate/job references.
- It should show current context clearly: candidate, job, interview, transcript, or dashboard.
- Suggested prompts should be contextual, not generic.
- Streaming responses should show working state and source evidence when available.

### Detail Panels

Variants:

- Candidate inspector.
- Job inspector.
- Interview inspector.
- Evaluation inspector.
- Evidence inspector.

Rules:

- Right panels should be scannable and action-oriented.
- Top area shows identity and status.
- Middle area shows key metadata and AI summary.
- Bottom area shows timeline, notes, evidence, or activity.
- Panels can be resized on desktop when reading transcripts or reports.

### Charts

Variants:

- KPI tile.
- Line chart.
- Bar chart.
- Funnel chart.
- Distribution chart.
- Confidence/risk breakdown.
- Time-to-hire trend.

Rules:

- Every chart needs a plain-language title.
- Every chart should answer one question.
- Use semantic colors consistently.
- Allow drill-down from chart to filtered table.
- Avoid decorative charts that do not support a decision.

### Empty States

Variants:

- No candidates.
- No interviews.
- No CV uploaded.
- No analytics data.
- No search results.
- No evaluation yet.

Rules:

- State what is missing.
- Explain why it matters in one sentence.
- Provide one primary next action.
- Keep illustration optional and restrained.

### Loading States

Variants:

- Skeleton rows.
- Skeleton cards.
- Streaming AI response.
- Voice listening/processing.
- Transcript generation.
- Evaluation running.
- Chart loading.

Rules:

- Preserve layout during loading.
- For AI tasks, show the current phase.
- For long tasks, allow the user to leave and return.
- Avoid full-screen spinners except for initial app boot.

## Navigation Rules

### Primary Sidebar

Recommended sections:

1. **Home**
2. **Inbox**
3. **Candidates**
4. **Jobs**
5. **Interviews**
6. **Evaluations**
7. **Job Matching**
8. **Analytics**
9. **Saved Views**
10. **Settings**

Rules:

- Sidebar is persistent on desktop.
- Highlight active section with brand-muted background and brand-primary indicator.
- Include counts where attention is needed, such as interviews pending review.
- Saved views should appear below primary navigation.
- Favorites or pinned jobs should be supported for high-volume recruiters.

### Secondary Navigation

Use tabs inside major objects:

- Candidate: Overview, CV, Interviews, Evaluation, Matches, Activity.
- Job: Overview, Pipeline, Rubric, Candidates, Analytics, Settings.
- Interview: Session, Transcript, Evaluation, Evidence, Notes.
- Analytics: Funnel, Interviews, Evaluation Quality, Matching, Sources.

Rules:

- Tabs are for sibling views within the same object.
- Do not use tabs for unrelated modules.
- Keep tab labels short and stable.

### Command Menu

The command menu should support:

- Search candidates.
- Search jobs.
- Open interviews.
- Run common actions.
- Create job.
- Invite candidate.
- Start voice interview.
- Generate evaluation.
- Navigate to saved views.

Rules:

- Command menu should rank recent and active work first.
- Results should show object type, status, and owner.
- Keyboard access should be available from anywhere.

### Search

Search modes:

- Global search.
- Current view search.
- Candidate database search.
- Transcript search.
- Analytics/filter search.

Rules:

- Global search retrieves objects.
- View search filters the current table/board.
- Transcript search highlights evidence.
- Search results should be actionable, not just navigational.

## Dashboard Principles

Dashboards should combine Vercel-like clarity with Linear-like operational relevance.

### Dashboard Types

1. **Recruiting Overview**
   - Active jobs.
   - Candidates by stage.
   - Interviews scheduled/completed.
   - Pending evaluations.
   - Bottlenecks.

2. **Candidate Funnel**
   - Sourced to hired funnel.
   - Drop-off by stage.
   - Time in stage.
   - Source quality.

3. **Interview Operations**
   - Completion rate.
   - Average duration.
   - No-show rate.
   - Transcript failure rate.
   - Pending human reviews.

4. **AI Evaluation Quality**
   - Confidence distribution.
   - Human override rate.
   - Criteria-level score trends.
   - Low-evidence evaluations.
   - Rerun frequency.

5. **Job Matching**
   - Match score distribution.
   - Top matching candidates.
   - Criteria gaps.
   - Role demand vs candidate supply.

6. **Executive Analytics**
   - Hiring velocity.
   - Conversion by role.
   - Offer acceptance.
   - Team workload.
   - Quality signals.

### Dashboard Rules

- Place urgent operational metrics first.
- Every metric should have a drill-down path.
- Pair aggregate metrics with the list of affected candidates/jobs.
- Show timeframe and filters persistently.
- Use comparison deltas only when the baseline is clear.
- Use charts for trends and distribution, tables for decisions.
- Show data freshness and loading status.
- Empty dashboards should explain what setup or activity is required.

## Animation Principles

Motion should communicate state, continuity, and AI progress. It should never feel decorative or slow.

### Timing Tokens

| Token | Duration | Usage |
| --- | ---: | --- |
| `motion-instant` | 80ms | Pressed states, small controls |
| `motion-fast` | 120ms | Hover, focus, badge changes |
| `motion-standard` | 180ms | Menus, tabs, panel changes |
| `motion-slow` | 260ms | Modals, larger panels |
| `motion-ai-stream` | Continuous | Streaming text, transcript generation |

### Easing

| Token | Usage |
| --- | --- |
| `ease-standard` | Default transitions |
| `ease-out` | Menus and panels entering |
| `ease-in` | Elements exiting |
| `ease-linear` | Progress bars, live audio levels |

### Motion Rules

- Use fast transitions for workflow actions.
- Use streaming and phase indicators for AI work.
- Use subtle row highlights when data updates.
- Respect reduced motion preferences.
- Avoid decorative background animation.
- Voice interview animation should focus on input confidence, listening, and turn-taking.

## Responsive Breakpoints

Breakpoints should support desktop-first operations while preserving core mobile tasks.

| Token | Width | Target |
| --- | ---: | --- |
| `breakpoint-xs` | 360px | Small mobile |
| `breakpoint-sm` | 640px | Mobile |
| `breakpoint-md` | 768px | Large mobile/tablet |
| `breakpoint-lg` | 1024px | Tablet/small laptop |
| `breakpoint-xl` | 1280px | Desktop |
| `breakpoint-2xl` | 1536px | Wide desktop |

### Responsive Rules

- Desktop is optimized for sidebar + table/board + detail panel.
- Tablet collapses the detail panel into a drawer.
- Mobile prioritizes Home, Candidates, Interviews, and Inbox.
- Mobile navigation should become bottom tabs or a compact menu.
- Dense tables become stacked list rows on mobile.
- Candidate detail tabs become segmented controls or a top horizontal tab bar.
- Dashboards on mobile show KPI cards first, then charts, then drill-down lists.
- Voice interview controls must remain reachable with one hand on mobile.
- Avoid hiding critical hiring decision data on small screens.

## Accessibility Rules

- All interactive components require visible focus states.
- Color contrast must meet WCAG AA at minimum.
- AI-generated recommendations must include evidence and confidence text.
- Voice interview states need text equivalents.
- Charts need accessible summaries.
- Tables need keyboard navigation and readable headers.
- Icon-only controls require labels/tooltips.
- Destructive or high-stakes actions need confirmation and clear undo where possible.
- Do not rely on hover for essential actions.

## Recommended Component Inventory

### Core

- App shell.
- Sidebar.
- Top bar.
- Breadcrumbs.
- Tabs.
- Command menu.
- Search input.
- Filter bar.
- Sort menu.
- View switcher.
- Button.
- Icon button.
- Badge.
- Avatar.
- Tooltip.
- Dropdown menu.
- Modal.
- Drawer.
- Toast.

### Workflow

- Candidate table.
- Candidate card.
- Candidate detail panel.
- Job table.
- Job detail panel.
- Interview session view.
- Transcript viewer.
- Evaluation report.
- Rubric editor.
- Match score panel.
- Activity timeline.
- Notes panel.
- Evidence viewer.
- Bulk action bar.

### AI

- AI composer.
- Streaming response.
- Suggested prompt chips.
- AI action button.
- Evidence citation card.
- Confidence indicator.
- Processing phase indicator.
- AI audit event.
- Human override control.

### Dashboard

- KPI card.
- Trend chart.
- Funnel chart.
- Distribution chart.
- Drill-down table.
- Timeframe selector.
- Dashboard filter bar.
- Data freshness indicator.
- Empty analytics state.

## Product-Specific Patterns

### Candidate Object

Candidate surfaces should always expose:

- Name.
- Target role.
- Current stage.
- Match score.
- Evaluation status.
- Owner.
- Last activity.
- Next action.
- Risk or review flag when applicable.

### Job Object

Job surfaces should always expose:

- Role title.
- Department/team.
- Openings.
- Pipeline count.
- Rubric status.
- Top match range.
- Hiring owner.
- Active/inactive state.

### Interview Object

Interview surfaces should always expose:

- Candidate.
- Job.
- Scheduled or completed time.
- Voice/transcript status.
- Evaluation status.
- Duration.
- Review owner.
- Recording/transcript access when permitted.

### Evaluation Object

Evaluation surfaces should always expose:

- Overall score.
- Confidence.
- Criteria scores.
- Evidence completeness.
- AI recommendation.
- Human decision.
- Override history.
- Generated or updated timestamp.

## Final Design System Positioning

LancerAI's design system should be:

- **Dense like Linear** where recruiters need to scan and act.
- **Conversational like ChatGPT** where users need AI help, voice workflows, or generated artifacts.
- **Precise like Vercel** where analytics, logs, evaluation quality, and operational trust matter.

The resulting product language should feel original: graphite surfaces, teal intelligence signals, disciplined grids, compact operational components, readable AI narratives, and evidence-first decision support.
