import { AUTH_LOGIN_PATH, AUTH_ME_PATH, AUTH_PASSWORD_PATH, AUTH_SIGNUP_PATH } from './paths';
import { apiJson } from './http';

/**
 * Create a new account.
 * Matches POST /api/v1/auth/signup → UserProfileResponse.
 *
 * NOTE: `tenant_id` is intentionally omitted — the server always sets
 * tenant_id = user_id and ignores any client-supplied value (MVP policy).
 *
 * @param {{ email: string, password: string, display_name: string }} param0
 * @returns {Promise<object>} UserProfileResponse
 */
export function signup({ email, password, display_name }) {
    return apiJson(AUTH_SIGNUP_PATH, {
        method: 'POST',
        body: { email, password, display_name },
        skipAuth: true,
    });
}

/** Payload khớp `AuthLoginRequest`: identifier, password */
export function login({ identifier, password }) {
    return apiJson(AUTH_LOGIN_PATH, { method: 'POST', body: { identifier, password }, skipAuth: true });
}

/** GET `/api/v1/auth/me` — Bearer token required from localStorage */
export function me() {
    return apiJson(AUTH_ME_PATH, { method: 'GET' });
}

export function changePassword({ current_password, new_password }) {
    return apiJson(AUTH_PASSWORD_PATH, {
        method: 'PUT',
        body: { current_password, new_password },
    });
}
