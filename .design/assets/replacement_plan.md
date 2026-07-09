# LancerAI Visual Asset Replacement Plan

Date: 2026-07-09

| Old Asset | Why It Was Bad | Replacement | Purpose | Implementation Status |
|---|---|---|---|---|
| Inline dashboard mockup rectangles | Looked like a generic dashboard and did not explain LancerAI | Storyset `Hiring-01.svg` saved as `ai-career-journey.svg`, Storyset `Artifctial-Intelligence-01.svg` saved as `product-workspace.svg` | Use existing web assets for career/AI workspace context | Done |
| Inline CV document lines and chips | Looked like placeholder content | Storyset `Data-extraction-01.svg` saved as `cv-analysis-pipeline.svg` | Use existing web asset for CV/data extraction | Done |
| Inline voice mini mockup | Generic mic/waveform without full state model | Storyset `Interview-01.svg` saved as `interview-states.svg` | Use existing web asset for interview practice | Done |
| Inline match mini cards | Did not clearly show CV-to-JD matching | Storyset `Job-Hunt-01.svg` saved as `job-match-pipeline.svg` | Use existing web asset for job search/matching | Done |
| Inline report bars/ring | Generic analytics card | Storyset `Data-report-01.svg` saved as `report-analytics.svg` | Use existing web asset for reports/analytics | Done |
| Inline question cards | Did not communicate searchable knowledge library | Storyset `Questions-01.svg` saved as `question-library.svg` | Use existing web asset for question bank | Done |
| Candidate cluster placeholder | Generic avatars and score lines | Storyset `Resume-bro.svg` saved as `candidate-workspace.svg` | Use existing web asset for candidate resume/profile context | Done |
| Hand-coded feature icon paths | Inconsistent and not reusable as local assets | `frontend/src/assets/icons/*.svg` | Single line icon language for CV, interview, match, reports, questions, AI | Done |
| Dashboard hero with no visual | Empty first-viewport visual communication | `AssetIllustration name="journey"` | Show candidate -> CV -> AI -> interview -> evaluation -> readiness | Done |
| Interview hero with no visual | Did not preview live interview state model | `AssetIllustration name="voice"` | Show recording, waveform, thinking, transcript | Done |
| Job matching hero with no visual | Did not explain matching workflow | `AssetIllustration name="match"` | Show CV/JD comparison and score | Done |
| Text-only question detail sections | Required reading before recognition | Local icons beside section headings | Improve recognition of purpose, answer, structure, mistakes, sample | Done |
| Page ambient glow | Decorative only | Removed from `Page` | Reduce meaningless visual noise | Done |
| Hero status dots | Decorative only | Removed from `PageHero` | Reduce meaningless visual noise | Done |
| Panel corner mark | Decorative only | Removed from `Panel` | Reduce meaningless visual noise | Done |

## Remaining Placeholders

No placeholder rectangles were intentionally left as visual assets. Some skeleton loaders remain for loading states, where the placeholder pattern communicates pending data rather than decoration.

## Correction Note

The generated SVG illustrations from the first pass were removed by overwriting them with sourced Storyset SVG files. The filenames remain stable so existing React imports continue to work.
