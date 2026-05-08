import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

import logoImg from '../../assets/Logo/lancerai_logo.png'

const Navbar = () => {
    const navigate = useNavigate();
    const [showDropdown, setShowDropdown] = useState(false);
    const [isDarkMode, setIsDarkMode] = useState(false);

    const handleLogout = () => {
        localStorage.removeItem('mockUserDB');
        navigate('/');
    };

    const toggleDarkMode = (e) => {
        e.stopPropagation(); // Ngăn dropdown bị đóng khi bấm công tắc
        setIsDarkMode(!isDarkMode);
        // Tương lai: Thêm logic đổi màu toàn website ở đây
    };

    const styles = {
        nav: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 30px', background: isDarkMode ? '#1a202c' : '#fff', borderBottom: '1px solid #e2e8f0', color: isDarkMode ? '#fff' : '#000' },
        logoWrapper: {
            display: 'flex',
            alignItems: 'center',
            cursor: 'pointer',
            gap: '10px' // Khoảng cách nếu bạn muốn để cả Logo và Tên thương hiệu
        },
        logoIcon: {
            height: '35px', // Cố định chiều cao để không làm vỡ thanh Navbar
            width: 'auto',   // Tự động điều chỉnh chiều rộng theo tỉ lệ ảnh
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
            overflow: 'hidden', // Quan trọng: để ảnh không tràn ra ngoài vòng tròn
            border: '2px solid #e2e8f0',
            cursor: 'pointer',
            padding: 0
        },
        avatarImg: {
            width: '100%',
            height: '100%',
            objectFit: 'cover' // Giúp ảnh không bị méo khi kích thước khác nhau
        },
        btnGroup: { display: 'flex', gap: '20px', alignItems: 'center' },
        navBtn: { background: 'none', border: 'none', fontSize: '16px', fontWeight: '500', cursor: 'pointer', color: isDarkMode ? '#cbd5e0' : '#4a5568' },
        avatar: { width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#cbd5e0', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', border: 'none', fontSize: '20px' },
        dropdown: { position: 'absolute', right: '30px', top: '70px', background: isDarkMode ? '#2d3748' : 'white', border: '1px solid #e2e8f0', borderRadius: '8px', width: '220px', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', overflow: 'hidden', zIndex: 100 },
        dropItem: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', padding: '12px 20px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', color: isDarkMode ? '#fff' : '#4a5568', fontSize: '15px', borderBottom: '1px solid #edf2f7' },
        // CSS cho công tắc Toggle
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
                <button style={styles.navBtn}>Phỏng vấn</button>
                <button style={styles.navBtn}>Đánh giá CV</button>
                
                <div>
                    <button style={styles.avatar} onClick={() => setShowDropdown(!showDropdown)}>👤</button>
                    
                    {showDropdown && (
                        <div style={styles.dropdown}>
                            <button style={styles.dropItem} onClick={() => {navigate('/profile'); setShowDropdown(false);}}>Profile của tôi</button>
                            <button style={styles.dropItem} onClick={() => {navigate('/settings'); setShowDropdown(false);}}>Quản lý tài khoản</button>
                            
                            {/* Nút Chế độ tối có công tắc */}
                            <button style={styles.dropItem} onClick={toggleDarkMode}>
                                Chế độ tối
                                <div style={styles.switchBg}>
                                    <div style={styles.switchDot}></div>
                                </div>
                            </button>

                            <button style={styles.dropItem} onClick={() => {navigate('/about'); setShowDropdown(false);}}>Về chúng tôi</button>
                            <button style={{...styles.dropItem, color: '#e53e3e', borderBottom: 'none'}} onClick={handleLogout}>Đăng xuất</button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

export default Navbar;