# `tests/` - Pytest Suite

The test suite covers API routes, auth/security, models/repositories, settings, schema validation, optimization guardrails, matching, interview helpers, vector repository behavior and workers.

`tests/conftest.py` sets required env variables before app import and provides async DB fixtures.

## Commands

```bash
uv run pytest
uv run pytest -v
uv run pytest -k auth
uv run pytest --collect-only -q
```

Default pytest config deselects integration tests:

```toml
addopts = "-m 'not integration'"
```

Run integration tests explicitly:

```bash
uv run pytest -m integration
```

## Current Collection Snapshot

During this docs audit:

```text
171/178 tests collected (7 deselected)
```

One Starlette/httpx deprecation warning is currently emitted by the test client dependency stack.

## Test Areas

| File | Scope |
|---|---|
| `test_api_routes.py` | FastAPI route integration smoke tests |
| `test_auth_dependency.py` | JWT auth dependency and token resolution |
| `test_security.py` | Password hashing and JWT behavior |
| `test_settings.py` | Environment validation and defaults |
| `test_database.py` | Database engine/session behavior |
| `test_models.py` | ORM models and relational repository |
| `test_schemas.py` | Pydantic request/response validation |
| `test_vector_repository.py` | Vector repository factory and Chroma integration |
| `test_graph_repository.py` | Neo4j graph repository behavior |
| `test_llm_cache.py` | LLM cache hashing/similarity/repository behavior |
| `test_llm_hosted_config.py` | Hosted LLM routing |
| `test_cv_scorecard.py` | Deterministic CV scorecard |
| `test_optimization_graph.py` | LangGraph construction |
| `test_prompt_guardrails.py` | Roast/rewrite/audit prompt guardrails |
| `test_matching_scoring.py` | Matching score behavior |
| `test_matching_security.py` | JD URL SSRF guard |
| `test_interview_behavior.py` | Behavior observation scoring |
| `test_interview_pacing.py` | Interview pacing clock |
| `test_interview_scoring.py` | Interview score fallback |
| `test_topcv_crawler.py` | TopCV URL/parser utilities |
| `test_workers.py` | Celery worker tasks |

## Add New Tests

Add focused tests for every new contract:

- Router status code and auth behavior.
- Service fallback behavior.
- Schema validation for new request fields.
- Ownership checks for user-scoped resources.
- Worker retry/failure payload shape.
- Frontend changes should at least pass `npm run build`.
