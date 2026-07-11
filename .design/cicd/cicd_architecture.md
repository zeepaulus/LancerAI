# LancerAI CI/CD Architecture

## Workflow Overview

- `ci.yml`: validates workflow syntax, shell scripts, Docker Compose files, backend quality/tests/migrations, frontend install/build, and Docker smoke checks.
- `security.yml`: runs secret scanning, dependency audit, Trivy filesystem scanning, and CodeQL.
- `release-deploy.yml`: builds immutable GHCR images, creates GitHub releases for production tags, deploys staging or production through GitHub Environments, and supports rollback.

## Triggers

- Pull requests to `main`: `ci.yml` and `security.yml`.
- Push to `main`: `ci.yml` and `security.yml`.
- Weekly schedule: `security.yml`.
- Tags matching `v*`: `release-deploy.yml` defaults to production deploy.
- Manual dispatch: `ci.yml`, `security.yml`, and `release-deploy.yml`.

## Dependencies

- Backend CI: Python 3.11, uv, PostgreSQL 16 service, Redis 7 service.
- Frontend CI: Node 22, npm lockfile.
- Docker CI: Docker Buildx, Docker Compose v2.
- Security: Gitleaks, pip-audit, npm audit, Trivy, CodeQL.
- Deployments: SSH server with Docker Compose and a production-ready `.env`.

## CI Job Graph

- `workflow-validation`: actionlint, deployment shell script syntax, and Compose config validation.
- `backend`: Ruff, format check, compile check, import check, pytest coverage, and Alembic validation.
- `frontend`: npm install, optional lint/test scripts when present, and Vite production build.
- `docker`: backend/frontend image builds plus lightweight compose smoke checks.

## Release And Deploy Job Graph

- `resolve`: normalizes operation, target environment, image tag, and image names.
- `build-images`: builds and pushes backend/frontend images for deploy operations.
- `github-release`: creates a GitHub Release for production deploys.
- `deploy-staging` and `deploy-production`: deploy through the corresponding GitHub Environment.
- `rollback-staging` and `rollback-production`: run the rollback helper on the selected host.

## Artifacts

- Backend coverage: `coverage.xml`.
- Frontend dist: `frontend/dist`.
- Docker smoke logs on failure: `docker-compose-smoke.log`.

## Environments

- `staging`: used by `release-deploy.yml`; should have reviewer rules if staging is shared.
- `production`: used by `release-deploy.yml`; must require manual reviewer approval.

## Image Tags

- Staging manual deploy: `ghcr.io/<owner>/lancerai-backend:<short-sha>` and `staging-latest`.
- Production tag deploy: `ghcr.io/<owner>/lancerai-backend:<version>` and `production-latest`.
- Production deploys require an immutable semantic version tag.

## Service Exposure

- Production compose exposes nginx only.
- Backend, frontend container, PostgreSQL, Redis, ChromaDB, and Neo4j stay on the internal Docker network.
- nginx proxies `/health` and `/ready` to FastAPI for deployment checks.
