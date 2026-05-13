/**
 * Backend origin for REST calls.
 * Override with `VITE_API_BASE_URL` in `frontend/.env` (see `frontend/.env.example`).
 */
function resolveApiBaseUrl() {
    const raw = import.meta.env.VITE_API_BASE_URL;
    if (typeof raw === 'string' && raw.trim() !== '') {
        return raw.replace(/\/+$/, '');
    }
    return 'http://127.0.0.1:8000';
}

export const API_BASE_URL = resolveApiBaseUrl();
