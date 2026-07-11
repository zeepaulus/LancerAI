# LancerAI Current CI/CD Project Audit

Date: 2026-07-12

## 1. Current Project Structure

- `app/`: FastAPI backend, routers, core settings/database/connectors, services, repositories, models, Celery workers.
- `tests/`: pytest suite with 178 collected tests; default config deselects `integration` tests.
- `migration/alembic/`: Alembic environment and five migrations, current head `d4e5f6a7b8c9`.
- `frontend/`: React 18 + Vite frontend in JavaScript.
- `Dockerfile`: multi-target backend, frontend dev, frontend builder, and frontend prod image.
- `docker-compose.yml`: local development services for PostgreSQL, Redis, ChromaDB, Neo4j.
- `docker-compose.prod.yml`: production compose stack behind nginx.
- `nginx/nginx.conf`: public nginx proxy for frontend, API, `/health`, and now `/ready`.

## 2. Current Python Version

- `.python-version`: `3.11`
- `pyproject.toml`: `requires-python = ">=3.11"`
- Local `uv run python --version`: Python 3.11.9

## 3. Current Node.js Version

- `frontend/package-lock.json` lockfile version: 3.
- Vite `8.1.0`, `@vitejs/plugin-react 6.0.3`, and Rolldown packages require `node: ^20.19.0 || >=22.12.0`.
- Workflows use Node 22 to match the Dockerfile `node:22-alpine` target and satisfy Vite.

## 4. Existing Test Commands

- Backend default tests: `uv run pytest`
- Backend coverage: `uv run pytest --cov=app --cov-report=xml --cov-report=term-missing`
- Integration tests: `uv run pytest -m integration`
- Frontend tests: no `test` script currently exists.

## 5. Existing Lint Commands

- Backend lint: `uv run ruff check app tests`
- Backend format check: `uv run ruff format --check app tests`
- Backend strict mypy config exists, but `uv run mypy app tests` currently fails with 48 errors.
- Frontend lint: no `lint` script currently exists.

## 6. Existing Build Commands

- Frontend production build: `cd frontend && npm run build`
- Backend package build is handled by `uv sync`/Hatch.
- Docker backend image: `docker build --target backend -t lancerai-backend:ci .`
- Docker frontend prod image: `docker build --target frontend-prod -t lancerai-frontend:ci .`

## 7. Existing Docker Setup

- `Dockerfile` backend target uses Python 3.11 slim and uv.
- Backend image intentionally avoids CUDA Torch during uv sync, then installs CPU-only Torch/Torchaudio.
- `frontend-prod` target builds Vite assets and serves them with nginx on port 3000.
- Production compose exposes only nginx publicly; PostgreSQL, Redis, ChromaDB, Neo4j, backend, and frontend stay on the internal network.
- Added `docker-compose.test.yml` for lightweight CI smoke testing without ChromaDB, Qdrant, Neo4j, crawlers, GPU, or model downloads.

## 8. Existing Migration Setup

- Alembic config: `alembic.ini`
- Alembic env: `migration/alembic/env.py`
- DB URL comes from `app.core.settings`.
- Clean PostgreSQL migration validation passed locally against PostgreSQL 16.

## 9. Existing CI Workflows

- Previous `.github/workflows/ci.yml` ran backend and frontend in one workflow.
- It used Node 18, which is incompatible with the current Vite 8 lockfile.
- It ran mypy as required, but current mypy state is not green.

## 10. Missing CI/CD Capabilities Found

- No split backend/frontend/docker/security/release/deploy workflows.
- No workflow validation/actionlint.
- No safe CI env template.
- No Dependabot config.
- No release workflow or immutable GHCR image tagging.
- No staging/production deployment workflow with environment protection.
- No rollback runbook.
- No Docker smoke stack.
- Frontend has no lint/test scripts.
- Strict mypy config exists but current code is not type-clean.

## 11. External Services To Mock Or Disable In CI

- NVIDIA, Groq, hosted LLMs, local Ollama.
- faster-whisper model downloads and local STT model paths.
- VieNeu/Piper local TTS model downloads.
- SMTP/email.
- TopCV/ITviec/live crawling.
- Neo4j and ChromaDB/Qdrant for normal PR CI unless integration tests explicitly require them.

## 12. CI Stability Risks

- Backend dependency set is heavy; Docker backend build took about 7 minutes locally.
- `uv export` plus `pip-audit -r` cannot resolve CPU Torch `+cpu` wheels; security workflow audits the synced environment instead.
- Strict mypy currently fails with 48 errors.
- `pip-audit` currently reports 39 vulnerabilities across 15 packages.
- Frontend lint/test coverage is absent because package scripts are absent.
- FastAPI lifespan warms vector storage and seeds dummy jobs; CI import checks avoid running lifespan.

## 13. Final Workflow Structure

- `ci.yml`: actionlint, shell syntax, compose config validation, backend checks/tests/migrations, frontend install/build, and Docker smoke validation.
- `security.yml`: Gitleaks, pip-audit, npm audit, Trivy filesystem scan, and CodeQL.
- `release-deploy.yml`: versioned GHCR images, GitHub Release creation, staging deploy, production deploy with GitHub Environment protection, and rollback.
