# LancerAI TopCV, Job Matching, Question Bank Context Audit

## Scope
Inspected frontend/backend files requested in the latest prompt:

- Backend: `app/router/v1/job_matching_api.py`, `app/service/matching/service.py`, `app/models/job_listing.py`, `app/models/job_match_result.py`, `app/workers/crawler_worker.py`, `app/workers/celery_app.py`, `app/schema/request.py`, `app/schema/response.py`, provider modules, Alembic versions.
- Frontend: `JobMatchingPage.jsx`, `JobRecommendationsPage.jsx`, `matching.js`, `paths.js`, `QuestionBankPage.jsx`, `questionBank.js`, `Navbar.jsx`, `ReportsPage.jsx`, `InterviewReportPage.jsx`, `index.css`.

## 1. Current Job Matching Flow

- Frontend `JobMatchingPage.jsx` uses a local hard-coded `JOB_COLLECTION` array with five demo IT roles.
- The page supports three JD modes: selected local job, pasted JD text, or JD URL.
- Matching calls `matchCV(payload)` in `frontend/src/api/matching.js`, which posts to `POST /api/v1/jobs/matches`.
- The backend route validates the CV belongs to the current user, then calls `MatchingService.match_cv_to_jd(cv_data, jd_text, jd_url)`.
- The service computes frequency, position, semantic scores, requests LLM feedback, saves a `JobMatchResult`, and returns `JobMatchResponse`.

## 2. Mock Job Collection Status

- Yes, frontend still uses mock `JOB_COLLECTION` directly inside `frontend/src/pages/JobMatchingPage.jsx`.
- The mock collection is not sourced from `job_listings`, so crawled jobs are not visible in Job Matching yet.
- `JobRecommendationsPage.jsx` does use backend recommendations, but only through vector search results.

## 3. JD Text and JD URL Backend Support

- `JobMatchRequest` accepts `cv_id`, optional `jd_url`, optional `jd_text`.
- The validator requires either `jd_url` or `jd_text`.
- `MatchingService.match_cv_to_jd()` fetches from `jd_url` only when `jd_text` is empty.
- `_fetch_jd_from_url()` has SSRF protection, tries Jina Reader first, then a direct request with BeautifulSoup.
- Existing `POST /jobs/matches` contract should remain intact. Safer frontend integration is to send selected crawled job description as `jd_text`.

## 4. JobListing Model

`JobListing` stores:

- `id`, `source`, `source_url`, `title`, `company`, `location`
- `description`, `requirements` JSON, `salary_range`
- `experience_level`, `job_type`, `is_active`
- `created_by`, `crawled_at`, `updated_at`

Alembic already created the base table and later added `experience_level`, `job_type`, `updated_at`.

## 5. Existing Crawler

- `app/workers/crawler_worker.py` already has `crawl_job_listings(source="topcv", max_pages=5)`.
- It supports `topcv` and `itviec`.
- It saves jobs to `job_listings`, deduplicates by `source_url`, and stores embeddings through the vector repository.
- It falls back to `MOCK_JOBS` when no live jobs are crawled.

## 6. Crawler Weaknesses

- TopCV URL is old: `https://www.topcv.vn/tim-viec-lam?keyword=IT&page={page}`.
- It does not validate the approved TopCV URL query structure.
- It scrapes only shallow card data and often constructs placeholder descriptions.
- It does not fetch detail pages for robust JD, requirements, or benefits.
- It does not infer skills, tags, experience level, or job type from detail text.
- It increments `jobs_skipped` for existing rows but does not update stale existing jobs.
- It lacks explicit polite delay/rate limiting between detail page requests.
- Celery app still has a TODO and no 12-hour beat schedule.

## 7. Recommendations and Vector Search

- `MatchingService.get_recommendations()` embeds flattened CV text, queries vector repository, and maps metadata into `JobRecommendationResponse`.
- Crawler stores embeddings with job id and metadata including title/company/location/url.
- Recommendation quality depends on crawler storing useful JD text and embeddings.

## 8. Current Question Bank Data

- `frontend/src/data/questionBank.js` contains about 18 English question objects.
- Fields are `question`, `category`, `role`, `level`, `difficulty`, `tags`, `answerStructure`, `commonMistakes`, `expectations`, `sampleAnswer`.
- It exports `IT_ROLES`, `IT_LEVELS`, `QUESTION_CATEGORIES`, `DIFFICULTIES`, and `allQuestionTags()`.

## 9. Frontend UI Sections to Remove or Simplify

- `Navbar.jsx`: remove topbar brand button and search/action row containing “Find focused IT questions and start voice practice”; remove visible theme toggle and dropdown theme option.
- `QuestionBankPage.jsx`: remove interview practice behavior (`selectedIds`, add/remove session, practice selected, practice this question, navigation to `/interview`).
- `QuestionBankPage.jsx`: replace vertical filters panel with compact horizontal filter bar.
- `QuestionBankPage.jsx`: remove always-visible detail panel; open Vietnamese detail only on question click.
- `InterviewReportPage.jsx`: remove visible `Competency scorecard`, `Interview plan`, and `Competency score` metric.
- `ReportsPage.jsx`: remove confusing template metric/model panel wording that implies unavailable report templates/scorecards.
- `JobMatchingPage.jsx`: replace local mock-first collection with backend loaded job listings and fallback only when backend is unavailable/empty.
- `Visuals.jsx`: make question-bank visuals knowledge/question oriented and keep other variants tied to product meaning.

## 10. Files Needing Changes

- Frontend:
  - `frontend/src/components/Layout/Navbar.jsx`
  - `frontend/src/store/ThemeContext.jsx`
  - `frontend/src/pages/QuestionBankPage.jsx`
  - `frontend/src/data/questionBank.js`
  - `frontend/src/pages/JobMatchingPage.jsx`
  - `frontend/src/pages/ReportsPage.jsx`
  - `frontend/src/pages/InterviewReportPage.jsx`
  - `frontend/src/components/Common/Visuals.jsx`
  - `frontend/src/api/matching.js`
  - `frontend/src/api/paths.js`
  - `frontend/src/index.css`
- Backend:
  - `app/router/v1/job_matching_api.py`
  - `app/schema/response.py`
  - `app/workers/crawler_worker.py`
  - `app/workers/celery_app.py`
- Documentation:
  - `.design/implementation/topcv_crawler_questionbank_summary.md`
