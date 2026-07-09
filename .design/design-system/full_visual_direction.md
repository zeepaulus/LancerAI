# LancerAI Full Visual Direction

## Identity

LancerAI should feel like a premium AI career cockpit for IT candidates: calm enough for serious job preparation, vivid enough to be memorable, and structured enough that non-technical users always know the next step.

## Mood

- Modern, energetic, professional.
- Dark theme: deep graphite workspace with mint, violet, blue, green, and amber feature accents.
- Light theme: warm white work canvas with clean raised surfaces, visible borders, and restrained vivid accents.
- Avoid single-hue dominance, random decorative assets, childish illustration, and stock-photo collage.

## Palette Strategy

- Brand primary: mint for core AI readiness and action.
- AI accent: violet for analysis, feedback, generation, and assistant panels.
- Voice accent: violet/magenta mix for recording and waveform states.
- CV accent: blue for upload, extraction, document structure.
- Job matching accent: green for fit, match, and skill alignment.
- Analytics accent: amber for reports, insights, and score interpretation.
- Danger/warning/success/info remain semantic and theme-safe.

## Theme Tokens

Use complete semantic tokens:

- `--color-bg-app`, `--color-bg-surface`, `--color-bg-surface-raised`, `--color-bg-muted`, `--color-bg-inset`
- `--color-bg-sidebar`, `--color-bg-topbar`, `--color-bg-card`, `--color-bg-dropdown`, `--color-bg-modal`
- `--color-border-subtle`, `--color-border-strong`
- `--color-text-primary`, `--color-text-secondary`, `--color-text-muted`, `--color-text-disabled`
- `--color-brand-primary`, `--color-brand-primary-hover`, `--color-on-brand`
- `--color-accent-ai`, `--color-accent-voice`, `--color-accent-cv`, `--color-accent-match`, `--color-accent-analytics`
- `--color-overlay`, `--shadow-sm`, `--shadow-md`, `--shadow-lg`, `--shadow-glow`, `--shadow-focus`

## Typography

- Page hero title: 38-54px desktop, 30-36px mobile.
- Page title: 30-42px desktop, 26-32px mobile.
- Panel title: 15-18px.
- Body: 14px, line-height 1.55.
- Captions: 12-13px.
- No negative letter spacing. Uppercase only for small page kickers/status labels.

## Spacing

- Base scale: 4, 8, 12, 16, 20, 24, 32, 40, 48, 64.
- Dashboard/page sections use 16-24px gaps.
- Dense tools use 8-12px internal gaps.
- Avoid cards inside cards except repeated items and framed tools.

## Icon Style

- Use simple 24x24 outline SVGs with round caps, consistent stroke width.
- Use icons as functional signposts, not decoration.
- Inline original SVG icons are preferred unless a library is already installed.
- Lucide/Heroicons/Tabler are approved future sources because they are permissively licensed.

## Illustration / Asset Style

- Prefer original CSS/SVG product mockups and abstract workflow visuals.
- Use lightweight dashboard, document, waveform, score, and match visuals.
- External assets must be open/license-safe and recorded in `.design/assets/asset_sources.md`.

## Components

- Cards: 8px radius, soft border, subtle gradient, hover lift no more than 2px.
- Panels: readable header/body separation, theme-safe raised surface, no visual clutter.
- Buttons: clear primary/outline/ghost/danger states; icon optional; focus ring required.
- Empty states: useful illustration, concise reason, clear next action.
- AI panels: violet/mint accent, explicit state, explanation, and human-review reminder.
- Metric panels: strong number, small trend/detail, status color only where meaningful.

## Page Directions

- Dashboard: AI career command center with hero, readiness score, quick actions, recent evidence, and next best step.
- Question Bank: searchable knowledge base with compact filters, rich detail panel, and direct voice-practice handoff.
- Interview: voice-first workspace with microphone/waveform visual, clear pipeline states, transcript/evaluation language.
- Job Matching: job intelligence dashboard with score clarity, missing skills, and next actions.
- CV: polished document-intelligence flow with clear upload/extraction/optimization states.
- Reports: Vercel/Mercury-inspired metrics and readable evidence panels.
- Settings/Profile: simple workspace preferences with clear categories and safe destructive actions.

## Motion

- Use opacity/transform transitions only.
- Cards hover up 1-2px with border glow.
- Page sections enter subtly via reusable animation.
- Sidebar collapse uses width/padding/icon transitions.
- Recording/analyzing states use pulse/wave animations.
- Respect `prefers-reduced-motion`.

## Responsive Behavior

- Sidebar hidden under 1120px, topbar full-width.
- Grids collapse to one column under 720px.
- Buttons wrap, text truncates only when appropriate, detail panels stay readable.
- Fixed-format UI like cards/boards should have stable dimensions to avoid layout shift.
