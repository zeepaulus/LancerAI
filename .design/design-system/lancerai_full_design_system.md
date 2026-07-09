# LancerAI Full Design System

## Visual Identity

Premium AI SaaS cockpit for IT career preparation. The interface should feel vivid, compact, trustworthy, and fast to understand.

## Themes

- Dark: graphite workspace, raised cards, mint primary, violet AI, blue CV, green matching, amber analytics.
- Light: clean white workspace, soft borders, readable text, same feature accents with lighter muted backgrounds.
- All app surfaces use semantic tokens, not fixed theme colors.

## Core Tokens

- Backgrounds: app, sidebar, topbar, surface, raised surface, muted, inset, card, dropdown, modal, overlay.
- Text: primary, secondary, muted, disabled, on-brand.
- Borders: subtle, strong.
- Accents: brand, AI, voice, CV, matching, analytics, success, warning, danger, info.
- Effects: focus ring, shadow sm/md/lg, glow, hero gradient.

## Type Scale

- Hero: 42/50 desktop, 30/38 mobile.
- Page title: 24/32.
- Panel title: 16/24.
- Body: 14/22.
- Caption: 13/20.
- Status labels: 11px bold.

## Spacing And Radius

- Spacing: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64.
- Radius: 3, 5, 8, 12, pill.
- Cards and panels use 8px radius for SaaS clarity.

## Component Rules

- PageHero: first product signal, clear page purpose, actions, optional visual/progress.
- Panel: section frame with clear header/body separation.
- QuickActionCard: compact action, icon, status, short explanation.
- MetricCard: one metric, one context line, status color only when useful.
- AIStatusPanel: tells user what AI is doing and what to do next.
- InterviewStateCard: voice pipeline states only.
- SearchFilterBar: compact search/filter row.
- TimelineItem: activity, transcript, report, extraction steps.
- ReportPanel: metrics and recommendations grouped for scanability.
- EmptyState/Loading/Error: always include reason and next action when possible.

## Forms

- Inputs use inset background, strong focus ring, readable labels, no hidden placeholder-only forms.
- Destructive actions need clear danger styling and confirmation.
- Buttons wrap on small screens.

## Motion

- Hover lift: 1-2px.
- Sidebar: width/padding/label opacity.
- Modal/dropdown: opacity/transform.
- AI/voice states: pulse and waveform, subtle only.
- Respect `prefers-reduced-motion`.

## Page Patterns

- Dashboard: command center.
- Chat/Interview: voice-first workspace with question, mic controls, transcript, AI feedback.
- Question Bank: searchable knowledge base.
- CV: document intelligence pipeline.
- Job: job intelligence and preparation actions.
- Reports: score/evidence dashboard.
- Settings/Profile: clear workspace preferences and identity.
