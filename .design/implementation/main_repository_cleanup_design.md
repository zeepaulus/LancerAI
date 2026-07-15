# Main Repository Cleanup Design

## Goal

Keep the `main` branch as a complete, runnable source project while removing only files, UI behavior, assets, and documentation that are demonstrably obsolete, duplicated, generated, or not implemented.

## Safety Boundary

- Work only on the current `main` branch.
- Delete tracked files only when `git ls-files` confirms they belong to `main` and repository search confirms they are unused, duplicated, obsolete process output, or tied exclusively to unimplemented behavior.
- Preserve `.design/`, application routes, backend services, migrations, tests, deployment configuration, lock files, core documentation, and all assets referenced by current source code.
- Preserve local `.env`, `.venv/`, `frontend/node_modules/`, `models/`, `.agent/`, and `.agents/` directories.
- Do not refactor long functions or partially implemented integrations during this cleanup.
- Delete the untracked `bao_cao_UI/` and `.codex_tmp/` directories only because the user explicitly authorized their local removal. They must never be staged or committed.

## Tracked Cleanup Scope

### Remove obsolete process documents

Delete the four tracked files under `docs/superpowers/`. They record agent workflow rather than product architecture or operating instructions. Keep the project documentation under `docs/` and the design history under `.design/`.

### Remove unimplemented social authentication

The social buttons in `frontend/src/pages/AuthPage.jsx` do not implement OAuth. They generate deterministic local email addresses and use the shared hardcoded password `SocialLoginPassword123!` to create or log into ordinary accounts. Remove:

- the four provider-logo imports and `socials` configuration;
- `handleSocialLogin`;
- the social divider and provider buttons;
- CSS selectors used only by those removed elements;
- the four provider logo image files;
- the obsolete `LANCERAI_MOCK_USER_LEGACY` storage key and all calls that clear it.

Email/display-name login, signup, profile hydration, logout, and auth guarding remain unchanged.

### Remove unused and duplicated frontend assets

Delete the following source assets after a final reference search confirms they have no import, CSS URL, HTML, or manifest consumer:

- `frontend/src/assets/backgrounds/lancerai-grid.svg`
- `frontend/src/assets/icons/alert-triangle.svg`
- `frontend/src/assets/icons/badge-check.svg`
- `frontend/src/assets/icons/lightbulb.svg`
- `frontend/src/assets/icons/search.svg`
- `frontend/src/assets/landing_image.png`
- `frontend/src/assets/lottie/ai-thinking-dots.json`
- `frontend/src/assets/lottie/recording-pulse.json`
- `frontend/src/assets/illustrations/vendor/storyset/artificial-intelligence-bro.svg`
- `frontend/src/assets/illustrations/vendor/storyset/chat-bot-pana.svg`
- `frontend/src/assets/illustrations/vendor/storyset/data-extraction-bro.svg`
- `frontend/src/assets/illustrations/vendor/storyset/image-upload-bro.svg`
- `frontend/src/assets/illustrations/vendor/storyset/job-hunt-bro.svg`

Three vendor illustrations are byte-identical duplicates of canonical assets that remain in use. The other listed assets have no source reference and are not emitted by Vite.

### Remove backend configuration with no consumer

- Remove `PATCH` from CORS allowed methods because `main` registers no PATCH endpoint.
- Remove the application-level `NotImplementedError` handler and its now-unused `JSONResponse` import because no registered application route raises that exception. Existing service error handling remains unchanged.

## Documentation Updates

- Keep `TODO.md`, but update authentication status to state that display names are immutable after signup and remove the obsolete claim that `PATCH /auth/me` updates profiles.
- Refresh test-count/status statements from the final verification output.
- Preserve valid open backlog items rather than presenting them as implemented features.
- Update only `.design/` entries that directly advertise the removed fake social authentication or removed assets. Other design, audit, and future-planning material remains intact.
- Add `.codex_tmp/` and `bao_cao_UI/` to `.gitignore` so those local artifacts cannot be accidentally committed again.

## Local Artifact Cleanup

Delete only known generated or explicitly authorized local artifacts:

- `.codex_tmp/`
- `bao_cao_UI/` when present
- root test CV PDF files
- coverage reports, temporary test databases/directories, generated logs, and frontend build output

Do not delete dependency environments, model weights, or secret configuration.

## Verification

1. Add a source-contract regression check proving social provider credentials, buttons, logos, and the legacy mock key are absent.
2. Confirm every deleted asset has no remaining reference.
3. Run `uv run ruff check app tests`.
4. Run the full default backend suite with `uv run pytest -q`.
5. Run `npm run build` in `frontend/`.
6. Run stale-reference scans, Markdown local-link checks, and `git diff --check`.
7. Confirm `git status --short` contains only intentional tracked changes before committing.

## Acceptance Criteria

1. The application retains all currently implemented frontend routes and backend endpoints.
2. Login and signup expose only the implemented credential flow.
3. No tracked social-auth mock code, obsolete Superpowers document, unused listed asset, or stale display-name update claim remains.
4. `.design/` remains present.
5. Local runtime dependencies and model files remain present and uncommitted.
6. Ruff, pytest, and the production frontend build pass.
