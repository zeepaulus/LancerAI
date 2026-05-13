import { JOB_MATCH_PATH } from './paths';
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
