import React from 'react';
import { BrowserRouter as Router, Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { ThemeProvider } from './store/ThemeContext';

import AuthGuard from './components/Common/AuthGuard';
import AboutUsPage from './pages/AboutUsPage';
import AccountSettingsPage from './pages/AccountSettingsPage';
import AuthPage from './pages/AuthPage';
import CandidatePage from './pages/CandidatePage';
import ChatPage from './pages/ChatPage';
import CVExtractionResultPage from './pages/CVExtractionResultPage';
import CVOptimizationPage from './pages/CVOptimizationPage';
import CVReviewPage from './pages/CVReviewPage';
import CVUploadPage from './pages/CVUploadPage';
import InterviewPage from './pages/InterviewPage';
import InterviewReportPage from './pages/InterviewReportPage';
import JobMatchingPage from './pages/JobMatchingPage';
import JobRecommendationsPage from './pages/JobRecommendationsPage';
import LandingPage from './pages/LandingPage';
import MainDashboard from './pages/MainDashboard';
import ProfilePage from './pages/ProfilePage';
import QuestionBankPage from './pages/QuestionBankPage';
import ReportsPage from './pages/ReportsPage';

function App() {
    return (
        <Router>
            <ThemeProvider>
                <AnimatedRoutes />
            </ThemeProvider>
        </Router>
    );
}

function AnimatedRoutes() {
    const location = useLocation();

    return (
        <div key={location.pathname} className="route-transition-shell">
            <Routes location={location}>
                <Route path="/" element={<LandingPage />} />
                <Route path="/login" element={<AuthPage />} />
                <Route path="/signup" element={<AuthPage />} />
                <Route path="/about" element={<AboutUsPage />} />

                <Route element={<AuthGuard />}>
                    <Route path="/dashboard" element={<MainDashboard />} />
                    <Route path="/candidate" element={<CandidatePage />} />
                    <Route path="/profile" element={<ProfilePage />} />
                    <Route path="/settings" element={<AccountSettingsPage />} />
                    <Route path="/cv-upload" element={<CVUploadPage />} />
                    <Route path="/cv-extraction-result" element={<CVExtractionResultPage />} />
                    <Route path="/cv-optimization" element={<CVOptimizationPage />} />
                    <Route path="/cv-review" element={<CVReviewPage />} />
                    <Route path="/job-matching" element={<JobMatchingPage />} />
                    <Route path="/job-recommendations" element={<JobRecommendationsPage />} />
                    <Route path="/interview" element={<InterviewPage />} />
                    <Route path="/interview-report" element={<InterviewReportPage />} />
                    <Route path="/question-bank" element={<QuestionBankPage />} />
                    <Route path="/reports" element={<ReportsPage />} />
                    <Route path="/chat" element={<ChatPage />} />
                </Route>

                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </div>
    );
}

export default App;
