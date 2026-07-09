import { INTERVIEW_SESSIONS_PATH, interviewReportPath } from './paths';
import { apiJson } from './http';

/**
 * Create a new interview session.
 * Matches POST /api/v1/interview/sessions
 * @param {{ cv_id: string, mode?: string, focus_area?: string, duration_minutes?: number }} payload
 * @returns {Promise<object>} InterviewSessionResponse
 */
export function createSession(payload) {
    return apiJson(INTERVIEW_SESSIONS_PATH, {
        method: 'POST',
        body: payload,
    });
}

/**
 * Get the STAR-scored report for a completed interview session.
 * Matches GET /api/v1/interview/sessions/{session_id}/report
 * @param {string} sessionId
 * @returns {Promise<object>} InterviewReportResponse
 */
export function getReport(sessionId) {
    return apiJson(interviewReportPath(sessionId), { method: 'GET' });
}

/**
 * Get all interview sessions for the current user.
 * Matches GET /api/v1/interview/sessions
 * @returns {Promise<Array>} List of InterviewReportResponse
 */
export function getSessions() {
    return apiJson(INTERVIEW_SESSIONS_PATH, { method: 'GET' });
}

/**
 * Scrape and structure a job description from a URL.
 * Matches GET /api/v1/interview/scrape-jd?url={url}
 * @param {string} url
 * @returns {Promise<object>} `{ job_title, company, jd_text, focus_area }`
 */
export function scrapeJD(url) {
    const encoded = encodeURIComponent(url);
    return apiJson(`/api/v1/interview/scrape-jd?url=${encoded}`, { method: 'GET' });
}
