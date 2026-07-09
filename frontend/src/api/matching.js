import { JOB_LISTINGS_PATH, JOB_MATCH_PATH, jobListingPath, jobRecommendationsPath } from './paths';
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

export function getJobListings(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null && value !== '') query.set(key, value);
    });
    const suffix = query.toString() ? `?${query.toString()}` : '';
    return apiJson(`${JOB_LISTINGS_PATH}${suffix}`, { method: 'GET' });
}

export function getJobListing(jobId) {
    return apiJson(jobListingPath(jobId), { method: 'GET' });
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
