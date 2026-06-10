import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './store/ThemeContext';

// Public pages
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import AboutUsPage from './pages/AboutUsPage';

// Protected pages
import MainDashboard from './pages/MainDashboard';
import ProfilePage from './pages/ProfilePage';
import AccountSettingsPage from './pages/AccountSettingsPage';

import CVUploadPage from './pages/CVUploadPage';
import CVExtractionResultPage from './pages/CVExtractionResultPage';
import CVOptimizationPage from './pages/CVOptimizationPage';
import CVReviewPage from './pages/CVReviewPage';

import JobMatchingPage from './pages/JobMatchingPage';
import JobRecommendationsPage from './pages/JobRecommendationsPage';

import InterviewPage from './pages/InterviewPage';
import InterviewReportPage from './pages/InterviewReportPage';

import ChatPage from './pages/ChatPage';

// Auth guard
import AuthGuard from './components/Common/AuthGuard';

function App() {
    return (
        <Router>
            <ThemeProvider>
                <Routes>
                    {/* ── Public ── */}
                    <Route path="/" element={<LandingPage />} />
                    <Route path="/login" element={<AuthPage />} />
                    <Route path="/signup" element={<AuthPage />} />
                    <Route path="/about" element={<AboutUsPage />} />

                    {/* ── Protected ── */}
                    <Route element={<AuthGuard />}>
                        <Route path="/dashboard" element={<MainDashboard />} />
                        <Route path="/profile" element={<ProfilePage />} />
                        <Route path="/settings" element={<AccountSettingsPage />} />

                        {/* CV flow */}
                        <Route path="/cv-upload" element={<CVUploadPage />} />
                        <Route path="/cv-extraction-result" element={<CVExtractionResultPage />} />
                        <Route path="/cv-optimization" element={<CVOptimizationPage />} />
                        <Route path="/cv-review" element={<CVReviewPage />} />

                        {/* Job matching */}
                        <Route path="/job-matching" element={<JobMatchingPage />} />
                        <Route path="/job-recommendations" element={<JobRecommendationsPage />} />

                        {/* Interview */}
                        <Route path="/interview" element={<InterviewPage />} />
                        <Route path="/interview-report" element={<InterviewReportPage />} />

                        {/* Chat */}
                        <Route path="/chat" element={<ChatPage />} />
                    </Route>

                    {/* Fallback */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                </Routes>
            </ThemeProvider>
        </Router>
    );
}

export default App;