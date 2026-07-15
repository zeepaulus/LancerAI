# `app/service/optimization/` - CV Intelligence Pipeline

This bounded context owns CV optimization: retrieve context, detect weak areas, rewrite high-impact sections, audit truthfulness and persist an optimized CV.

## Structure

```text
optimization/
|-- service.py
|-- graph.py
|-- state.py
|-- retrieval_agent.py
|-- roast_agent.py
|-- rewrite_agent.py
|-- audit_agent.py
|-- template_renderer.py
`-- README.md
```

## Runtime Pipeline

```text
START
  -> retrieval_agent
  -> roast_agent
  -> rewrite_agent
  -> audit_agent
  -> END
```

`OptimizationService.analyze_cv`:

1. Loads the user-owned `CVRecord`.
2. Builds initial `CVOptimizationState`.
3. Invokes the compiled LangGraph workflow.
4. Builds a deterministic scorecard with `build_cv_scorecard`.
5. Persists `optimized_data`, `audit_score`, `optimization_mode` and `status="optimized"`.
6. Returns `CVOptimizationResponse`.

## Main Files

| File | Role |
|---|---|
| `service.py` | Public orchestrator called by router |
| `graph.py` | Builds and compiles the LangGraph state graph |
| `state.py` | TypedDict state and Pydantic sub-schemas |
| `retrieval_agent.py` | Retrieves role/industry context and keyword map |
| `roast_agent.py` | Finds evidence-backed CV issues |
| `rewrite_agent.py` | Rewrites high/critical issues with guardrails |
| `audit_agent.py` | Rejects unsupported rewrites and assembles final CV |
| `template_renderer.py` | Renders CV templates and PDF bytes |

## State Highlights

| Field | Meaning |
|---|---|
| `cv_id` | CV being optimized |
| `raw_cv_data` | Structured CV input |
| `target_job_title` | Role context |
| `target_industry` | Industry context |
| `industry_benchmarks` | Retrieved standards/context |
| `keyword_frequency_map` | Keywords useful for ATS/matching |
| `roast_issues` | Issues found by analysis |
| `rewritten_sections` | Candidate rewrites |
| `audit_flags` | Truthfulness audit output |
| `optimized_cv` | Final structured CV |
| `overall_improvement_score` | Pipeline improvement signal |

## Guardrails

- Low-impact comments are filtered to avoid noisy suggestions.
- Rewrite focuses on high/critical issues.
- Numeric claims are rejected when the original CV has no evidence.
- Audit compares rewritten text against original content before applying changes.
- The deterministic scorecard provides a stable score even when LLM output varies.

## Template Rendering

`CVTemplateRenderer` is separate from `OptimizationService`.

| Method | Description |
|---|---|
| `render_cv` | Returns structured JSON for a named template |
| `render_pdf` | Produces PDF bytes through WeasyPrint or JSON fallback bytes |

Supported template names depend on `template_renderer.py`; API defaults to `harvard`.

## Dependencies

| Dependency | Used for |
|---|---|
| `LLMConnector` | Agent analysis, rewrite and audit |
| `BaseVectorRepository` | Retrieval context |
| `GraphRepository` | Optional skill relationship context |
| `RelationalRepository[CVRecord]` | Load/update CV record |
| `build_cv_scorecard` | Deterministic scoring |

## Known Follow-Ups

- Validate `OptimizationRequest.mode` as a `Literal`.
- Reduce partial commit risk by grouping updates.
- Add output provenance metadata: LLM backend, fallback/cached status.
- Add UI inquiry loop for missing context before rewrite.
