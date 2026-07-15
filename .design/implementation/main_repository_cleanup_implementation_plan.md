# Main Repository Cleanup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remove only proven redundant code, obsolete workflow documents, unused assets, fake social authentication, and authorized local artifacts from `main` while preserving a complete runnable project.

**Architecture:** Use repository-hygiene regression tests to define the deletion boundary before changing tracked files. Keep implemented credential auth and all application routes intact, remove fake social behavior and dead assets/configuration, then validate the full Python and frontend builds.

**Tech Stack:** Python 3.11, pytest, Ruff, FastAPI/TestClient, React 18, Vite 8, Git

## Global Constraints

- Work only on the current `main` branch, as explicitly authorized by the user.
- Keep `.design/`, `.env`, `.venv/`, `frontend/node_modules/`, `models/`, `.agent/`, and `.agents/`.
- Do not remove any currently implemented frontend route, backend endpoint, migration, test, deployment file, lock file, or referenced asset.
- Delete `bao_cao_UI/` and `.codex_tmp/` locally only; never stage them.
- Use `apply_patch` for tracked file edits/deletions and verified literal PowerShell paths for local recursive deletion.

---

### Task 1: Remove Fake Social Authentication

**Files:**
- Create: `tests/test_repository_hygiene.py`
- Modify: `frontend/src/pages/AuthPage.jsx`
- Modify: `frontend/src/config/storageKeys.js`
- Modify: `frontend/src/components/Layout/Navbar.jsx`
- Modify: `frontend/src/index.css`
- Modify: `.design/implementation/visual_assets_plan.md`
- Modify: `.design/implementation/frontend_architecture.md`
- Delete: `frontend/src/assets/Logo/google_logo.png`
- Delete: `frontend/src/assets/Logo/microsoft_logo.png`
- Delete: `frontend/src/assets/Logo/linkedin_logo.png`
- Delete: `frontend/src/assets/Logo/github_logo.png`

**Interfaces:**
- Consumes: existing `apiLogin`, `apiSignup`, `apiMe`, local credential forms, and logout behavior.
- Produces: credential-only login/signup UI; no `handleSocialLogin`, shared social password, provider buttons, provider logos, or legacy mock storage key.

- [x] **Step 1: Write the failing repository-hygiene test**

Create `tests/test_repository_hygiene.py` with:

```python
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _frontend_source() -> str:
    source_root = ROOT / "frontend" / "src"
    source_files = (
        path
        for pattern in ("*.js", "*.jsx", "*.css")
        for path in source_root.rglob(pattern)
    )
    return "\n".join(path.read_text(encoding="utf-8") for path in source_files)


def test_fake_social_authentication_is_absent() -> None:
    source = _frontend_source()
    auth_page = (ROOT / "frontend/src/pages/AuthPage.jsx").read_text(encoding="utf-8")

    assert "SocialLoginPassword123!" not in source
    assert "handleSocialLogin" not in auth_page
    assert "LANCERAI_MOCK_USER_LEGACY" not in source

    for name in ("google_logo.png", "microsoft_logo.png", "linkedin_logo.png", "github_logo.png"):
        assert not (ROOT / "frontend/src/assets/Logo" / name).exists()
```

- [x] **Step 2: Run the test and verify RED**

Run: `uv run pytest tests/test_repository_hygiene.py::test_fake_social_authentication_is_absent -v`

Expected: FAIL because the hardcoded password, handler, legacy key, and provider logos currently exist.

- [x] **Step 3: Remove fake social behavior and its exclusive resources**

Use `apply_patch` to:

- remove provider logo imports, `socials`, `handleSocialLogin`, the divider, and social buttons from `AuthPage.jsx`;
- remove every `localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY)` call from `AuthPage.jsx` and `Navbar.jsx`;
- remove `LANCERAI_MOCK_USER_LEGACY` from `storageKeys.js`;
- remove CSS rules whose selectors are exclusively `.auth-divider`, `.auth-socials`, or `.auth-social-btn`;
- delete the four provider logo files;
- remove the social-logo/OAuth-action entries tied to this fake UI from the two listed `.design/implementation/` documents.

Do not change local credential login, signup, `me()` hydration, logout token removal, or navigation.

- [x] **Step 4: Verify GREEN and build the frontend**

Run:

```powershell
uv run pytest tests/test_repository_hygiene.py::test_fake_social_authentication_is_absent -v
Push-Location frontend
npm run build
Pop-Location
```

Expected: the hygiene test passes and Vite exits 0.

- [x] **Step 5: Commit the fake-auth removal**

```powershell
git add -- tests/test_repository_hygiene.py frontend/src/pages/AuthPage.jsx frontend/src/config/storageKeys.js frontend/src/components/Layout/Navbar.jsx frontend/src/index.css frontend/src/assets/Logo .design/implementation/visual_assets_plan.md .design/implementation/frontend_architecture.md .design/implementation/main_repository_cleanup_implementation_plan.md
git commit -m "fix(auth): remove fake social login"
```

### Task 2: Remove Obsolete Documents and Dead Assets

**Files:**
- Modify: `tests/test_repository_hygiene.py`
- Modify: `.design/assets/asset_manifest.md`
- Modify: `.design/assets/asset_sources.md`
- Delete: `docs/superpowers/plans/2026-07-15-current-ui-report.md`
- Delete: `docs/superpowers/plans/2026-07-15-disable-display-name-editing.md`
- Delete: `docs/superpowers/specs/2026-07-15-current-ui-report-design.md`
- Delete: `docs/superpowers/specs/2026-07-15-disable-display-name-editing-design.md`
- Delete: the 13 unused assets enumerated in the approved design

**Interfaces:**
- Consumes: the retained canonical illustrations imported by `frontend/src/components/Common/Visuals.jsx`.
- Produces: no tracked Superpowers workflow output, no unreferenced listed asset, and no stale asset manifest row for deleted vendor files.

- [x] **Step 1: Add a failing obsolete-artifact test**

Append to `tests/test_repository_hygiene.py`:

```python
OBSOLETE_TRACKED_PATHS = (
    "docs/superpowers",
    "frontend/src/assets/backgrounds/lancerai-grid.svg",
    "frontend/src/assets/icons/alert-triangle.svg",
    "frontend/src/assets/icons/badge-check.svg",
    "frontend/src/assets/icons/lightbulb.svg",
    "frontend/src/assets/icons/search.svg",
    "frontend/src/assets/landing_image.png",
    "frontend/src/assets/lottie/ai-thinking-dots.json",
    "frontend/src/assets/lottie/recording-pulse.json",
    "frontend/src/assets/illustrations/vendor/storyset",
)


def test_obsolete_tracked_artifacts_are_absent() -> None:
    for relative_path in OBSOLETE_TRACKED_PATHS:
        assert not (ROOT / relative_path).exists(), relative_path
```

- [x] **Step 2: Run the test and verify RED**

Run: `uv run pytest tests/test_repository_hygiene.py::test_obsolete_tracked_artifacts_are_absent -v`

Expected: FAIL on `docs/superpowers` or the first unused asset.

- [x] **Step 3: Delete only the enumerated tracked artifacts**

Use `apply_patch` to delete the four Superpowers files and the exact unused asset files from the design. Remove manifest/source rows that describe only deleted vendor assets. Preserve all canonical illustration files imported by `Visuals.jsx`.

- [x] **Step 4: Verify GREEN and scan references**

Run:

```powershell
uv run pytest tests/test_repository_hygiene.py::test_obsolete_tracked_artifacts_are_absent -v
rg -n "lancerai-grid|alert-triangle|badge-check|lightbulb|search\.svg|landing_image|ai-thinking-dots|recording-pulse|vendor/storyset|docs/superpowers" frontend .design docs README.md DESIGN.md
```

Expected: the test passes; `rg` has no stale reference except explanatory history in the cleanup design/plan, which may name deleted paths intentionally.

- [x] **Step 5: Commit obsolete artifact removal**

```powershell
git add -- tests/test_repository_hygiene.py docs/superpowers frontend/src/assets .design/assets
git commit -m "chore: remove obsolete repository artifacts"
```

### Task 3: Remove Dead Backend Configuration

**Files:**
- Modify: `tests/test_api_routes.py`
- Modify: `app/main.py`

**Interfaces:**
- Consumes: FastAPI CORS middleware and current registered route methods.
- Produces: CORS rejects PATCH preflight; no unused app-level `NotImplementedError` handler or `JSONResponse` import.

- [x] **Step 1: Write the failing CORS test**

Add to the system/auth route tests in `tests/test_api_routes.py`:

```python
def test_cors_rejects_patch_preflight(integration_client: TestClient) -> None:
    response = integration_client.options(
        "/api/v1/auth/me",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "PATCH",
        },
    )

    assert response.status_code == 400
```

- [x] **Step 2: Run the test and verify RED**

Run: `uv run pytest tests/test_api_routes.py::TestAuthRoutes::test_cors_rejects_patch_preflight -v`

Expected: FAIL because current CORS configuration permits PATCH and returns 200.

- [x] **Step 3: Remove dead configuration**

In `app/main.py`:

- change `allow_methods` to `["GET", "POST", "PUT", "DELETE", "OPTIONS"]`;
- remove the `JSONResponse` import;
- delete `_not_implemented_handler` and its decorator.

- [x] **Step 4: Verify GREEN and run focused backend checks**

Run:

```powershell
uv run pytest tests/test_api_routes.py::TestAuthRoutes::test_cors_rejects_patch_preflight tests/test_auth_dependency.py -v
uv run ruff check app tests
```

Expected: tests and Ruff pass.

- [x] **Step 5: Commit backend cleanup**

```powershell
git add -- app/main.py tests/test_api_routes.py
git commit -m "chore(api): remove unused patch configuration"
```

### Task 4: Update Hygiene Rules, TODO, and Local Artifacts

**Files:**
- Modify: `tests/test_repository_hygiene.py`
- Modify: `.gitignore`
- Modify: `TODO.md`
- Delete locally, never stage: `.codex_tmp/`, `bao_cao_UI/` if present, `CV _PhamNgocDuy.pdf`, `.coverage`, `coverage.xml`, `docker-compose-smoke.log`, `vite-dev.err.log`, `vite-dev.out.log`, `frontend/vite-dev.err.log`, `frontend/vite-dev.log`, `logs/`, `test_chroma_tmp/`, and `frontend/dist/`

**Interfaces:**
- Consumes: current verified test totals and tracked auth behavior.
- Produces: ignore rules for local report/tool folders and a TODO that describes immutable display names and current verification state.

- [x] **Step 1: Add a failing ignore-rule test**

Append to `tests/test_repository_hygiene.py`:

```python
def test_local_report_directories_are_ignored() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".codex_tmp/" in gitignore
    assert "bao_cao_UI/" in gitignore
```

- [x] **Step 2: Run the test and verify RED**

Run: `uv run pytest tests/test_repository_hygiene.py::test_local_report_directories_are_ignored -v`

Expected: FAIL because neither directory has an explicit ignore rule.

- [x] **Step 3: Update tracked hygiene and TODO files**

Use `apply_patch` to add `.codex_tmp/` and `bao_cao_UI/` to `.gitignore`. Update `TODO.md` so authentication states display names are immutable after signup, removes the obsolete profile PATCH claim, preserves valid open backlog, and uses the fresh test total from final verification.

- [x] **Step 4: Delete explicitly authorized/generated local artifacts safely**

Resolve the workspace root and each existing target to an absolute path. Before deletion, require every resolved target to start with the workspace root plus a directory separator. Then use `Remove-Item -LiteralPath` only for the exact local paths in this task; do not use `git clean` and do not delete `.env`, `.venv`, `frontend/node_modules`, `models`, `.agent`, or `.agents`.

- [x] **Step 5: Verify GREEN and commit hygiene files**

Run:

```powershell
uv run pytest tests/test_repository_hygiene.py -v
git check-ignore -v -- .codex_tmp bao_cao_UI
git add -- .gitignore TODO.md tests/test_repository_hygiene.py
git commit -m "chore: finalize repository hygiene"
```

Expected: hygiene tests pass, both paths are ignored, and the commit contains no local artifact.

### Task 5: Full Verification and Final Audit

**Files:**
- Modify: `.design/implementation/main_repository_cleanup_implementation_plan.md` (mark completed steps)

**Interfaces:**
- Consumes: all cleanup tasks.
- Produces: verified `main` with only intentional cleanup commits and no unrelated staged/untracked report content.

- [ ] **Step 1: Run the complete quality gate**

```powershell
uv run ruff check app tests
uv run pytest -q
Push-Location frontend
npm run build
Pop-Location
```

Expected: Ruff passes, pytest reports zero failures, and Vite exits 0.

- [ ] **Step 2: Verify repository references and Markdown links**

Run source/reference scans for removed social auth strings, deleted asset names, `docs/superpowers`, the old profile PATCH claim, and broken relative Markdown links. Expected: no unintended stale reference.

- [ ] **Step 3: Inspect the final Git boundary**

Run:

```powershell
git diff --check
git status --short
git log -8 --oneline
```

Expected: no whitespace errors; only the plan checklist may remain modified before its final commit; `.design/` remains present.

- [ ] **Step 4: Commit the completed implementation plan**

```powershell
git add -- .design/implementation/main_repository_cleanup_implementation_plan.md
git commit -m "docs: complete main repository cleanup plan"
```
