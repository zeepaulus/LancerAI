import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import LandingPage from './pages/LandingPage';
import AuthPage from './pages/AuthPage';
import MainDashboard from './pages/MainDashboard';
// Import các trang mới
import ProfilePage from './pages/ProfilePage';
import AccountSettingsPage from './pages/AccountSettingsPage';
import AboutUsPage from './pages/AboutUsPage';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/signup" element={<AuthPage />} />
        <Route path="/dashboard" element={<MainDashboard />} />
        
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/settings" element={<AccountSettingsPage />} />
        <Route path="/about" element={<AboutUsPage />} />
      </Routes>
    </Router>
  );
}

export default App;