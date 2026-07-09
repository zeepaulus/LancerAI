import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import * as keys from '../../config/storageKeys';

const navSections = [
    {
        label: 'Tổng quan',
        items: [
            { label: 'Dashboard', path: '/dashboard', match: ['/dashboard'], icon: 'dashboard' },
        ],
    },
    {
        label: 'Chuẩn bị',
        items: [
            { label: 'Phân tích CV', path: '/cv-upload', match: ['/cv-upload', '/cv-extraction-result', '/cv-optimization', '/cv-review'], icon: 'cv' },
            { label: 'So khớp việc làm', path: '/job-matching', match: ['/job-matching', '/job-recommendations'], icon: 'match' },
        ],
    },
    {
        label: 'Luyện tập',
        items: [
            { label: 'Ngân hàng câu hỏi', path: '/question-bank', match: ['/question-bank'], icon: 'questions' },
            { label: 'Phỏng vấn giọng nói', path: '/interview', match: ['/interview', '/chat'], icon: 'interview' },
            { label: 'Lịch sử luyện tập', path: '/candidate', match: ['/candidate', '/profile'], icon: 'records' },
        ],
    },
    {
        label: 'Đánh giá',
        items: [
            { label: 'Báo cáo', path: '/reports', match: ['/reports', '/interview-report'], icon: 'reports' },
            { label: 'Cài đặt', path: '/settings', match: ['/settings'], icon: 'settings' },
        ],
    },
];

const iconPaths = {
    dashboard: (
        <>
            <path d="M4 6.5h5v5H4z" />
            <path d="M15 6.5h5v3h-5z" />
            <path d="M15 13h5v4.5h-5z" />
            <path d="M4 15h5v2.5H4z" />
        </>
    ),
    cv: (
        <>
            <path d="M7 4.5h7l4 4v11H7z" />
            <path d="M14 4.5v4h4" />
            <path d="M10 12h5.5" />
            <path d="M10 15h7" />
        </>
    ),
    match: (
        <>
            <path d="M5 7.5h5.5" />
            <path d="M5 16.5h5.5" />
            <path d="M13 6l6 6-6 6" />
            <path d="M18.5 12H5" />
        </>
    ),
    questions: (
        <>
            <path d="M5.5 5.5h13v10h-5l-3.5 3v-3H5.5z" />
            <path d="M9 9h6" />
            <path d="M9 12h4" />
        </>
    ),
    interview: (
        <>
            <path d="M12 4.5a3 3 0 0 1 3 3v4a3 3 0 0 1-6 0v-4a3 3 0 0 1 3-3z" />
            <path d="M6.5 11.5a5.5 5.5 0 0 0 11 0" />
            <path d="M12 17v3" />
        </>
    ),
    records: (
        <>
            <path d="M5.5 6.5h13" />
            <path d="M7 10.5h10" />
            <path d="M7 14.5h6" />
            <path d="M5.5 19h13" />
        </>
    ),
    reports: (
        <>
            <path d="M6 18V9" />
            <path d="M12 18V5" />
            <path d="M18 18v-6" />
            <path d="M4.5 18.5h15" />
        </>
    ),
    settings: (
        <>
            <path d="M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z" />
            <path d="M12 3.8v2" />
            <path d="M12 18.2v2" />
            <path d="M4.9 7.1l1.4 1.4" />
            <path d="M17.7 15.5l1.4 1.4" />
            <path d="M19.1 7.1l-1.4 1.4" />
            <path d="M6.3 15.5l-1.4 1.4" />
        </>
    ),
    expand: <path d="M9 6l6 6-6 6" />,
    collapse: <path d="M15 6l-6 6 6 6" />,
};

const NavGlyph = ({ type }) => (
    <svg aria-hidden="true" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
        {iconPaths[type]}
    </svg>
);

function isActive(pathname, item) {
    return item.match.some((path) => pathname === path || pathname.startsWith(`${path}/`));
}

function workspaceLabel(pathname) {
    const labels = {
        '/': 'Trang chủ',
        '/dashboard': 'Dashboard',
        '/candidate': 'Lịch sử luyện tập',
        '/profile': 'Hồ sơ',
        '/settings': 'Cài đặt',
        '/cv-upload': 'Phân tích CV',
        '/cv-extraction-result': 'Kết quả trích xuất CV',
        '/cv-optimization': 'Tối ưu CV',
        '/cv-review': 'Lịch sử CV',
        '/job-matching': 'So khớp việc làm',
        '/job-recommendations': 'Gợi ý việc làm',
        '/interview': 'Phỏng vấn giọng nói',
        '/interview-report': 'Báo cáo phỏng vấn',
        '/question-bank': 'Ngân hàng câu hỏi',
        '/reports': 'Báo cáo',
        '/chat': 'Phòng phỏng vấn',
        '/about': 'Giới thiệu',
    };
    return labels[pathname] || 'Dashboard';
}

const Navbar = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const [showDropdown, setShowDropdown] = useState(false);
    const [sidebarCollapsed, setSidebarCollapsed] = useState(() => {
        try {
            return localStorage.getItem('lancerai_sidebar_collapsed') === 'true';
        } catch {
            return false;
        }
    });
    const dropdownRef = useRef(null);
    const profile = JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');
    const displayName = profile.display_name || profile.email || 'Người dùng';
    const initials = displayName
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join('') || 'U';

    const handleLogout = () => {
        localStorage.removeItem(keys.LANCERAI_ACCESS_TOKEN);
        localStorage.removeItem(keys.LANCERAI_USER_PROFILE);
        localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
        navigate('/');
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setShowDropdown(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    useEffect(() => {
        try {
            localStorage.setItem('lancerai_sidebar_collapsed', String(sidebarCollapsed));
        } catch {
            // Ignore storage failures; the UI still works for the current session.
        }
    }, [sidebarCollapsed]);

    return (
        <div className={`lancer-nav-shell ${sidebarCollapsed ? 'is-collapsed' : ''}`}>
            <aside className="lancer-sidebar" aria-label="Primary navigation">
                <div className="lancer-sidebar-head">
                    <button className="lancer-brand" type="button" onClick={() => navigate('/dashboard')} title="Dashboard LancerAI">
                        <span className="lancer-brand-mark">L</span>
                        <span className="lancer-brand-name">
                            <strong>LancerAI</strong>
                            <span>Trợ lý nghề nghiệp</span>
                        </span>
                    </button>
                    <button
                        className="lancer-sidebar-toggle"
                        type="button"
                        onClick={() => setSidebarCollapsed((value) => !value)}
                        aria-label={sidebarCollapsed ? 'Mở rộng thanh điều hướng' : 'Thu gọn thanh điều hướng'}
                        title={sidebarCollapsed ? 'Mở rộng' : 'Thu gọn'}
                    >
                        <NavGlyph type={sidebarCollapsed ? 'expand' : 'collapse'} />
                    </button>
                </div>

                {navSections.map((section) => (
                    <div className="lancer-nav-section" key={section.label}>
                        <div className="lancer-nav-label">{section.label}</div>
                        {section.items.map((item) => (
                            <button
                                key={item.path}
                                type="button"
                                className={`lancer-nav-item ${isActive(location.pathname, item) ? 'is-active' : ''}`}
                                onClick={() => navigate(item.path)}
                                aria-label={item.label}
                                title={item.label}
                            >
                                <span className="lancer-nav-icon"><NavGlyph type={item.icon} /></span>
                                <span>{item.label}</span>
                            </button>
                        ))}
                    </div>
                ))}

                <div className="lancer-nav-spacer" />

                <div className="lancer-review-card">
                    <strong>Bước nên làm</strong>
                    <p>Tải CV, so khớp với JD, luyện phỏng vấn, rồi xem báo cáo để cải thiện.</p>
                </div>
            </aside>

            <header className="lancer-topbar">
                <div className="lancer-topbar-context" aria-label="Khu vực hiện tại">
                    <span className="page-kicker">Không gian làm việc</span>
                    <strong>{workspaceLabel(location.pathname)}</strong>
                </div>

                <div className="lancer-topbar-actions">
                    <button className="btn-outline" type="button" onClick={() => navigate('/cv-upload')}>
                        Tải CV
                    </button>
                    <button className="btn-primary" type="button" onClick={() => navigate('/interview')}>
                        Bắt đầu phỏng vấn
                    </button>

                    <div className="lancer-user-menu" ref={dropdownRef}>
                        <button className="lancer-avatar" type="button" onClick={() => setShowDropdown((value) => !value)}>
                            {initials}
                        </button>
                        {showDropdown && (
                            <div className="lancer-dropdown">
                                <button type="button" onClick={() => { navigate('/profile'); setShowDropdown(false); }}>
                                    Hồ sơ <span>Mở</span>
                                </button>
                                <button type="button" onClick={() => { navigate('/settings'); setShowDropdown(false); }}>
                                    Cài đặt <span>Mở</span>
                                </button>
                                <button type="button" onClick={() => { navigate('/about'); setShowDropdown(false); }}>
                                    Giới thiệu <span>Mở</span>
                                </button>
                                <button type="button" onClick={handleLogout} className="lancer-dropdown__danger">
                                    Đăng xuất
                                </button>
                            </div>
                        )}
                    </div>
                </div>
            </header>
        </div>
    );
};

export default Navbar;
