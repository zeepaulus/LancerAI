import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '../../store/ThemeContext';

import * as keys from '../../config/storageKeys';
import logoImg from '../../assets/Logo/lancerai_logo.png'

const Navbar = () => {
    const navigate = useNavigate();
    const [showDropdown, setShowDropdown] = useState(false);
    const { isDarkMode, toggleDarkMode } = useTheme();
    const dropdownRef = useRef(null);

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

    // Close dropdown on outside click
    useEffect(() => {
        const handleClickOutside = (e) => {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <nav style={styles.nav}>
            <div style={styles.logoWrapper} onClick={() => navigate('/dashboard')}>
                <img src={logoImg} alt="LancerAI Logo" style={styles.logoIcon} />
                <span style={styles.logoText}>LANCER AI</span>
            </div>

            <div style={styles.btnGroup}>
                <button
                    type="button"
                    style={styles.navBtn}
                    onClick={() => navigate('/interview')}
                    onMouseEnter={(e) => e.target.style.color = 'var(--ink)'}
                    onMouseLeave={(e) => e.target.style.color = 'var(--muted)'}
                >
                    Phỏng vấn
                </button>
                <button
                    type="button"
                    style={styles.navBtn}
                    onClick={() => navigate('/cv-upload')}
                    onMouseEnter={(e) => e.target.style.color = 'var(--ink)'}
                    onMouseLeave={(e) => e.target.style.color = 'var(--muted)'}
                >
                    Đánh giá CV
                </button>
                
                <div ref={dropdownRef} style={{ position: 'relative' }}>
                    <button
                        type="button"
                        style={styles.avatarBtn}
                        onClick={() => setShowDropdown(!showDropdown)}
                    >
                        👤
                    </button>
                    
                    {showDropdown && (
                        <div style={styles.dropdown}>
                            <button type="button" style={styles.dropItem} onClick={() => { navigate('/profile'); setShowDropdown(false); }}>
                                <span>Profile của tôi</span>
                                <span style={styles.dropIcon}>→</span>
                            </button>
                            <button type="button" style={styles.dropItem} onClick={() => { navigate('/settings'); setShowDropdown(false); }}>
                                <span>Quản lý tài khoản</span>
                                <span style={styles.dropIcon}>→</span>
                            </button>
                            
                            <button type="button" style={styles.dropItem} onClick={handleToggleDarkMode}>
                                <span>Chế độ tối</span>
                                <div style={styles.switchBg(isDarkMode)}>
                                    <div style={styles.switchDot(isDarkMode)}></div>
                                </div>
                            </button>

                            <button type="button" style={styles.dropItem} onClick={() => { navigate('/about'); setShowDropdown(false); }}>
                                <span>Về chúng tôi</span>
                                <span style={styles.dropIcon}>→</span>
                            </button>

                            <div style={styles.dropDivider}></div>

                            <button type="button" style={{...styles.dropItem, color: 'var(--semantic-error)'}} onClick={handleLogout}>
                                <span>Đăng xuất</span>
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </nav>
    );
};

const styles = {
    nav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 var(--sp-xl)',
        height: 'var(--nav-height)',
        backgroundColor: 'var(--canvas)',
        borderBottom: '1px solid var(--hairline)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backdropFilter: 'blur(8px)',
        transition: 'background-color var(--transition-base)',
    },
    logoWrapper: {
        display: 'flex',
        alignItems: 'center',
        cursor: 'pointer',
        gap: 'var(--sp-sm)',
    },
    logoIcon: {
        height: '32px',
        width: 'auto',
        objectFit: 'contain',
    },
    logoText: {
        fontFamily: 'var(--font-body)',
        fontWeight: 600,
        fontSize: '15px',
        color: 'var(--ink)',
        letterSpacing: '1.5px',
    },
    btnGroup: {
        display: 'flex',
        gap: 'var(--sp-lg)',
        alignItems: 'center',
    },
    navBtn: {
        background: 'none',
        border: 'none',
        fontFamily: 'var(--font-body)',
        fontSize: '15px',
        fontWeight: 500,
        lineHeight: 1.4,
        cursor: 'pointer',
        color: 'var(--muted)',
        transition: 'color var(--transition-fast)',
        padding: 'var(--sp-xs) var(--sp-sm)',
    },
    avatarBtn: {
        width: '36px',
        height: '36px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        border: '1px solid var(--hairline)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        fontSize: '16px',
        transition: 'border-color var(--transition-fast)',
    },
    dropdown: {
        position: 'absolute',
        right: 0,
        top: 'calc(100% + var(--sp-xs))',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-xl)',
        width: '240px',
        boxShadow: 'var(--shadow-dropdown)',
        overflow: 'hidden',
        zIndex: 100,
        padding: 'var(--sp-xs) 0',
    },
    dropItem: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        width: '100%',
        padding: 'var(--sp-sm) var(--sp-base)',
        background: 'none',
        border: 'none',
        textAlign: 'left',
        cursor: 'pointer',
        color: 'var(--body)',
        fontFamily: 'var(--font-body)',
        fontSize: '14px',
        fontWeight: 400,
        lineHeight: 1.5,
        transition: 'background-color var(--transition-fast)',
    },
    dropIcon: {
        color: 'var(--muted-soft)',
        fontSize: '12px',
    },
    dropDivider: {
        height: '1px',
        backgroundColor: 'var(--hairline)',
        margin: 'var(--sp-xs) 0',
    },
    switchBg: (isDark) => ({
        width: '36px',
        height: '20px',
        borderRadius: 'var(--rounded-pill)',
        backgroundColor: isDark ? 'var(--ink)' : 'var(--hairline-strong)',
        position: 'relative',
        transition: 'background-color var(--transition-base)',
        flexShrink: 0,
    }),
    switchDot: (isDark) => ({
        width: '16px',
        height: '16px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: isDark ? 'var(--canvas)' : '#ffffff',
        position: 'absolute',
        top: '2px',
        left: isDark ? '18px' : '2px',
        transition: 'left var(--transition-base)',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    }),
};

export default Navbar;
