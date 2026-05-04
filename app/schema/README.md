# `app/schema/` — Pydantic Request & Response Schemas

Package định nghĩa toàn bộ **data contracts** cho API surface — request validation (inbound) và response serialization (outbound) — bằng **Pydantic v2**.

Routers import schemas từ đây; service layer không bao giờ trả về raw dict mà phải map sang schema này trước khi respond.

## Files

### `request.py` — Inbound Validation Schemas

| Schema | Endpoint | Fields |
|---|---|---|
| `AuthSignupRequest` | `POST /auth/signup` | `email`, `password` (min 8), `display_name`, `tenant_id?` |
| `AuthLoginRequest` | `POST /auth/login` | `email`, `password` |
| `CVUploadRequest` | `POST /extraction/upload` | `language` (`vi` \| `en`, default `vi`) |
| `OptimizationRequest` | `POST /optimization/analyze` | `cv_id`, `target_job_title?`, `target_industry`, `mode` (`standard` \| `roast`) |
| `JobMatchRequest` | `POST /jobs/match` | `cv_id`, `jd_url?` hoặc `jd_text?` |
| `InterviewSessionRequest` | `POST /interview/sessions` | `cv_id`, `mode` (Literal), `focus_area?`, `duration_minutes` (1–60) |

**Validation highlights:**
- `InterviewSessionRequest.mode` dùng `Literal["practice", "mock", "quick"]` — FastAPI/Pydantic sẽ reject bất kỳ giá trị ngoài enum này với 422.
- `password` có `min_length=8, max_length=128`.
- `duration_minutes` có `ge=1, le=60` (Pydantic constraint, không cần validator riêng).

### `response.py` — Outbound Serialization Schemas

#### Module 1 — CV Extraction

| Schema | Description |
|---|---|
| `PersonalInfo` | name, email, phone, linkedin, location |
| `Education` | school, degree, major, gpa, period |
| `Experience` | company, title, period, descriptions, key_impacts, tech_stack |
| `Project` | name, role, tech_stack, description, key_impacts, potential_roast_points |
| `SkillsMatrix` | languages, frameworks, tools, soft_skills |
| `CVExtractionResponse` | Root response — assembles tất cả sub-schemas trên |

`CVExtractionResponse` là "Deep JSON schema" — LLM được prompt để output JSON conform schema này.

#### Module 3 — Job Matching

| Schema | Description |
|---|---|
| `SkillGap` | skill_name, impact_level (`critical` \| `important` \| `nice_to_have`), reason |
| `JobMatchResponse` | match_score (0–100), highlighted_jd, gap_list |

#### Module 4 — Interview

| Schema | Description |
|---|---|
| `STARScore` | situation, task, action, result (mỗi chiều 0–10) |
| `InterviewReportResponse` | session_id, overall_confidence, total_questions, star_scores, logic_issues, improvement_suggestions |

## Technology

| Component | Library |
|---|---|
| Schema validation | **Pydantic v2** (`BaseModel`, `Field`) |
| Type constraints | `Literal`, `ge`, `le`, `min_length`, `max_length` |
| JSON mode | Pydantic `.model_dump()` / `.model_validate()` |

## Notes

- `email` field hiện là `str` thuần; switch sang `pydantic[email]` (`EmailStr`) khi dependency được thêm vào.
- Tất cả response schemas đều có `default_factory=list` / `default_factory=dict` để tránh shared mutable defaults.
