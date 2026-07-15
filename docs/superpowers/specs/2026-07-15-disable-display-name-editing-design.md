# Disable Display Name Editing

## Goal

Make a user's display name immutable after account registration. Users can still view their display name in account settings, but neither the web interface nor the authenticated API may change it.

## Scope

- Keep `display_name` required during registration.
- Keep display-name login behavior unchanged.
- Keep `GET /api/v1/auth/me` unchanged.
- Keep password changes unchanged.
- Remove the authenticated `PATCH /api/v1/auth/me` profile-update capability.
- Remove the account-settings controls and client code that submit display-name changes.
- Do not modify existing users or database data.

## Backend Design

Remove the `PATCH /auth/me` route from the auth router. Consequently, a direct `PATCH` request to `/api/v1/auth/me` will be rejected by FastAPI with `405 Method Not Allowed`; the auth service update method will no longer be reachable through the API.

Remove the now-unused profile-update request schema and profile-update service method; repository search confirms the removed route is their only caller. Update API documentation so it no longer advertises display-name updates.

## Frontend Design

Account settings will continue loading the current profile through `GET /auth/me`. The display name will be rendered as a disabled or read-only field with explanatory text stating that it cannot be changed after registration.

Remove the display-name form submission handler, editable state, save state, success message, and “Lưu hồ sơ” button. Remove the unused `updateMe` API client function. Password-changing behavior remains intact.

## Error Handling

No new application error contract is introduced. Attempts to call the removed method receive the framework-standard `405 Method Not Allowed` response. Existing authentication and password errors remain unchanged.

## Testing

- Add or update a backend route test proving `PATCH /api/v1/auth/me` returns HTTP 405 and does not mutate the user.
- Because the frontend currently has no test runner, verify the rendered source contract with focused source assertions and run the production frontend build. The display-name control must be non-editable and no profile-save control may exist.
- Run the focused auth/schema/API tests and the relevant frontend checks.
- Run the broader available test suites in proportion to execution time and report any unrelated failures separately.

## Acceptance Criteria

1. Display name can still be supplied during signup and used during login.
2. Account settings displays the current display name but offers no way to edit or save it.
3. `PATCH /api/v1/auth/me` returns HTTP 405.
4. Password changes and `GET /api/v1/auth/me` still work.
5. No documentation or active client code claims that display names can be updated.
