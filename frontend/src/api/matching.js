import { JOB_MATCH_PATH, jobRecommendationsPath } from './paths';
import { apiJson } from './http';

/**
 * Match a CV against a Job Description.
 * Matches POST /api/v1/jobs/matches
 * @param {{ cv_id: string, jd_url?: string, jd_text?: string }} payload
 * @returns {Promise<object>} JobMatchResponse
 */
export function matchCV(payload) {
    return apiJson(JOB_MATCH_PATH, {
        method: 'POST',
        body: payload,
    });
}

/**
 * Get ranked job recommendations based on CV.
 * Matches GET /api/v1/jobs/recommendations/{cv_id}?limit=...
 * @param {string} cvId
 * @param {number} limit
 * @returns {Promise<object[]>} JobRecommendationResponse[]
 */
export function getRecommendations(cvId, limit = 10) {
    return apiJson(jobRecommendationsPath(cvId, limit), { method: 'GET' });
}
