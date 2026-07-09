# LancerAI Asset Manifest

Date: 2026-07-09

## Sourced Local Illustrations

All illustration assets below are downloaded SVG files from Storyset, saved locally under `frontend/src/assets/illustrations/`, then optimized with `svgo`. They are not hotlinked.

| Local asset | Feature | Web source | Source SVG URL | License | Reason for choosing | Page used |
|---|---|---|---|---|---|---|
| `ai-career-journey.svg` | Dashboard / career journey | Storyset Hiring, Bro | `https://stories.freepiklabs.com/storage/1720/Hiring-01.svg` | Storyset / Freepik license, attribution required | Existing hiring/career visual; closer to candidate readiness than the previously generated custom journey | Dashboard |
| `product-workspace.svg` | Product overview / AI workspace | Storyset Artificial intelligence, Bro | `https://stories.freepiklabs.com/storage/2588/Artifctial-Intelligence-01.svg` | Storyset / Freepik license, attribution required | Existing AI product visual for landing/auth/about workspace messaging | Landing, Auth, About |
| `cv-analysis-pipeline.svg` | CV extraction / analysis | Storyset Data extraction, Bro | `https://stories.freepiklabs.com/storage/35381/Data-extraction-01.svg` | Storyset / Freepik license, attribution required | Existing data extraction illustration; communicates document-to-structured-data workflow | CV upload, extraction, optimization, review |
| `interview-states.svg` | Voice interview | Storyset Interview, Bro | `https://stories.freepiklabs.com/storage/13273/Interview-01.svg` | Storyset / Freepik license, attribution required | Existing interview illustration; communicates live interview practice | Interview, landing voice showcase |
| `question-library.svg` | Question bank | Storyset Questions, Bro | `https://stories.freepiklabs.com/storage/14181/Questions-01.svg` | Storyset / Freepik license, attribution required | Existing questions illustration; communicates interview question content | Question bank |
| `job-match-pipeline.svg` | Job matching | Storyset Job hunt, Bro | `https://stories.freepiklabs.com/storage/1485/Job-Hunt-01.svg` | Storyset / Freepik license, attribution required | Existing job search illustration; communicates role discovery and matching | Job matching, recommendations |
| `report-analytics.svg` | Reports / analytics | Storyset Data report, Pana | `https://stories.freepiklabs.com/storage/1895/Data-report-01.svg` | Storyset / Freepik license, attribution required | Existing reporting illustration; communicates analytics/reporting | Reports, interview report |
| `candidate-workspace.svg` | Candidate profile/workspace | Storyset Resume, Bro | `https://stories.freepiklabs.com/storage/13477/Resume-bro.svg` | Storyset / Freepik license, attribution required | Existing resume/profile visual for candidate workspace surfaces | Candidate, Profile |
| `empty-interviews.svg` | Empty interview state | Storyset Interview, Rafiki | `https://stories.freepiklabs.com/storage/6326/314-Interview_Artboard-1.svg` | Storyset / Freepik license, attribution required | Existing interview visual for “no sessions yet” state | Interview empty state |

## Vendor Copies Kept For Reference

These were already downloaded under `frontend/src/assets/illustrations/vendor/storyset/` and remain local reference/fallback assets.

| Asset | Source | License |
|---|---|---|
| `vendor/storyset/job-hunt-bro.svg` | Storyset Job hunt | Storyset / Freepik license, attribution required |
| `vendor/storyset/image-upload-bro.svg` | Storyset Image upload | Storyset / Freepik license, attribution required |
| `vendor/storyset/artificial-intelligence-bro.svg` | Storyset Artificial intelligence | Storyset / Freepik license, attribution required |
| `vendor/storyset/data-extraction-bro.svg` | Storyset Data extraction | Storyset / Freepik license, attribution required |
| `vendor/storyset/chat-bot-pana.svg` | Storyset Chat bot | Storyset / Freepik license, attribution required |

## Icon And Motion Notes

The user specifically requested checking/replacing the generated SVG files in `illustrations/`. Icons and Lottie files were not changed in this pass.

## Optimization

All SVG files in `frontend/src/assets/illustrations/` were optimized with `svgo` after download. No external image URLs are rendered by the app.
