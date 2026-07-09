# LancerAI Frontend Visual Gap Audit

## Skill Usage
- `ui-ux-pro-max`: available at `C:\Users\ZeePaul\.agents\skills\ui-ux-pro-max\SKILL.md`; used for design-system search, UX validation, React stack checks.
- `ui-styling`: available at `C:\Users\ZeePaul\.agents\skills\ui-styling\SKILL.md`; used for accessibility, focus, semantic HTML, and reduced-motion guidance. Tailwind/shadcn setup was not applied because the project constraints require keeping the current Vite/React/CSS stack.

## Global Gaps
- Current UI already has a modern shell, but still reads closer to a clean admin dashboard than a vivid AI SaaS. The old mint-heavy palette makes pages feel similar and reduces feature personality.
- Light theme is functional but not premium enough; surfaces are flat white with limited aurora depth.
- Some visual components rely on inline object styles. They are safe for SVG/mockup primitives, but global tokens need to carry more of the visual identity.
- Motion exists in hover and loading states, but page sections, cards, dropdowns, sidebar, and AI states need stronger, consistent transition rhythm.

## Page Gaps
- Dashboard: structure is good, but hero/cards need more Superlist-like energy and stronger next-action hierarchy.
- Voice Interview: voice-first behavior is present; visual state needs more recording/analyzing energy and clearer premium stage framing.
- ChatPage: live interview layout is strong; needs aurora state glow and better AI transcript focus.
- Question Bank: detail panel exists; needs knowledge-base polish, active question contrast, and tighter Raycast-like search/filter feel.
- Job Matching: functionally clear; cards and match panels need more dashboard-grade visual density and role-fit accenting.
- CV Upload/Extraction/Optimization/Review: flows are clear; document intelligence visuals need more premium color depth and stronger before/after grouping.
- Reports/Interview Report: readable; metric and evidence panels need Vercel-like scan quality and stronger chart/card hierarchy.
- Landing/Auth: significantly improved from legacy, but should better express Stripe/Framer aurora and product preview energy.
- Profile/Settings/About: consistent but still subdued; needs clearer Notion-like grouping and theme-aware controls.

## Risk Notes
- Do not add Tailwind, shadcn, or new UI architecture.
- Keep API calls, route names, and backend contracts unchanged.
- Preserve accessibility: focus rings, labels, aria-live, semantic buttons.
