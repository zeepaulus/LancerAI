# LancerAI CI/CD Architecture

## Workflow Overview

- `ci.yml`: validates workflow syntax, Docker Compose files, backend quality/tests/migrations, frontend install/build, and Docker smoke checks.
- `security.yml`: runs secret scanning, dependency audit, Trivy filesystem scanning, and CodeQL.

## Triggers

- Pull requests to `main`: `ci.yml` and `security.yml`.
- Push to `main`: `ci.yml` and `security.yml`.
- Weekly schedule: `security.yml`.
- Manual dispatch: `ci.yml` and `security.yml`.

## Dependencies

- Backend CI: Python 3.11, uv, PostgreSQL 16 service, Redis 7 service.
- Frontend CI: Node 22, npm lockfile.
- Docker CI: Docker Buildx, Docker Compose v2.
- Security: Gitleaks, pip-audit, npm audit, Trivy, CodeQL.

## CI Job Graph

- `workflow-validation`: actionlint and Compose config validation.
- `backend`: Ruff, format check, compile check, import check, pytest coverage, and Alembic validation.
- `frontend`: npm install, optional lint/test scripts when present, and Vite production build.
- `docker`: backend/frontend image builds plus lightweight compose smoke checks.

## Artifacts

- Backend coverage: `coverage.xml`.
- Frontend dist: `frontend/dist`.
- Docker smoke logs on failure: `docker-compose-smoke.log`.

## Deployment Scope

Deployment automation is intentionally out of scope for the current repository setup. The GitHub Actions configuration is CI-only.
