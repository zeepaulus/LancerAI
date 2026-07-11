# LancerAI CI/CD Architecture

## Workflow Overview

- `Workflow Validation`: validates workflow YAML with actionlint, shell syntax, and compose config.
- `Backend CI`: validates Python backend quality, imports, tests, coverage, and Alembic migrations.
- `Frontend CI`: validates npm install and Vite production build; lint/test run only when scripts exist.
- `Docker CI`: builds backend and frontend images, then smoke-tests `/health`, `/ready`, and frontend `/health`.
- `Security`: runs Gitleaks, pip-audit, npm audit, Trivy filesystem scan, and CodeQL.
- `Release`: publishes immutable backend/frontend images to GHCR and creates a GitHub Release.
- `Deploy Staging`: pushes SHA-tagged images from `main` and deploys over SSH.
- `Deploy Production`: deploys a semantic version image tag with production environment approval.

## Triggers

- Pull requests to `main` or `dev`: validation, backend, frontend, Docker, security.
- Push to `main`: validation, backend, frontend, Docker, security, staging deploy.
- Tag `v*`: release and production deploy.
- Manual dispatch: all major workflows support manual execution where useful.

## Dependencies

- Backend CI: Python 3.11, uv, PostgreSQL 16 service, Redis 7 service.
- Frontend CI: Node 22, npm lockfile.
- Docker CI: Docker Buildx, Docker Compose v2.
- Security: Gitleaks, pip-audit, npm audit, Trivy, CodeQL.
- Deployments: SSH server with Docker Compose and a production `.env`.

## Job Graph

- Backend CI is a single job because tests and migrations share uv setup.
- Frontend CI is a single job because the project has no separate lint/test toolchain yet.
- Docker CI builds backend and frontend images before running smoke tests.
- Staging deployment has two jobs: `build-images` then `deploy`.
- Production deployment verifies immutable images before SSH deployment.

## Artifacts

- Backend coverage: `coverage.xml`.
- Frontend dist: `frontend/dist`.
- Release metadata: `release-metadata.json`.
- Docker smoke logs on failure: `docker-compose-smoke.log`.

## Environments

- `staging`: required for `deploy-staging.yml`; should have reviewer rules if staging is shared.
- `production`: required for `deploy-production.yml`; must require manual reviewer approval.

## Image Tags

- Main/staging: `ghcr.io/<owner>/lancerai-backend:<short-sha>` and `staging-latest`.
- Release: `ghcr.io/<owner>/lancerai-backend:<version>`, `<short-sha>`, and `latest`.
- Production deploys only an immutable semantic version tag.

## Service Exposure

- Production compose exposes nginx only.
- Backend, frontend container, PostgreSQL, Redis, ChromaDB, and Neo4j stay on the internal Docker network.
- nginx proxies `/health` and `/ready` to FastAPI for deployment checks.
