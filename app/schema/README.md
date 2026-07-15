# `app/schema/` - Pydantic Contracts

`app/schema/` defines API request validation and response serialization using Pydantic v2.

Routers should import schemas from here and avoid returning arbitrary dicts where a stable contract exists.

## Files

| File | Purpose |
|---|---|
| `request.py` | Inbound request bodies |
| `response.py` | Outbound response models |

## Request Schemas

| Schema | Endpoint | Key fields |
|---|---|---|
| `AuthSignupRequest` | `POST /auth/signup` | `email`, `password`, `display_name`, optional ignored `tenant_id` |
| `AuthLoginRequest` | `POST /auth/login` | `identifier`, `password` |
| `PasswordChangeRequest` | `PUT /auth/password` | `current_password`, `new_password` |
| `CVExtractionUpdateRequest` | `PUT /extraction/cvs/{cv_id}` | Editable structured CV fields |
| `OptimizationRequest` | `POST /optimization/cvs/{cv_id}/optimizations` | `target_job_title`, `target_industry`, `mode` |
| `RenderTemplateRequest` | `POST /optimization/cvs/{cv_id}/render` | `template` |
| `JobMatchRequest` | `POST /jobs/matches` | `cv_id`, `jd_text` or `jd_url` |
| `InterviewSessionRequest` | `POST /interview/sessions` | `cv_id`, optional JD context, `mode`, `focus_area`, `duration_minutes` |

Validation highlights:

- Passwords require 8-128 chars.
- `InterviewSessionRequest.mode` is `Literal["practice", "mock", "quick"]`.
- `duration_minutes` is constrained to 1-60.
- `JobMatchRequest` requires at least one JD source.
- `email` is currently plain `str`; switching to `EmailStr` requires adding `pydantic[email]`.

## Response Schemas

| Schema | Purpose |
|---|---|
| `AuthTokenResponse` | Bearer token response |
| `UserProfileResponse` | Basic user profile |
| `CVExtractionResponse` | Full structured extracted CV |
| `CVRecordSummaryResponse` | Compact CV history row |
| `CVOptimizationResponse` | Optimization output, issues, rewrites, scorecard |
| `RenderedCVResponse` | Template render output |
| `JobListingResponse` | Public job listing row/detail |
| `JobMatchResponse` | Match scores, feedback and missing skills |
| `JobRecommendationResponse` | Vector recommendation row |
| `InterviewSessionResponse` | Session creation metadata |
| `InterviewReportResponse` | STAR report, behavior, transcript, scorecard |

## CV Extraction Shape

`CVExtractionResponse` contains:

- `personal_info`
- `education`
- `experience`
- `projects`
- `skills_matrix`
- `certifications`
- `languages`

This schema is also used as the LLM extraction target.

## Notes

- Use `default_factory` for list/dict fields to avoid shared mutable defaults.
- Keep request schemas minimal; path params like `cv_id` should stay in the URL.
- Update this README when adding public fields because frontend API wrappers depend on these shapes.
