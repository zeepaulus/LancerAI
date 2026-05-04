import React from 'react';
import Navbar from '../components/Layout/Navbar';

const MainDashboard = () => {
    return (
        <div>
            <Navbar />
            <div style={{ padding: '20px' }}>
                <h2>Chào mừng bạn đến với Hệ thống phân tích CV</h2>
                <p>Tính năng tải file và phỏng vấn sẽ được hiển thị ở đây...</p>
            </div>
        </div>
    );
};

export default MainDashboard;