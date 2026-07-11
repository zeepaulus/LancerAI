# LancerAI CI/CD Runbook

## Local Equivalent Commands

Backend:

```bash
uv sync --frozen
uv run ruff check app tests
uv run ruff format --check app tests
uv run python -m compileall -q app tests
uv run pytest --cov=app --cov-report=xml --cov-report=term-missing
```

Alembic:

```bash
uv run alembic heads
uv run alembic upgrade head
uv run alembic current
```

Frontend:

```bash
cd frontend
npm ci
npm run build
```

Docker:

```bash
docker compose config --quiet
ENV_FILE=.env.test.example docker compose --env-file .env.test.example -f docker-compose.prod.yml config --quiet
docker build --target backend -t lancerai-backend:ci .
docker build --target frontend-prod -t lancerai-frontend:ci .
docker compose -p lancerai-ci-local --env-file .env.test.example -f docker-compose.test.yml up -d --no-build postgres redis frontend
docker compose -p lancerai-ci-local --env-file .env.test.example -f docker-compose.test.yml run --rm --no-deps backend uv run --no-sync alembic upgrade head
docker compose -p lancerai-ci-local --env-file .env.test.example -f docker-compose.test.yml up -d --no-build backend
curl -fsS http://localhost:18000/health
curl -fsS http://localhost:18000/ready
curl -fsS http://localhost:13000/health
docker compose -p lancerai-ci-local -f docker-compose.test.yml down -v --remove-orphans
```

Security:

```bash
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:v8.24.3 detect --source /repo --no-git --config /repo/.gitleaks.toml -v
uv run --with pip-audit pip-audit --progress-spinner off --skip-editable
cd frontend && npm audit --audit-level=high
docker run --rm -v "$PWD:/repo" aquasec/trivy:0.58.2 fs --exit-code 1 --severity HIGH,CRITICAL --ignore-unfixed --skip-dirs /repo/frontend/node_modules --skip-dirs /repo/.venv /repo
```

## Required GitHub Secrets

Staging:

- `STAGING_HOST`
- `STAGING_USER`
- `STAGING_SSH_KEY`
- `STAGING_DEPLOY_PATH`
- `GHCR_USERNAME`
- `GHCR_TOKEN`

Production:

- `PRODUCTION_HOST`
- `PRODUCTION_USER`
- `PRODUCTION_SSH_KEY`
- `PRODUCTION_DEPLOY_PATH`
- `GHCR_USERNAME`
- `GHCR_TOKEN`

## Required GitHub Environments

- `staging`
- `production`

Production should require reviewer approval and disallow bypass for normal maintainers.

## Trigger Staging

- Push to `main`, or run `Deploy Staging` manually.
- The workflow builds and pushes SHA-tagged images, logs the remote host into GHCR, pulls images, backs up PostgreSQL, runs Alembic, restarts services, and checks health.

## Trigger Production

- Push a semantic version tag such as `v1.2.3`, or run `Deploy Production` manually with `image_tag`.
- The workflow verifies the GHCR images exist, waits for `production` environment approval, then deploys via `scripts/deploy/compose_deploy.sh`.

## Inspect Failed Runs

- Backend failures: inspect Ruff output, pytest failure, `coverage.xml`, or Alembic logs.
- Frontend failures: inspect `npm ci` and Vite build output.
- Docker failures: download `docker-compose-smoke-logs`.
- Security failures: inspect Gitleaks, pip-audit, npm audit, Trivy, or CodeQL results.
- Deploy failures: inspect SSH step logs and remote `docker compose -f docker-compose.prod.yml logs`.

## Branch Protection Recommendations

Require pull requests before merge into `main`, one approval, conversation resolution, no force pushes, no branch deletion, and these status checks:

- `Workflow Validation / actionlint, shell, and compose validation`
- `Backend CI / lint, import, test, and migrate`
- `Frontend CI / install, optional checks, and build`
- `Docker CI / compose, build, and smoke`
- `Security / Gitleaks secret scan`
- `Security / Python and npm dependency audit`
- `Security / Trivy filesystem scan`
- `Security / CodeQL analysis`
