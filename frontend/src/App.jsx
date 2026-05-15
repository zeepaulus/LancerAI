import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './store/ThemeContext';

import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import MainDashboard from './pages/MainDashboard';
import ProfilePage from './pages/ProfilePage';
import AccountSettingsPage from './pages/AccountSettingsPage';
import AboutUsPage from './pages/AboutUsPage';
import InterviewPage from './pages/InterviewPage';
import ChatPage from './pages/ChatPage';
import CVReviewPage from './pages/CVReviewPage';

import CVUploadPage from './pages/CVUploadPage';

function App() {
  return (
    <Router>
      {/* Bọc ThemeProvider quanh Routes để cung cấp state cho toàn bộ trang */}
      <ThemeProvider>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<AuthPage />} />
          <Route path="/signup" element={<AuthPage />} />
          <Route path="/dashboard" element={<MainDashboard />} />
          
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/settings" element={<AccountSettingsPage />} />
          <Route path="/about" element={<AboutUsPage />} />
        
          <Route path="/interview" element={<InterviewPage />} />
          <Route path="/cv-review" element={<CVReviewPage />} />
          <Route path="/chat" element={<ChatPage />} />
        
          <Route path="/cv-upload" element={<CVUploadPage />} />
        </Routes>
      </ThemeProvider>
    </Router>
  );
}
export default App;