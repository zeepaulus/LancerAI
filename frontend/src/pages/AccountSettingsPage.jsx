import React, { useState, useEffect } from 'react';
import Navbar from '../components/Layout/Navbar';

const AccountSettingsPage = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [showPassword, setShowPassword] = useState(false);
    
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [countdown, setCountdown] = useState(5);

    useEffect(() => {
        let timer;
        if (showDeleteModal && countdown > 0) {
            timer = setInterval(() => setCountdown(c => c - 1), 1000);
        }
        return () => clearInterval(timer);
    }, [showDeleteModal, countdown]);

    const tabs = [
        { key: 'overview', label: 'Tổng quan' },
        { key: 'contact', label: 'Thông tin liên lạc' },
        { key: 'security', label: 'Tài khoản & Bảo mật' },
    ];

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <h2 className="display-sm" style={{marginBottom: 'var(--sp-xl)'}}>Quản lý tài khoản</h2>

                {/* Tabs */}
                <div style={styles.tabHeader}>
                    {tabs.map(tab => (
                        <button
                            key={tab.key}
                            style={{
                                ...styles.tabBtn,
                                color: activeTab === tab.key ? 'var(--ink)' : 'var(--muted)',
                                borderBottom: activeTab === tab.key ? '2px solid var(--ink)' : '2px solid transparent',
                                fontWeight: activeTab === tab.key ? 500 : 400,
                            }}
                            onClick={() => setActiveTab(tab.key)}
                        >
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* TAB 1: TỔNG QUAN */}
                {activeTab === 'overview' && (
                    <div>
                        <div style={styles.avatarRow}>
                            <div style={styles.avatarCircle}></div>
                            <div>
                                <button className="btn-outline" style={{fontSize: '13px', padding: '6px 14px', height: '32px'}}>Upload avatar</button>
                                <p style={{fontSize: '12px', color: 'var(--muted-soft)', marginTop: 'var(--sp-xxs)'}}>Max size: 2MB. Formats: JPG, PNG.</p>
                            </div>
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Tên người dùng <span style={styles.req}>*</span></label>
                            <input className="text-input" />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Họ và tên <span style={styles.req}>*</span></label>
                            <input className="text-input" />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Tiểu sử</label>
                            <textarea className="text-input" style={{height: '80px'}} />
                        </div>
                        <div style={styles.formGroup}>
                            <label style={styles.label}>Địa chỉ email <span style={styles.req}>*</span></label>
                            <input className="text-input" type="email" />
                        </div>
                        <button className="btn-primary">Lưu thay đổi</button>
                    </div>
                )}

                {/* TAB 2: LIÊN LẠC */}
                {activeTab === 'contact' && (
                    <div>
                        {['Nơi làm việc hiện tại', 'Số điện thoại', 'Tên Github', 'Tên Linkedin'].map(label => (
                            <div style={styles.formGroup} key={label}>
                                <label style={styles.label}>{label}</label>
                                <input className="text-input" />
                            </div>
                        ))}
                        <button className="btn-primary">Lưu thay đổi</button>
                    </div>
                )}

                {/* TAB 3: BẢO MẬT */}
                {activeTab === 'security' && (
                    <div>
                        <h3 className="title-sm" style={{marginBottom: 'var(--sp-base)'}}>Thay đổi mật khẩu</h3>
                        {['Mật khẩu hiện tại', 'Mật khẩu mới', 'Xác nhận mật khẩu mới'].map((label, i) => (
                            <div style={styles.formGroup} key={i}>
                                <label style={styles.label}>{label}</label>
                                <div style={styles.pwdWrapper}>
                                    <input className="text-input" type={showPassword ? "text" : "password"} />
                                    <span style={styles.eyeIcon} onClick={() => setShowPassword(!showPassword)}>
                                        {showPassword ? '🙈' : '👁️'}
                                    </span>
                                </div>
                            </div>
                        ))}
                        <button className="btn-primary">Lưu mật khẩu</button>

                        <div style={styles.divider}></div>
                        
                        <h3 className="title-sm" style={{color: 'var(--semantic-error)', marginBottom: 'var(--sp-sm)'}}>Xóa tài khoản</h3>
                        <p style={{color: 'var(--muted)', fontSize: '14px', marginBottom: 'var(--sp-base)', lineHeight: 1.6}}>
                            Nếu bạn xóa tài khoản, bạn sẽ mất quyền truy cập vĩnh viễn vào tài khoản này mà không có cách nào khôi phục. Dữ liệu cá nhân và tiến trình của bạn sẽ bị mất.
                        </p>
                        <button className="btn-danger" onClick={() => {setShowDeleteModal(true); setCountdown(5);}}>
                            Xóa tài khoản
                        </button>
                    </div>
                )}
            </div>

            {/* MODAL XÓA TÀI KHOẢN */}
            {showDeleteModal && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modalBox}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>Xóa tài khoản?</h3>
                        <p style={{color: 'var(--muted)', marginBottom: 'var(--sp-xl)', fontSize: '14px'}}>Hành động này không thể hoàn tác!</p>
                        <div style={{display: 'flex', gap: 'var(--sp-sm)', justifyContent: 'center'}}>
                            <button
                                className="btn-danger"
                                disabled={countdown > 0}
                                style={countdown > 0 ? {opacity: 0.4, cursor: 'not-allowed'} : {}}
                            >
                                Có {countdown > 0 ? `(${countdown}s)` : ''}
                            </button>
                            <button className="btn-outline" onClick={() => setShowDeleteModal(false)}>
                                Không
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '800px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg)',
    },
    tabHeader: {
        display: 'flex',
        borderBottom: '1px solid var(--hairline)',
        marginBottom: 'var(--sp-xl)',
        gap: 'var(--sp-xxs)',
    },
    tabBtn: {
        padding: 'var(--sp-sm) var(--sp-base)',
        cursor: 'pointer',
        border: 'none',
        background: 'none',
        fontFamily: 'var(--font-body)',
        fontSize: '15px',
        transition: 'all var(--transition-fast)',
    },
    avatarRow: {
        display: 'flex',
        gap: 'var(--sp-lg)',
        alignItems: 'center',
        marginBottom: 'var(--sp-xl)',
    },
    avatarCircle: {
        width: '56px',
        height: '56px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        border: '2px solid var(--hairline)',
    },
    formGroup: {
        marginBottom: 'var(--sp-base)',
    },
    label: {
        display: 'block',
        marginBottom: 'var(--sp-xs)',
        fontWeight: 500,
        fontSize: '14px',
        color: 'var(--body-strong, var(--ink))',
    },
    req: {
        color: 'var(--semantic-error)',
    },
    pwdWrapper: {
        position: 'relative',
    },
    eyeIcon: {
        position: 'absolute',
        right: 'var(--sp-sm)',
        top: '12px',
        cursor: 'pointer',
        fontSize: '16px',
    },
    divider: {
        height: '1px',
        backgroundColor: 'var(--hairline)',
        margin: 'var(--sp-xxl) 0',
    },
    modalOverlay: {
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        background: 'rgba(0,0,0,0.6)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(4px)',
    },
    modalBox: {
        backgroundColor: 'var(--surface-card)',
        color: 'var(--ink)',
        padding: 'var(--sp-xl)',
        borderRadius: 'var(--rounded-xl)',
        textAlign: 'center',
        width: '400px',
        maxWidth: '90%',
        border: '1px solid var(--hairline)',
        boxShadow: 'var(--shadow-dropdown)',
    },
};

export default AccountSettingsPage;