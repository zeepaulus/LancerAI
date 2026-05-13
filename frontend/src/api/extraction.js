import { EXTRACTION_UPLOAD_PATH, extractionCvPath } from './paths';
import { API_BASE_URL } from '../config/env';
import * as keys from '../config/storageKeys';
import { apiJson } from './http';

/**
 * Upload a CV file (multipart/form-data).
 * Matches POST /api/v1/extraction/cvs
 * @param {File} file - PDF, PNG, JPEG, or WebP
 * @returns {Promise<object>} CVExtractionResponse
 */
export async function uploadCV(file) {
    const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
    const formData = new FormData();
    formData.append('file', file);

    const url = `${API_BASE_URL}${EXTRACTION_UPLOAD_PATH}`;
    const res = await fetch(url, {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
    });

    if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        const err = new Error(payload.detail || 'Upload failed.');
        err.status = res.status;
        throw err;
    }

    return res.json();
}

/**
 * Fetch a previously uploaded CV by id.
 * Matches GET /api/v1/extraction/cv/{cv_id}
 * @param {string} cvId
 * @returns {Promise<object>} CVExtractionResponse
 */
export function getCV(cvId) {
    return apiJson(extractionCvPath(cvId), { method: 'GET' });
}
