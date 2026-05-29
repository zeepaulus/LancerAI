/**
 * Stable paths — must mirror FastAPI `app.include_router(..., prefix="/api/v1")`
 * và prefix router (ví dụ auth: `/auth`).
 */

// Auth
export const AUTH_SIGNUP_PATH = '/api/v1/auth/signup';
export const AUTH_LOGIN_PATH = '/api/v1/auth/login';
export const AUTH_ME_PATH = '/api/v1/auth/me';

// Extraction
export const EXTRACTION_UPLOAD_PATH = '/api/v1/extraction/cvs';
export const extractionCvPath = (cvId) => `/api/v1/extraction/cv/${cvId}`;

// Optimization
export const optimizationAnalyzePath = (cvId) => `/api/v1/optimization/cvs/${cvId}/optimizations`;
export const optimizationRenderPath = (cvId) => `/api/v1/optimization/cvs/${cvId}/render`;
export const optimizationPdfPath = (cvId, template = 'harvard') =>
    `/api/v1/optimization/cvs/${cvId}/pdf?template=${encodeURIComponent(template)}`;

// Job matching
export const JOB_MATCH_PATH = '/api/v1/jobs/matches';
export const jobRecommendationsPath = (cvId, limit = 10) =>
    `/api/v1/jobs/recommendations/${cvId}?limit=${limit}`;

// Interview
export const INTERVIEW_SESSIONS_PATH = '/api/v1/interview/sessions';
export const interviewReportPath = (sessionId) => `/api/v1/interview/sessions/${sessionId}/report`;

// Interview WebSocket
export const INTERVIEW_WS_PATH = '/api/v1/interview/ws';
