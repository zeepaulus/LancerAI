# Branching Strategy

Date: 2026-07-12

LancerAI uses a simple GitHub Flow / trunk-based model. The repository is small enough that permanent staging, production, release, and workflow-specific branches add cost without adding safety.

## Long-Lived Branches

```text
main
```

`main` must contain stable, reviewable code. It is the only long-lived branch.

## Short-Lived Branches

Allowed branch prefixes:

```text
feature/<task>
fix/<bug>
chore/<maintenance>
docs/<documentation>
test/<testing>
```

## Rules

1. Branch from latest `main`.
2. Keep each branch focused on one task.
3. Open a Pull Request into `main`.
4. CI must pass before merge.
5. Require review if repository settings support it.
6. Prefer squash merge for short-lived branches.
7. Delete the branch after successful merge.
8. Do not create permanent branches for CI, staging, production, or release bookkeeping.

## Branches To Avoid

Do not keep permanent branches for:

```text
staging
production
release
backend-ci
frontend-ci
docker-ci
security-ci
deploy-staging
deploy-production
cicd/*
devops/*
workflow/*
```

CI/CD workflow files live in `.github/workflows/` on normal product branches and merge into `main` through Pull Requests.

## CI Flow

```text
feature/fix/chore branch
-> Pull Request
-> CI and security checks
-> merge main
```

Deployment automation is intentionally not configured in GitHub Actions for the current project scope.
