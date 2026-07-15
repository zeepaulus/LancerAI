# Disable Display Name Editing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make display names immutable after signup in both the web settings interface and authenticated HTTP API.

**Architecture:** Remove the profile-update route and its now-dead backend/client support instead of retaining an endpoint that always fails. Keep `GET /auth/me` as the single source for the read-only settings view, and retain signup, display-name login, and password-change behavior.

**Tech Stack:** FastAPI, Pydantic v2, SQLAlchemy async, pytest/TestClient, React 18, Vite 8

## Global Constraints

- `display_name` remains required during registration and usable as a login identifier.
- `GET /api/v1/auth/me` and `PUT /api/v1/auth/password` remain unchanged.
- `PATCH /api/v1/auth/me` must return HTTP 405 and must not mutate the user.
- No new frontend test dependency will be added; verify the source contract and production Vite build.
- Preserve unrelated untracked files and user changes.

---

### Task 1: Remove Display Name Mutation from the Backend

**Files:**
- Modify: `tests/test_api_routes.py`
- Modify: `app/router/v1/auth_api.py`
- Modify: `app/schema/request.py`
- Modify: `app/service/auth/service.py`

**Interfaces:**
- Consumes: existing `POST /api/v1/auth/signup`, `POST /api/v1/auth/login`, and `GET /api/v1/auth/me` routes.
- Produces: `PATCH /api/v1/auth/me` has no registered handler and therefore returns HTTP 405; no `UserProfileUpdateRequest` or `AuthService.update_profile` API remains.

- [x] **Step 1: Write the failing route regression test**

Add this method to `TestAuthRoutes` in `tests/test_api_routes.py`:

```python
def test_display_name_cannot_be_updated(self, integration_client: TestClient) -> None:
    integration_client.post(
        "/api/v1/auth/signup",
        json={
            "email": "immutable-name@example.com",
            "password": "secret123",
            "display_name": "Original Name",
        },
    )
    token = integration_client.post(
        "/api/v1/auth/login",
        json={"identifier": "immutable-name@example.com", "password": "secret123"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = integration_client.patch(
        "/api/v1/auth/me",
        json={"display_name": "Changed Name"},
        headers=headers,
    )

    assert response.status_code == 405
    profile = integration_client.get("/api/v1/auth/me", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["display_name"] == "Original Name"
```

- [x] **Step 2: Run the regression test and verify RED**

Run: `uv run pytest tests/test_api_routes.py::TestAuthRoutes::test_display_name_cannot_be_updated -v`

Expected: FAIL because the current route returns 200 and changes the name.

- [x] **Step 3: Remove the update route and dead backend support**

In `app/router/v1/auth_api.py`, remove `UserProfileUpdateRequest` from the schema import and delete the `@router.patch("/me")` handler.

In `app/schema/request.py`, delete:

```python
class UserProfileUpdateRequest(BaseModel):
    """Payload for updating the current user's visible profile."""

    display_name: str = Field(..., min_length=1, max_length=120)
```

In `app/service/auth/service.py`, delete the complete `AuthService.update_profile` method. Do not change signup, login, `me`, or password logic.

- [x] **Step 4: Run focused backend tests and verify GREEN**

Run: `uv run pytest tests/test_api_routes.py::TestAuthRoutes tests/test_schemas.py tests/test_models.py -v`

Expected: all selected tests pass, including the new HTTP 405 regression.

- [x] **Step 5: Commit the backend behavior change**

```powershell
git add -- tests/test_api_routes.py app/router/v1/auth_api.py app/schema/request.py app/service/auth/service.py
git commit -m "fix(auth): make display names immutable"
```

### Task 2: Make Account Settings Read-Only

**Files:**
- Modify: `frontend/src/pages/AccountSettingsPage.jsx`
- Modify: `frontend/src/api/auth.js`

**Interfaces:**
- Consumes: `me(): Promise<object>` from `frontend/src/api/auth.js` and the cached `LANCERAI_USER_PROFILE` value.
- Produces: a display-name input with `readOnly` and `aria-describedby="settings-display-name-note"`; no `updateMe` export or profile-submit control.

- [x] **Step 1: Add a failing source-contract check**

Run this PowerShell assertion before changing production files:

```powershell
$page = Get-Content -Raw 'frontend/src/pages/AccountSettingsPage.jsx'
$api = Get-Content -Raw 'frontend/src/api/auth.js'
if ($page -notmatch 'readOnly' -or
    $page -notmatch 'settings-display-name-note' -or
    $page -match 'handleProfileSubmit|savingProfile|Lưu hồ sơ' -or
    $api -match 'export function updateMe') { exit 1 }
```

Expected: exit code 1 because the settings field is editable and `updateMe` exists.

- [x] **Step 2: Remove frontend mutation state and API calls**

In `frontend/src/pages/AccountSettingsPage.jsx`:

- Change the auth import to `import { changePassword, me } from '../api/auth';`.
- Remove `displayName`, `savingProfile`, and `profileMessage` state.
- Remove `setDisplayName` from profile hydration.
- Delete `handleProfileSubmit`.
- Change the hero description to explain that account details are view-only and the password remains changeable.
- Replace the profile `<form>` with a `<div className="ui-stack">`.
- Bind the name input to `profile.display_name || ''`, add `readOnly`, and add `aria-describedby="settings-display-name-note"`.
- Add `<p id="settings-display-name-note" className="caption">Tên hiển thị được đặt khi đăng ký và không thể chỉnh sửa.</p>`.
- Remove the profile-save button and success badge.

In `frontend/src/api/auth.js`, delete:

```javascript
export function updateMe({ display_name }) {
    return apiJson(AUTH_ME_PATH, {
        method: 'PATCH',
        body: { display_name },
    });
}
```

- [x] **Step 3: Re-run the source-contract check**

Run the PowerShell assertion from Step 1.

Expected: exit code 0.

- [x] **Step 4: Build the frontend**

Run: `npm run build` from `frontend/`.

Expected: Vite production build succeeds with exit code 0.

- [x] **Step 5: Commit the frontend behavior change**

```powershell
git add -- frontend/src/pages/AccountSettingsPage.jsx frontend/src/api/auth.js
git commit -m "fix(settings): disable display name editing"
```

### Task 3: Remove Stale API Documentation and Verify the Repository

**Files:**
- Modify: `README.md`
- Modify: `docs/SYSTEM_OVERVIEW.md`
- Modify: `app/router/v1/README.md`
- Modify: `app/schema/README.md`
- Modify: `app/service/README.md`

**Interfaces:**
- Consumes: backend and frontend behavior established by Tasks 1 and 2.
- Produces: documentation that lists signup, login, current-profile reads, and password changes without advertising profile mutation.

- [x] **Step 1: Verify stale references exist**

Run:

```powershell
rg -n "PATCH.*auth/me|Update display name|UserProfileUpdateRequest|update profile" README.md docs/SYSTEM_OVERVIEW.md app/router/v1/README.md app/schema/README.md app/service/README.md
```

Expected: one or more stale references are printed.

- [x] **Step 2: Update documentation**

- Delete the `PATCH /api/v1/auth/me` endpoint row from `README.md` and `app/router/v1/README.md`.
- Delete `PATCH /api/v1/auth/me` from `docs/SYSTEM_OVERVIEW.md`.
- Delete the `UserProfileUpdateRequest` row from `app/schema/README.md`.
- Change the auth-service summary in `app/service/README.md` from “Signup, login, resolve token, update profile, change password” to “Signup, login, resolve token, change password”.

- [x] **Step 3: Verify no stale implementation or documentation remains**

Run:

```powershell
rg -n "UserProfileUpdateRequest|update_profile\(|updateMe\(|PATCH.*auth/me|Update display name|update profile" app frontend/src tests README.md docs/SYSTEM_OVERVIEW.md
```

Expected: no output and exit code 1 from `rg`.

- [x] **Step 4: Run final verification**

Run:

```powershell
uv run pytest tests/test_api_routes.py tests/test_schemas.py tests/test_models.py -v
Push-Location frontend
npm run build
Pop-Location
git diff --check
git status --short
```

Expected: pytest passes, Vite build succeeds, `git diff --check` prints nothing, and status contains only intended changes plus the pre-existing `.codex_tmp/` and `bao_cao_UI/` untracked paths.

- [x] **Step 5: Commit documentation**

```powershell
git add -- README.md docs/SYSTEM_OVERVIEW.md app/router/v1/README.md app/schema/README.md app/service/README.md docs/superpowers/plans/2026-07-15-disable-display-name-editing.md
git commit -m "docs: remove display name update API"
```
