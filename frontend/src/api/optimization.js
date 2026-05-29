import { optimizationAnalyzePath, optimizationRenderPath, optimizationPdfPath } from './paths';
import { apiJson } from './http';
import { API_BASE_URL } from '../config/env';
import * as keys from '../config/storageKeys';

/**
 * Run the CV optimization pipeline.
 * Matches POST /api/v1/optimization/cvs/{cv_id}/optimizations
 * @param {string} cvId
 * @param {{ target_job_title?: string, target_industry?: string, mode?: string }} opts
 * @returns {Promise<object>} CVOptimizationResponse
 */
export function optimizeCV(cvId, opts = {}) {
    return apiJson(optimizationAnalyzePath(cvId), {
        method: 'POST',
        body: { ...opts },
    });
}

/**
 * Render the optimized CV into a named template (returns JSON).
 * Matches POST /api/v1/optimization/cvs/{cv_id}/render
 * @param {string} cvId
 * @param {string} template - e.g. 'harvard', 'stanford', 'modern'
 * @returns {Promise<object>} RenderedCVResponse
 */
export function renderCV(cvId, template = 'harvard') {
    return apiJson(optimizationRenderPath(cvId), {
        method: 'POST',
        body: { template },
    });
}

/**
 * Download the optimized CV as PDF.
 * Matches GET /api/v1/optimization/cvs/{cv_id}/pdf?template=...
 * @param {string} cvId
 * @param {string} template
 * @returns {Promise<Blob>} PDF file blob
 */
export async function downloadPDF(cvId, template = 'harvard') {
    const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
    const url = `${API_BASE_URL}${optimizationPdfPath(cvId, template)}`;
    const res = await fetch(url, {
        method: 'GET',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
    if (!res.ok) {
        const payload = await res.json().catch(() => ({}));
        throw new Error(payload.detail || 'PDF download failed.');
    }
    return res.blob();
}
