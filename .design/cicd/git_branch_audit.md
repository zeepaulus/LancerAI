# Git Branch Audit

Date: 2026-07-12

## Audit Commands

Commands run before cleanup:

```bash
git fetch --all --prune
git status
git branch --show-current
git branch -vv
git branch --merged main
git branch --no-merged main
git branch -r
git log --oneline --decorate --graph --all --max-count=200
```

Additional verification used:

```bash
git merge-base --is-ancestor <branch> main
git rev-list --count main..<branch>
git rev-list --left-right --count main...<branch>
git log --oneline main..<branch>
```

Working tree was clean before branch deletion. `main` was up to date with `origin/main`. Commit SHAs in the tables are abbreviated to 12 characters.

## Local Branches Found Before Cleanup

| Branch | Latest commit | Latest message | Merged into `main` | Exists on remote | Unique commits not in `main` | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| `Bao-version` | `48cc69339587` | `feat(camera): add standard-compliant frame-diff motion detection for restless_motion check` | Yes | Yes, but remote pointed to `bc81ece52ee2` | No | Delete local; merged and stale. |
| `baseline` | `ab83c261f6f8` | `feat: implement core AI services for CV extraction, optimization, interview simulation, and job matching pipelines` | Yes | No | No | Delete local; merged and obsolete. |
| `chungdat` | `6a5f3a48c200` | `bổ sung & nâng cấp giao diện` | Yes | No | No | Delete local; merged and obsolete. |
| `main` | `e971e1f4f8a2` | `chore: strengthen CI/CD automation` | Yes | Yes | No | Keep; only long-lived branch. |
| `refactor/technical-debt` | `3726fd647482` | `test: fix sqlalchemy session mock to resolve runtime warnings` | Yes | Yes | No | Delete local; merged by PR and stale. |

## Remote Branches Found Before Cleanup

| Branch | Latest commit | Latest message | Merged into `main` | Exists on remote | Unique commits not in `main` | Recommendation |
| --- | --- | --- | --- | --- | --- | --- |
| `origin/Bao-version` | `bc81ece52ee2` | `fix(tts): sanitize markdown from LLM output before sending to edge-tts` | Yes | Yes | No | Delete remote; merged and obsolete. |
| `origin/Hung-version` | `13c54a692774` | `feat(prompt): add rubric-based evaluation standards for CV and interview` | No | Yes | Yes, 2 commits | Keep until reviewed, merged, or intentionally closed. |
| `origin/dependabot/docker/docker-minor-patch-a1b840253f` | `fb002f48795e` | `build(deps): bump the docker-minor-patch group with 2 updates` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/docker/node-26-alpine` | `aa0a07fb9ccf` | `build(deps): bump node from 22-alpine to 26-alpine` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/github_actions/actions/upload-artifact-7` | `523f2f4aa6e8` | `build(deps): bump actions/upload-artifact from 4 to 7` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/github_actions/astral-sh/setup-uv-7` | `a9241b18fb8b` | `build(deps): bump astral-sh/setup-uv from 5 to 7` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/github_actions/docker/login-action-4` | `771f64d870e8` | `build(deps): bump docker/login-action from 3 to 4` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/github_actions/docker/setup-buildx-action-4` | `0397a16abea8` | `build(deps): bump docker/setup-buildx-action from 3 to 4` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/github_actions/gitleaks/gitleaks-action-3` | `db7a813ab1b0` | `build(deps): bump gitleaks/gitleaks-action from 2 to 3` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/npm_and_yarn/frontend/frontend-minor-patch-b53666f74c` | `09c75a2a0d05` | `build(deps-dev): bump vite` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/npm_and_yarn/frontend/react-19.2.7` | `ddc013ebcdfc` | `build(deps): bump react from 18.3.1 to 19.2.7 in /frontend` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/npm_and_yarn/frontend/react-dom-19.2.7` | `1bc70414d35b` | `build(deps): bump react-dom from 18.3.1 to 19.2.7 in /frontend` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/npm_and_yarn/frontend/react-router-dom-7.18.1` | `d1f330eae75b` | `build(deps): bump react-router-dom from 6.30.4 to 7.18.1 in /frontend` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/uv/celery-redis--gte-5.6.3` | `5b70d9abaa28` | `build(deps): update celery[redis] requirement from >=5.4.0 to >=5.6.3` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/uv/mypy-2.2.0` | `998264331c20` | `build(deps): bump mypy from 1.20.2 to 2.2.0` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/uv/python-minor-patch-dbd33b4302` | `c9c07d24c20c` | `build(deps): bump the python-minor-patch group with 22 updates` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/uv/sqlalchemy-asyncio--gte-2.0.51` | `7538f5511e45` | `build(deps): update sqlalchemy[asyncio] requirement` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/dependabot/uv/weasyprint-69.0` | `7391cc4d82d8` | `build(deps): bump weasyprint from 68.1 to 69.0` | No | Yes | Yes, 1 commit | Keep; Dependabot update requires review. |
| `origin/main` | `e971e1f4f8a2` | `chore: strengthen CI/CD automation` | Yes | Yes | No | Keep; protected trunk branch. |
| `origin/refactor/technical-debt` | `3726fd647482` | `test: fix sqlalchemy session mock to resolve runtime warnings` | Yes | Yes | No | Delete remote; merged by PR and stale. |
| `origin/ui` | `5dd0c780d63b` | `feat(ui): refine landing page, dashboard` | Yes | Yes | No | Delete remote; merged and obsolete. |

## Protected Unique Commits

The following unmerged work was not deleted:

```text
origin/Hung-version
13c54a6 feat(prompt): add rubric-based evaluation standards for CV and interview
cf7008b feat(data): improve schema and persist component scores
```

Dependabot remote branches were initially preserved during the first safety pass because each contained a unique autogenerated dependency-update commit. After the project scope was clarified to CI checks only, the Dependabot config and generated `dependabot/*` branches were removed.

## CI/CD Branch Result

No remote or local branches named `backend-ci`, `frontend-ci`, `docker-ci`, `security-ci`, `release-ci`, `deploy-staging`, `deploy-production`, `cicd/*`, `devops/*`, or `workflow/*` were present at audit time. The CI/CD sprawl was in workflow files, not currently visible branch refs.
