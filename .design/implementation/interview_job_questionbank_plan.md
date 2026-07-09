# Interview, Job Matching, and Question Bank Implementation Plan

Date: 2026-07-07

## Files To Inspect

- `app/service/interview/pipeline.py`
- `app/service/interview/agents.py`
- `app/service/interview/state.py`
- `app/service/interview/planning.py`
- `app/router/v1/interview_api.py`
- `app/service/matching/service.py`
- `app/router/v1/job_matching_api.py`
- `frontend/src/App.jsx`
- `frontend/src/components/Layout/Navbar.jsx`
- `frontend/src/pages/InterviewPage.jsx`
- `frontend/src/pages/ChatPage.jsx`
- `frontend/src/pages/InterviewReportPage.jsx`
- `frontend/src/pages/JobMatchingPage.jsx`
- `frontend/src/pages/JobRecommendationsPage.jsx`
- `frontend/src/pages/MainDashboard.jsx`
- `frontend/src/pages/CandidatePage.jsx`
- `frontend/src/pages/LandingPage.jsx`

## Files Likely To Change

- `app/service/interview/agents.py`
- `app/service/interview/pipeline.py`
- `app/service/interview/state.py`
- `frontend/src/App.jsx`
- `frontend/src/components/Layout/Navbar.jsx`
- `frontend/src/pages/InterviewPage.jsx`
- `frontend/src/pages/InterviewReportPage.jsx`
- `frontend/src/pages/JobMatchingPage.jsx`
- `frontend/src/pages/MainDashboard.jsx`
- `frontend/src/pages/CandidatePage.jsx`
- `frontend/src/pages/LandingPage.jsx`
- `frontend/src/pages/CVOptimizationPage.jsx`
- New: `frontend/src/pages/QuestionBankPage.jsx`
- New: `frontend/src/data/questionBank.js`

## Backend Changes

- Improve per-answer evaluation schema so the LLM can return:
  - `ask_follow_up`
  - `follow_up_question`
  - `reason`
  - `evaluation_notes`
  - `next_action`
- Wire the evaluation decision into `InterviewPipeline` before the next AI response.
- Limit follow-up loops with a small per-question depth counter.
- Preserve WebSocket, REST paths, request schemas, and response compatibility.

## Frontend Changes

- Remove visible recruiter/employer/auto-apply framing.
- Rename candidate-management surfaces into candidate-side records, practice, and career workspace language.
- Replace broad industry selection in Interview setup with IT role selection.
- Add a Question Bank page with search, filters, cards, details, practice actions, selected session actions, and empty state.
- Connect Question Bank practice actions to Interview setup through route state.
- Redesign Job Matching as a CV-to-job-fit workflow with collected IT job examples, filters, job detail, match score, missing skills, and actions to prepare interview or generate questions.

## Data Model Or Mock Data Changes

- Use frontend static MVP data for Question Bank and demo job collection.
- Do not add database tables for Question Bank in this pass.
- Keep job matching backend as CV/JD matching and recommendations; frontend collection helps the MVP feel realistic without becoming a full ATS.

## Risk Level

Medium.

- Backend risk: adding live follow-up evaluation calls can increase LLM latency after each user answer.
- Frontend risk: route-state based Question Bank practice still requires an uploaded CV because current interview API requires `cv_id`.
- Scope risk: removing recruiter wording should not remove candidate dashboard/report functionality.

## Step-By-Step Implementation Order

1. Remove visible Emotion Detection references and make session signals clearly integrity/session-quality only.
2. Remove or de-emphasize recruiter, employer, auto-apply, and hiring-team product language.
3. Restrict Interview setup to IT roles and IT levels.
4. Implement structured follow-up decision in the live interview pipeline.
5. Add Question Bank static data and page.
6. Add route and navigation entry for Question Bank.
7. Connect Question Bank actions to Interview setup.
8. Improve Job Matching UI with job collection, detail, matching actions, and question/interview handoffs.
9. Run frontend build and targeted tests where practical.

