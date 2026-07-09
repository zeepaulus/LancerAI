# LancerAI Asset Sourcing Plan

## Safe Source Research

- Lucide Icons: https://lucide.dev/license - ISC license; safe for commercial/personal use with copyright notice.
- Heroicons: https://github.com/tailwindlabs/heroicons/blob/master/LICENSE - MIT license.
- Tabler Icons: https://github.com/tabler/tabler-icons - MIT license, 24x24 stroke icon style.
- unDraw: https://undraw.co/license - free use for commercial/noncommercial projects, but use selectively because the style is common.

## Asset Strategy

Current implementation should prefer original CSS/SVG visuals to keep the app cohesive and avoid asset-license uncertainty. External assets are planned as optional replacements only when they improve clarity.

| Feature Area | Asset Needed | Type | Suggested Source | License / Safety | Intended Use | Fallback |
| --- | --- | --- | --- | --- | --- | --- |
| Landing hero | AI career command center mockup | SVG/CSS or WebP | Original CSS/SVG first; optional unDraw | Original is safest; unDraw license allows use | First viewport product signal | `ProductMockupGraphic dashboard` |
| Dashboard | Readiness score, workflow cards | CSS/SVG/icon | Original + Lucide-style inline icons | Original paths, no dependency | Metric/quick action cards | `FeatureIcon`, `IconBadge` |
| CV upload/analysis | Document extraction visual | SVG/CSS | Original; optional Heroicons document icon | MIT if used | Upload dropzone and CV empty states | `CVDocumentGraphic` |
| CV optimization | Before/after rewrite visual | SVG/CSS | Original | Original safe | Rewrite comparison panels | existing panels/cards |
| Question Bank | Search/knowledge-base icons | SVG/icon | Tabler/Heroicons if downloaded later | MIT | Filters, tags, detail sections | inline original icons |
| Voice Interview | Microphone/waveform visual | CSS/SVG | Original; optional Lucide mic icon | ISC if used | Recording/listening/analyzing states | `ProductMockupGraphic voice` + CSS waves |
| Job Matching | Match score, job-card icons | CSS/SVG | Original; optional Tabler briefcase icons | MIT | Job card, score panel, missing skills | `ProductMockupGraphic match` |
| Reports | Analytics/score visuals | CSS/SVG | Original; optional Heroicons chart icons | MIT | Report panels and metrics | `EvaluationScoreGraphic` |
| Settings/Profile | Avatar and preference icons | CSS/SVG | Original | Original safe | Profile summary, categories | `CandidateAvatar` |
| Empty states | Consistent product miniatures | CSS/SVG | Original; optional unDraw only if style aligned | Original safe | No data, error, loading states | `EmptyState` with product visuals |
| Loading states | Skeleton, wave, analyzing pulse | CSS | Original | Original safe | AI processing/recording/loading | `.skeleton`, `.wave-bar`, pulse |

## Download Decision

No external bitmap/vector files are downloaded in this pass. The app will use original inline SVG/CSS visuals already in `Visuals.jsx` and newly improved component styling. This keeps file size low and avoids attribution ambiguity.

## Later Asset Candidates

- Add a local `src/assets/icons/` folder only if the team decides to vendor MIT/ISC icon SVGs.
- Add a local `src/assets/illustrations/` folder only for final brand-approved SVGs.
- Avoid GIFs and heavy Lottie unless the interview waveform truly needs richer motion.
