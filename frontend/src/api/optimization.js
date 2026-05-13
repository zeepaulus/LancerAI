import { optimizationAnalyzePath, optimizationRenderPath } from './paths';
import { apiJson } from './http';

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
