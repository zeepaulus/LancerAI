# LancerAI Visual Blueprint

## Reference Weighting
- Linear: 35%
- Superlist: 30%
- Raycast: 10%
- Vercel: 10%
- Stripe: 5%
- Framer: 5%
- Notion: 5%

## Core Direction
LancerAI becomes an AI Career Command Center: dense enough for hiring operations, friendly enough for candidates, and premium enough to feel like an AI-native product. The system should not copy any reference directly; it should blend Linear's operational precision with Superlist's warmth, Raycast's command speed, Vercel's metric clarity, Stripe's landing storytelling, Framer's motion polish, and Notion's readable workspace hierarchy.

## Visual Principles
- Operational clarity first: every page should expose the next action.
- Friendly premium: use expressive cards, soft color blocks, and original SVG/product diagrams without becoming cartoonish.
- Command-aware: quick actions, keyboard-like chips, compact menus, and contextual actions.
- Evidence-led AI: interview, CV, matching, and reports should visually connect to transcript/CV/JD evidence.
- Motion with purpose: hover/focus/reveal should clarify state, not distract.

## Theme
- Dark-first graphite, ink, aubergine, electric coral, mint, and warm cream.
- Light mode should be warm paper, not plain white.
- All colors must come from semantic CSS tokens.

## Typography
- Use existing web font stack, but tune toward modern rounded grotesk rhythm.
- Hero: 56-76px desktop, 40-48px tablet, 34-40px mobile.
- Page title: 28-36px.
- Panel title: 15-18px.
- Body: 14-16px.
- Metadata: 11-13px.

## Layout System
- New app shell: expressive left rail, command topbar, workspace canvas.
- Pages use hero strips plus modular sections.
- Dashboards use Bento/card layouts rather than old admin rows.
- Details use split panels: context, primary workspace, evidence/assistant.

## Components
- AppShell, top command bar, nav rail, page hero, bento card, action chip, metric tile, evidence card, voice stage, waveform, timeline, report scorecard, knowledge row, empty canvas, loading shimmer.

## Motion Language
- Durations: 160ms micro, 240ms panel, 420ms hero/entrance.
- Easing: cubic-bezier(.2,.8,.2,1).
- Hover: border glow, subtle translateY(-1px), color lift.
- Loading: shimmer and pulse only where data is pending.
- Reduced motion: disable transforms/continuous animation.

## Page Mapping
- Dashboard: AI Career Command Center, bento overview, urgent queue, command cards.
- Interview: voice-first studio, waveform center, timeline, follow-up queue, transcript evidence.
- Question Bank: searchable knowledge base with command rows and Notion-like topic hierarchy.
- CV Upload/Analysis/Optimization: document-to-evidence workspace.
- Job Matching: candidate/JD comparison with gap cards and match radar.
- Reports: Vercel-like metric clarity with scorecards and evidence sections.
- Landing: Stripe/Framer editorial hero with product mockup scene.
- Auth: premium split screen with product preview.
- Settings/Profile/About: workspace pages with polished sections, not generic forms.

## Asset Strategy
- Use original CSS/SVG visuals built in React.
- No stock photos for product UI.
- Existing member photos may remain for About only.
- Icons should be SVG and consistent; no emoji UI icons.
