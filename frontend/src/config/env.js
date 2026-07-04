/**
 * Backend origin for REST calls.
 * - Local dev: defaults to 'http://127.0.0.1:8000'
 * - Production (Nginx proxy): set VITE_API_BASE_URL="" at build time
 *   → returns '' so all /api/... calls are relative and proxied by Nginx.
 * Override with `VITE_API_BASE_URL` in `frontend/.env`.
 */
function resolveApiBaseUrl() {
    const raw = import.meta.env.VITE_API_BASE_URL;
    // Explicitly set to empty string → production mode: use relative URLs
    if (typeof raw === 'string') {
        return raw.replace(/\/+$/, '');
    }
    // Undefined (local dev without .env) → localhost backend
    return 'http://127.0.0.1:8000';
}

export const API_BASE_URL = resolveApiBaseUrl();

