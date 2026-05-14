import { API_BASE_URL } from '../config/env';
import * as keys from '../config/storageKeys';

/**
 * Chuẩn hóa thông báo lỗi FastAPI ({ detail: string | object }).
 */
export function detailToMessage(detail) {
    if (detail === undefined || detail === null) return 'Lỗi không xác định.';
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
        const parts = detail.map((e) =>
            typeof e?.msg === 'string' ? e.msg : JSON.stringify(e)
        );
        return parts.join(' · ');
    }
    if (typeof detail === 'object' && typeof detail.detail === 'string') {
        return detail.detail;
    }
    try {
        return JSON.stringify(detail);
    } catch {
        return 'Lỗi server.';
    }
}

function readJsonSafe(text) {
    if (!text || !text.trim()) return null;
    try {
        return JSON.parse(text);
    } catch {
        return { detail: text };
    }
}

/**
 * POST/GET JSON đến backend. Mặc định gắn Bearer từ localStorage (trừ khi skipAuth).
 */
export async function apiJson(path, { method = 'GET', body, headers = {}, skipAuth } = {}) {
    const token =
        typeof skipAuth === 'boolean' && skipAuth ? null : localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);

    const h = new Headers(headers);
    if (body !== undefined && !h.has('Content-Type')) {
        h.set('Content-Type', 'application/json');
    }
    if (token) {
        h.set('Authorization', `Bearer ${token}`);
    }

    const url = `${API_BASE_URL}${path.startsWith('/') ? path : `/${path}`}`;
    const controller = new AbortController();
    const timeoutMs = 60_000;
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    let res;
    try {
        res = await fetch(url, {
            method,
            headers: h,
            body: body !== undefined ? JSON.stringify(body) : undefined,
            signal: controller.signal,
        });
    } finally {
        clearTimeout(timeoutId);
    }

    const payload = readJsonSafe(await res.text());

    if (!res.ok) {
        const msg = payload && typeof payload === 'object' ? detailToMessage(payload.detail) : 'Yêu cầu thất bại.';
        const err = new Error(msg);
        err.status = res.status;
        err.payload = payload;
        throw err;
    }

    return payload;
}
