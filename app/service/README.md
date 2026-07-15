# `app/service/` - Business Logic

`app/service/` chứa logic nghiệp vụ của LancerAI. Service nhận dependencies qua constructor, không dùng FastAPI `Depends` bên trong method. Router gọi service, service gọi repository/connector.

## Structure

```text
service/
|-- auth/
|   `-- service.py
|-- cv_analysis/
|   `-- scorecard.py
|-- extraction/
|   `-- service.py
|-- matching/
|   `-- service.py
|-- optimization/
|   |-- service.py
|   |-- graph.py
|   |-- state.py
|   |-- retrieval_agent.py
|   |-- roast_agent.py
|   |-- rewrite_agent.py
|   |-- audit_agent.py
|   `-- template_renderer.py
|-- interview/
|   |-- service.py
|   |-- pipeline.py
|   |-- agents.py
|   |-- behavior.py
|   |-- pacing.py
|   |-- planning.py
|   |-- scoring.py
|   |-- state.py
|   `-- state_machine.py
`-- README.md
```

## Module Summary

| Module | Main service | Responsibilities |
|---|---|---|
| Auth | `AuthService` | Signup, login, resolve token, change password |
| CV analysis | `scorecard.py` | Deterministic CV scoring and skill-gap helpers |
| Extraction | `ExtractionService` | PDF/image text extraction, LLM structuring, persistence, vector embedding |
| Optimization | `OptimizationService` | LangGraph pipeline and CV score persistence |
| Matching | `MatchingService` | CV-JD hybrid scoring, LLM feedback, recommendations, match persistence |
| Interview | `InterviewService`, `InterviewPipeline` | REST session/report lifecycle and WebSocket voice pipeline |

## Auth

| Method | Description |
|---|---|
| `signup` | Normalize account data, hash password, create `User` |
| `login` | Verify identifier/password and create JWT |
| `resolve_token` | Decode JWT and fetch active user |
| `update_profile` | Update visible user profile |
| `change_password` | Verify old password and save new hash |

## Extraction

Pipeline:

```text
file bytes
  -> PDF text layer or OCR
  -> LLM JSON extraction
  -> CVRecord
  -> vector embedding best-effort
```

Key methods:

| Method | Description |
|---|---|
| `extract_from_pdf` | Validate size, extract PDF text with PyMuPDF, OCR low-density pages |
| `extract_from_image` | OCR image bytes |
| `get_cv` | User-scoped CV lookup |
| `list_user_cvs` | Recent CV history |
| `update_extracted_data` | Save reviewed structured data and reset optimization status |

## Optimization

See [optimization/README.md](optimization/README.md).

Pipeline:

```text
retrieval -> roast -> rewrite -> audit -> deterministic scorecard -> persist
```

`OptimizationService.analyze_cv` runs the compiled LangGraph workflow, saves `optimized_data`, `audit_score`, `optimization_mode` and `status`.

## Matching

Pipeline:

```text
JD text/url
  -> safe fetch if URL
  -> token scoring
  -> section-position scoring
  -> semantic embedding scoring
  -> LLM feedback or deterministic fallback
  -> optional Neo4j related-skill adjustment
```

Key methods:

| Method | Description |
|---|---|
| `match_cv_to_jd` | Return `JobMatchResponse` |
| `get_recommendations` | Query vector store for similar job listings |
| `save_match_result` | Persist component scores and missing skills |
| `save_job`, `update_match_status` | User workflow helpers for saved/applied/rejected states |

## Interview

See [interview/README.md](interview/README.md).

`InterviewService` handles REST-side session lifecycle and reports. `InterviewPipeline` handles WebSocket audio/conversation lifecycle.

## Worker-Adjacent Logic

Workers in `app/workers/` reuse services where possible:

- TopCV crawler stores `JobListing` rows and embeddings.
- Document worker uses `CVTemplateRenderer` and `python-docx`.

## Testing Focus

Service-level tests should cover:

- Ownership checks via user-scoped records.
- Fallback behavior when LLM/vector/graph services fail.
- Prompt guardrails for rewrite/audit.
- Matching score renormalization when semantic score is missing.
- Interview scoring/behavior/pacing edge cases.
