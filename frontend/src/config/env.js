/**
 * Backend origin for REST calls.
 * - Local dev: defaults to 'http://127.0.0.1:8000'
 * - Production (Nginx proxy): defaults to '' so /api/... calls are same-origin.
 * Override with `VITE_API_BASE_URL` in `frontend/.env`.
 */
function resolveApiBaseUrl() {
    const raw = import.meta.env.VITE_API_BASE_URL;
    // Explicitly set to empty string -> same-origin proxy mode.
    if (typeof raw === 'string') {
        return raw.replace(/\/+$/, '');
    }
    if (import.meta.env.PROD) {
        return '';
    }
    // Undefined local dev without .env -> local FastAPI backend.
    return 'http://127.0.0.1:8000';
}

export const API_BASE_URL = resolveApiBaseUrl();
