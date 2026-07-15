# LancerAI Design Overview

Cập nhật: 2026-07-10.

Tài liệu này tóm tắt định hướng UI/UX hiện tại của LancerAI. Các kế hoạch, audit và chi tiết triển khai sâu hơn nằm trong thư mục `.design/`.

## Product Personality

LancerAI là công cụ hỗ trợ ứng viên, nên giao diện cần tạo cảm giác:

- Rõ ràng và đáng tin cậy.
- Tập trung vào hành động tiếp theo của ứng viên.
- Đủ hiện đại để phù hợp sản phẩm AI, nhưng không quá trang trí.
- Hữu ích trong các workflow lặp lại: upload CV, review dữ liệu, tối ưu, match JD, luyện phỏng vấn, đọc báo cáo.

## Core User Journey

```text
Landing/Auth
  -> Dashboard
  -> Upload CV
  -> Review extracted CV
  -> Optimize CV
  -> Match jobs / choose JD
  -> Practice interview
  -> Review reports
```

## Current Frontend Surfaces

Routes are defined in `frontend/src/App.jsx`.

| Surface | Route |
|---|---|
| Landing | `/` |
| Auth | `/login`, `/signup` |
| About | `/about` |
| Dashboard | `/dashboard` |
| Candidate profile area | `/candidate`, `/profile`, `/settings` |
| CV upload/review | `/cv-upload`, `/cv-extraction-result`, `/cv-review` |
| CV optimization | `/cv-optimization` |
| Job matching | `/job-matching`, `/job-recommendations` |
| Interview | `/interview`, `/chat`, `/interview-report` |
| Reports/question bank | `/reports`, `/question-bank` |

## UI Principles

### 1. Workflow-first

Every major page should answer:

- What input does the user need to provide?
- What is currently happening?
- What result did the system produce?
- What should the user do next?

Avoid marketing-only sections inside authenticated product surfaces.

### 2. Trustworthy AI Output

AI-generated results should be easy to inspect and correct:

- Show extracted CV data in editable/reviewable form before downstream use.
- Separate high-confidence facts from suggestions.
- Mark fallback/degraded results when a model, vector DB or TTS/STT service is unavailable.
- Keep raw technical errors out of the UI.

### 3. Dense But Calm Dashboards

Dashboard/report pages should prioritize scanning:

- Compact summary metrics.
- Clear status labels.
- Tables/lists for history.
- Direct actions near each item.

### 4. Interview State Clarity

Voice interview UI should clearly show state:

- Waiting for microphone.
- Listening.
- Transcribing.
- Thinking.
- Speaking.
- No speech detected.
- Session completed or interrupted.

The backend can support this better once explicit events such as `stt_started`, `llm_thinking`, `tts_started` and `no_speech_detected` are added.

## Visual Assets

Project assets live mainly in:

- `frontend/src/assets/Logo/`
- `frontend/src/assets/icons/`
- `frontend/src/assets/illustrations/`
- `frontend/src/assets/lottie/`
- `.design/assets/`

Current visual direction uses product-specific illustrations and icons for:

- CV analysis.
- Job matching.
- Interview states.
- Reports.
- Empty states.
- AI/career journey.

## Frontend Implementation Notes

| Area | Location |
|---|---|
| Routes | `frontend/src/App.jsx` |
| API wrappers | `frontend/src/api/*.js` |
| Shared UI | `frontend/src/components/Common/` |
| Layout | `frontend/src/components/Layout/` |
| Global styles | `frontend/src/index.css` |
| Theme context | `frontend/src/store/ThemeContext.jsx` |

Frontend should keep API paths centralized in `frontend/src/api/paths.js` and avoid duplicating endpoint strings in pages.

## Design Documentation Map

| Area | Path |
|---|---|
| Design system notes | `.design/design-system/` |
| Implementation plans | `.design/implementation/` |
| QA and release readiness | `.design/qa/` |
| Visual/UI reviews | `.design/reviews/` |
| Asset tracking | `.design/assets/` |
| Reference analysis | `.design/reference-analysis/` |

## Known UX Gaps

- Multipart CV upload should have timeout/retry UX.
- CV extraction should make partial/low-confidence results explicit.
- Interview should expose finer-grained state events from backend.
- Reports should show whether output is LLM-generated, fallback-generated or cache-served.
- Job recommendations need an empty-state explanation when the job corpus/vector store is empty.

## Related Docs

- [README.md](README.md)
- [docs/SYSTEM_OVERVIEW.md](docs/SYSTEM_OVERVIEW.md)
- [docs/FLOW_STUDY_CASES.md](docs/FLOW_STUDY_CASES.md)
- [docs/PROJECT_REPORT.md](docs/PROJECT_REPORT.md)
- [TODO.md](TODO.md)
