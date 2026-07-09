# Asset Sources Used

Date: 2026-07-07

## External Assets Used In This Implementation

No new external asset files were downloaded or embedded in this implementation.

The redesigned UI uses original CSS, inline SVG paths, and existing local project assets. This avoids copyright risk and keeps the app visually consistent.

## Existing Local Assets Observed

| Asset | Source URL | License / Usage Note | Where Used | Reason |
| --- | --- | --- | --- | --- |
| Existing LancerAI logo and social logos in `frontend/src/assets/Logo/` | Existing repository asset | Project-owned or pre-existing; not modified in this pass | Auth/legacy surfaces | Preserve existing brand/social sign-in visuals |
| Existing member images in `frontend/src/assets/Members/` | Existing repository asset | Project-owned or pre-existing; not modified in this pass | About/team pages | Preserve existing team visuals |

## External Sources Researched For Future Use

| Asset Source | URL | License / Usage Note | Intended Use | Reason |
| --- | --- | --- | --- | --- |
| Lucide Icons | https://lucide.dev/license | ISC license; safe for product UI with notice | App icons, nav, controls | Clean 24px outline style |
| Heroicons | https://github.com/tailwindlabs/heroicons/blob/master/LICENSE | MIT license | UI actions, report icons | High-quality minimal SVG icons |
| Tabler Icons | https://github.com/tabler/tabler-icons | MIT license | Dense utility/action icons | Large consistent icon set |
| unDraw | https://undraw.co/license | Free for commercial/noncommercial use; common visual style, use selectively | Optional onboarding/empty illustrations | Useful only if recolored and kept consistent |
# Current Redesign Asset Sources

| Asset | Source URL | License / Usage | Used In | Reason |
|---|---|---|---|---|
| ProductMockupGraphic | Internal CSS/SVG in `frontend/src/components/Common/Visuals.jsx` | Original generated implementation in repo | Landing, Dashboard, Reports, Matching, Auth | Lightweight product preview without copyright risk |
| CVDocumentGraphic | Internal CSS/SVG in `frontend/src/components/Common/Visuals.jsx` | Original generated implementation in repo | CV upload, extraction, optimization | Document intelligence placeholder |
| EvaluationScoreGraphic | Internal CSS/SVG in `frontend/src/components/Common/Visuals.jsx` | Original generated implementation in repo | Interview report, loading/empty report states | AI score/evidence visualization |
| CandidateClusterGraphic | Internal CSS/SVG in `frontend/src/components/Common/Visuals.jsx` | Original generated implementation in repo | Candidate/profile pages | Candidate evidence workspace visual |
| Logo/social icons | Existing project files under `frontend/src/assets/Logo` | Pre-existing project assets | Auth page | Authentication provider affordance |
