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
8. Release production from immutable tags, not from a permanent production branch.

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

## Environments

Use GitHub Environments:

```text
staging
production
```

Do not represent environments with Git branches unless the repository has a documented operational reason.

## Deployment Flow

```text
feature/fix/chore branch
-> Pull Request
-> CI and security checks
-> merge main
-> manual staging deploy from Release and Deploy
-> create version tag
-> production environment approval
-> production deployment
```

## Release Tags

Production deploys should use immutable semantic version tags:

```text
v1.2.3
v1.2.3-rc.1
```

Rollback should use deployment state stored on the host by `scripts/deploy/compose_deploy.sh`, not a rollback branch.
