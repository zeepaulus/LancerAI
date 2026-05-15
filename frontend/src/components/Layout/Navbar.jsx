import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../../store/ThemeContext';

import * as keys from '../../config/storageKeys';
import logoImg from '../../assets/Logo/lancerai_logo.png'

const Navbar = () => {
    const navigate = useNavigate();
    const [showDropdown, setShowDropdown] = useState(false);
    const { isDarkMode, toggleDarkMode } = useTheme();

    const handleLogout = () => {
        localStorage.removeItem(keys.LANCERAI_ACCESS_TOKEN);
        localStorage.removeItem(keys.LANCERAI_USER_PROFILE);
        localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
        navigate('/');
    };

    const handleToggleDarkMode = (e) => {
        e.stopPropagation(); // Ngăn dropdown bị đóng khi bấm công tắc
        toggleDarkMode();    // Gọi hàm đổi theme từ ThemeContext
    };

    const styles = {
        nav: { 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center', 
            padding: '15px 30px', 
            background: isDarkMode ? '#1a202c' : '#fff', 
            borderBottom: '1px solid #e2e8f0', 
            color: isDarkMode ? '#fff' : '#000' },
        logoWrapper: {
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            gap: '10px'
        },
        logoIcon: {
            height: '35px',
            width: 'auto',
            objectFit: 'contain' 
        },
        logoText: {
            fontWeight: 'bold',
            fontSize: '18px',
            color: '#3182ce',
            letterSpacing: '1px'
        },
        avatarBtn: { 
            width: '40px', 
            height: '40px', 
            borderRadius: '50%', 
            overflow: 'hidden',
            border: '2px solid #e2e8f0',
            cursor: 'pointer',
            padding: 0
        },
        avatarImg: {
            width: '100%',
            height: '100%',
            objectFit: 'cover'
        },
        btnGroup: { display: 'flex', gap: '20px', alignItems: 'center' },
        navBtn: { background: 'none', border: 'none', fontSize: '16px', fontWeight: '500', cursor: 'pointer', color: isDarkMode ? '#cbd5e0' : '#4a5568' },
        avatar: { width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#cbd5e0', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', border: 'none', fontSize: '20px' },
        dropdown: { position: 'absolute', right: '30px', top: '70px', background: isDarkMode ? '#2d3748' : 'white', border: '1px solid #e2e8f0', borderRadius: '8px', width: '220px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', overflow: 'hidden', zIndex: 100 },
        dropItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', padding: '12px 20px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', color: isDarkMode ? '#fff' : '#4a5568', fontSize: '15px', borderBottom: '1px solid #edf2f7' },
        switchBg: { width: '40px', height: '22px', borderRadius: '11px', background: isDarkMode ? '#3182ce' : '#cbd5e0', position: 'relative', transition: '0.3s' },
        switchDot: { width: '18px', height: '18px', borderRadius: '50%', background: 'white', position: 'absolute', top: '2px', left: isDarkMode ? '20px' : '2px', transition: '0.3s' }
        
    };

    return (
        <nav style={styles.nav}>
            <div style={styles.logoWrapper} onClick={() => navigate('/dashboard')}>
                <img src={logoImg} alt="AI Mock Interview Logo" style={styles.logoIcon} />
                <span style={styles.logoText}>LANCER AI</span>
            </div>
            <div style={styles.btnGroup}>
                <button type="button" style={styles.navBtn} onClick={() => navigate('/interview')}>Phỏng vấn</button>
                <button type="button" style={styles.navBtn} onClick={() => navigate('/cv-upload')}>Đánh giá CV</button>
                
                <div>
                    <button type="button" style={styles.avatar} onClick={() => setShowDropdown(!showDropdown)}>👤</button>
                    
                    {showDropdown && (
                        <div style={styles.dropdown}>
                            <button type="button" style={styles.dropItem} onClick={() => { navigate('/profile'); setShowDropdown(false); }}>Profile của tôi</button>
                            <button type="button" style={styles.dropItem} onClick={() => { navigate('/settings'); setShowDropdown(false); }}>Quản lý tài khoản</button>
                            
                            <button type="button" style={styles.dropItem} onClick={handleToggleDarkMode}>
                                Chế độ tối
                                <div style={styles.switchBg}>
                                    <div style={styles.switchDot}></div>
                                </div>
                            </button>

                            <button type="button" style={styles.dropItem} onClick={() => { navigate('/about'); setShowDropdown(false); }}>Về chúng tôi</button>
                            <button type="button" style={{ ...styles.dropItem, color: '#e53e3e', borderBottom: 'none' }} onClick={handleLogout}>Đăng xuất</button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
