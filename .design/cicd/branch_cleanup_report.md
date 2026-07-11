# Branch Cleanup Report

Date: 2026-07-12

## 1. Branches Found Before Cleanup

Local branches:

```text
Bao-version
baseline
chungdat
main
refactor/technical-debt
```

Remote branches:

```text
origin/Bao-version
origin/Hung-version
origin/dependabot/docker/docker-minor-patch-a1b840253f
origin/dependabot/docker/node-26-alpine
origin/dependabot/github_actions/actions/upload-artifact-7
origin/dependabot/github_actions/astral-sh/setup-uv-7
origin/dependabot/github_actions/docker/login-action-4
origin/dependabot/github_actions/docker/setup-buildx-action-4
origin/dependabot/github_actions/gitleaks/gitleaks-action-3
origin/dependabot/npm_and_yarn/frontend/frontend-minor-patch-b53666f74c
origin/dependabot/npm_and_yarn/frontend/react-19.2.7
origin/dependabot/npm_and_yarn/frontend/react-dom-19.2.7
origin/dependabot/npm_and_yarn/frontend/react-router-dom-7.18.1
origin/dependabot/uv/celery-redis--gte-5.6.3
origin/dependabot/uv/mypy-2.2.0
origin/dependabot/uv/python-minor-patch-dbd33b4302
origin/dependabot/uv/sqlalchemy-asyncio--gte-2.0.51
origin/dependabot/uv/weasyprint-69.0
origin/main
origin/refactor/technical-debt
origin/ui
```

No branches named `backend-ci`, `frontend-ci`, `docker-ci`, `security-ci`, `release-ci`, `deploy-staging`, `deploy-production`, `cicd/*`, `devops/*`, or `workflow/*` existed at audit time.

## 2. Branches Retained

Local:

```text
main
```

Remote:

```text
origin/main
origin/Hung-version
origin/dependabot/*
```

`origin/Hung-version` was retained because it contains two commits not present in `main`. Dependabot branches were retained because each contains dependency-update work not present in `main`.

## 3. Branches Deleted Locally

Deleted safely with `git branch -d` after verifying each branch was merged into `main` and had zero unique commits:

```text
Bao-version
baseline
chungdat
refactor/technical-debt
```

## 4. Branches Deleted Remotely

Deleted with `git push origin --delete` after verifying branch-only commit count was zero:

```text
Bao-version
refactor/technical-debt
ui
```

## 5. Branches Not Deleted And Why

```text
origin/Hung-version
```

Reason: contains unique commits not present in `main`.

```text
origin/dependabot/*
```

Reason: Dependabot branches contain unique dependency updates and should be reviewed, merged, or closed through the normal PR process.

## 6. Unique Commits Protected

`origin/Hung-version`:

```text
13c54a6 feat(prompt): add rubric-based evaluation standards for CV and interview
cf7008b feat(data): improve schema and persist component scores
```

Each Dependabot branch has one unique dependency-update commit and was preserved.

## 7. Backup Tag

No backup tag was created. The meaningful current CI/CD commit already existed on both local `main` and `origin/main`, and unmerged remote work was preserved rather than deleted.

## 8. Final Workflow Structure

```text
.github/workflows/
  ci.yml
  security.yml
```

Removed workflow files:

```text
.github/workflows/backend-ci.yml
.github/workflows/frontend-ci.yml
.github/workflows/docker-ci.yml
.github/workflows/release.yml
.github/workflows/deploy-staging.yml
.github/workflows/deploy-production.yml
.github/workflows/release-deploy.yml
```

## 9. Final Branching Strategy

The final strategy is GitHub Flow / trunk-based:

```text
main
feature/<task>
fix/<bug>
chore/<maintenance>
docs/<documentation>
test/<testing>
```

Do not keep permanent `staging`, `production`, `release`, or workflow-specific branches.

Deployment automation is intentionally not configured. The current GitHub Actions setup is CI-only.

## 10. CI Validation Results

Passed locally:

```text
git diff --check
docker run --rm -v "${PWD}:/repo" -w /repo rhysd/actionlint:1.7.7 -color
docker compose config --quiet
docker compose --env-file .env.test.example -f docker-compose.test.yml config --quiet
docker compose --env-file .env.test.example -f docker-compose.prod.yml config --quiet
uv run ruff check app tests
uv run ruff format --check app tests
uv run python -m compileall -q app tests
uv run pytest -q
npm run build
uv run alembic heads
```

Observed backend test result:

```text
171 passed, 7 deselected, 2 warnings
```

Alembic head:

```text
d4e5f6a7b8c9
```

Not executed locally:

```text
Full Docker smoke stack after workflow consolidation
```

## 11. Manual GitHub Settings Still Required

- Protect `main`.
- Require Pull Requests before merge.
- Require at least one approval if the team can support it.
- Require conversation resolution.
- Disable force pushes on `main`.
- Prefer squash merge.
- Delete short-lived branches after merge.
- Configure required checks from `CI` and `Security`.
- Review or close preserved Dependabot branches.
- Review `origin/Hung-version` and merge/cherry-pick only if the two unique commits are still desired.
