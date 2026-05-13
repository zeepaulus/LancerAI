# `tests/`

Pytest test suite (123 tests). `conftest.py` sets environment variables (`AUTH_*`, etc.) before importing the app and provides an `async_db_session` fixture using SQLite in-memory + ORM metadata.

```bash
uv run pytest          # run all tests
uv run pytest -v       # verbose output
uv run pytest -k auth  # filter by keyword
```

Test modules:
- `test_api_routes.py` — FastAPI endpoint integration tests
- `test_auth_dependency.py` — `get_current_user` / JWT dependency
- `test_database.py` — async DB session + repository
- `test_models.py` — SQLAlchemy ORM model integrity
- `test_schemas.py` — Pydantic request/response schema validation
- `test_settings.py` — environment-driven config validation
- `test_vector_repository.py` — ChromaDB / Qdrant repository layer
- `test_workers.py` — Celery task stubs
- `test_optimization_graph.py` — LangGraph agent node contracts

To expand: add integration tests against real Docker Compose services by marking them `@pytest.mark.integration` and running with a separate `docker compose`-backed session.
