# LancerAI Frontend UI Rules

Date: July 7, 2026  
Stack: React 18, Vite, React Router DOM, JavaScript ES Modules, existing CSS.

## UI UX Pro Max Status

Status: **Partially installed / locally available**

Evidence checked:

- Local artifact exists: `.agent/skills/ui-ux-pro-max/SKILL.md`
- Local datasets exist: `colors.csv`, `typography.csv`, `ux-guidelines.csv`, `charts.csv`, `styles.csv`, `web-interface.csv`, and React stack data.
- The skill is not listed as a registered runtime skill for this session, so the implementation uses its local guidance manually.
- Local UI UX Pro Max searches were run for AI SaaS dashboard direction, React guidance, UX loading/error/empty states, and chart/status guidance.

## Product Design Direction

- 50% Linear: persistent sidebar, compact panels, operational density, workflow-first tables.
- 30% ChatGPT: calm AI conversation surfaces, clear assistant states, approachable empty states.
- 20% Vercel: metrics, reports, status indicators, analytics clarity, technical trust.

## Typography Scale

- Page title: `24px / 32px`, `650`
- Section title: `20px / 28px`, `650`
- Panel title: `16px / 24px`, `620`
- Body: `14px / 22px`, `400`
- Caption/meta: `11-13px`, `600-700`
- Monospace: IDs, timestamps, transcript/system tokens only

Rules:

- No oversized app-page hero type.
- Use hierarchy, grouping, and metadata before increasing font size.
- Letter spacing stays `0`, except uppercase metadata at `0.02em`.

## Spacing Scale

- 4px: icon/text micro gaps
- 8px: compact controls
- 12px: row gaps and form field gaps
- 16px: default group gap
- 20px: panel padding
- 24px: page group spacing
- 32px: dashboard section spacing
- 48px+: public pages only

## Color Usage

- Neutral graphite surfaces carry most UI.
- Teal is the primary intelligence/action color.
- Purple is AI/voice/processing.
- Green, amber, and red are reserved for semantic status.
- Color must never be the only indicator; include labels or text.
- Light mode must keep body text at WCAG AA contrast.

## Border Radius / Elevation

- Inputs/buttons: `5px`
- Cards/panels: `8px`
- Modals/live room surfaces: `12px`
- Pills: status badges and metadata only
- Default elevation is border-first; shadows only for modals/dropdowns.

## Cards / Panels

- Cards represent objects: candidate, interview, report, metric, insight, or action.
- Do not create decorative nested cards.
- Use `Panel` for titled sections and `card` for repeated objects.
- Hover can change border/background but must not shift layout.

## Buttons

- Primary: one main action per surface.
- Outline: secondary navigation/action.
- Tertiary/ghost: low-emphasis inline utility.
- Danger: destructive or session-ending actions only.
- Disabled states must be visibly disabled and explainable through surrounding context.

## Inputs / Forms

- Use explicit labels with `htmlFor` and stable IDs.
- Placeholder text is helper copy, not the only label.
- Show field-level errors where possible.
- Blocking errors must use `role="alert"`.
- Long AI setup forms should be grouped by intent: role/JD/CV/mode.

## Tables / Lists

- Use tables for comparison and triage.
- Rows should be clickable only when they visibly behave as work objects.
- Include status, score, date/activity, and next action where possible.
- Mobile tables can collapse into stacked rows via existing CSS.

## Status Badges

- `success`: generated, complete, shortlist-ready
- `warning`: incomplete, medium confidence, needs review
- `danger`: failed, low confidence, critical gap
- `ai`: generating, analyzing, listening, processing
- `neutral`: metadata and non-actionable state

## Empty States

- Include a product-specific visual, one clear explanation, and one next action.
- Do not leave dashboard panels blank.
- Avoid tutorial copy; speak in operational next steps.

## Loading States

- Preserve page structure with skeletons where possible.
- Use inline progress for AI analysis and upload flows.
- Voice interview must show current phase continuously.

## Error States

- Use human-readable language and recovery action.
- Put errors near the failed action.
- Use `role="alert"` for blocking errors.
- Avoid silent failures and generic “something went wrong” where a next step is known.

## AI Response Panels

- Frame AI output as guidance with evidence.
- Include confidence/score when available.
- Separate AI recommendation from human decision/action.
- Long generated text should preserve whitespace and line breaks.

## Voice Interview UI

- The live room should prioritize state, audio/camera status, transcript, and end/report actions.
- Show listening, processing, speaking, ended, and error states with labels and semantic color.
- Avoid clutter inside video panes.
- Transcript must be easy to scan and distinguish system, candidate, and AI turns.

## Report / Analytics UI

- Start with score and status summary.
- Use metrics for scanability.
- Group sections in this order: summary, scorecard, behavior, STAR, transcript, suggestions.
- Use charts/bars sparingly and label every metric.

## Responsive Behavior

- Desktop is primary for recruiter operations.
- Below 1120px, sidebar collapses and content becomes single-column.
- Below 720px, tables stack and page headers/actions wrap.
- Avoid fixed-width inline layouts that cause horizontal scroll.

## Accessibility Rules

- Use semantic buttons for actions.
- Provide visible focus states.
- Avoid emoji as UI icons; use SVG/CSS/text labels.
- `aria-live` for dynamic live-room state and alert regions for blocking errors.
- Respect `prefers-reduced-motion`.
