# LancerAI Visual Asset Audit

Date: 2026-07-09

## Audit Summary

The previous system relied on inline React drawings in `frontend/src/components/Common/Visuals.jsx`: generic dashboard boxes, anonymous chart bars, fake document lines, glow blobs, and decorative shell elements. In the first rebuild pass, several replacement SVGs in `frontend/src/assets/illustrations/` were also generated locally. Per the follow-up instruction, those generated illustration SVGs have now been replaced with existing downloadable Storyset SVG files saved locally.

Meaningless visuals removed:

- Inline product mockup rectangles from `Visuals.jsx`.
- Inline CV line/chip placeholder graphic from `Visuals.jsx`.
- Inline candidate cluster placeholder panel from `Visuals.jsx`.
- Inline evaluation bars/score placeholder from `Visuals.jsx`.
- Decorative page ambient element from `AppUI.jsx`.
- Decorative hero status-dot element from `AppUI.jsx`.
- Decorative panel corner element from `AppUI.jsx`.

## Visuals Reviewed

| Visual | Where Used | Information Communicated | Meaningful? | Decision |
|---|---|---:|---:|---|
| `ProductMockupGraphic` inline dashboard | Landing, Auth, About, Profile | Generic app chrome and chart boxes | No | Replaced with local semantic SVGs by variant |
| `ProductMockupGraphic` inline voice | Landing showcase | Generic audio/chat area | Partial | Replaced with `interview-states.svg` |
| `ProductMockupGraphic` inline CV | CV review/optimization, landing | Generic document extraction | Partial | Replaced with `cv-analysis-pipeline.svg` |
| `ProductMockupGraphic` inline match | Job recommendations | Candidate/job cards with score | Partial | Replaced with `job-match-pipeline.svg` |
| `ProductMockupGraphic` inline report | Reports | Ring and bars | Partial | Replaced with `report-analytics.svg` |
| `ProductMockupGraphic` inline questions | Question bank | Question cards | Partial | Replaced with `question-library.svg` |
| `CVDocumentGraphic` inline | CV upload, extraction, empty states | Resume to extracted fields | Partial | Replaced with `cv-analysis-pipeline.svg` |
| `CandidateClusterGraphic` inline | Candidate page | Candidate group and score lines | Partial | Replaced with `candidate-workspace.svg` |
| `EvaluationScoreGraphic` inline | Interview report | AI score and bars | Partial | Replaced with `report-analytics.svg` plus live score overlay |
| `FeatureIcon` inline paths | Dashboard, landing, question modal | Mixed hand-drawn icon semantics | Partial | Replaced with local single-language SVG icons |
| `Page` ambient visual | All app pages | Decorative glow only | No | Removed |
| `PageHero` system dots | All page heroes | Decorative status chrome | No | Removed |
| `Panel` corner mark | Panels | Decorative line only | No | Removed |
| Dashboard hero with no visual | Dashboard | Nothing about product workflow | No | Added `ai-career-journey.svg` |
| Interview hero with no visual | Interview page | Nothing about live interview states | No | Added `interview-states.svg` |
| Job matching hero with no visual | Job matching page | Nothing about CV-to-JD matching | No | Added `job-match-pipeline.svg` |
| Question detail blocks with text-only sections | Question detail modal | Requires reading every heading | Partial | Added semantic local icons |

## Validation Question

Can a first-time user understand each feature from the visual alone?

- Dashboard: yes, the journey shows candidate, CV upload, AI analysis, interview, evaluation, and readiness.
- CV upload/extraction/optimization: yes, the pipeline shows resume, OCR, AI extraction, skills, and optimized CV.
- Interview: yes, the visual shows microphone, waveform, AI thinking, and transcript evidence.
- Question bank: yes, the visual reads as a searchable interview knowledge library.
- Job matching: yes, the visual shows candidate and JD compared through a scoring/matching engine.
- Reports: yes, the visual shows score, trend bars, and report evidence.

## 2026-07-09 Correction

The following generated illustration files were replaced with sourced Storyset SVG files:

- `ai-career-journey.svg` -> Storyset Hiring, Bro.
- `product-workspace.svg` -> Storyset Artificial intelligence, Bro.
- `cv-analysis-pipeline.svg` -> Storyset Data extraction, Bro.
- `interview-states.svg` -> Storyset Interview, Bro.
- `question-library.svg` -> Storyset Questions, Bro.
- `job-match-pipeline.svg` -> Storyset Job hunt, Bro.
- `report-analytics.svg` -> Storyset Data report, Pana.
- `candidate-workspace.svg` -> Storyset Resume, Bro.
- `empty-interviews.svg` -> Storyset Interview, Rafiki.
