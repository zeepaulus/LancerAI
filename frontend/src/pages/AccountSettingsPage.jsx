import React, { useState, useEffect } from 'react';
import Navbar from '../components/Layout/Navbar';

const AccountSettingsPage = () => {
    const [activeTab, setActiveTab] = useState('overview');
    const [showPassword, setShowPassword] = useState(false);
    
    // Logic cho Modal Xóa tài khoản
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [countdown, setCountdown] = useState(5);

    useEffect(() => {
        let timer;
        if (showDeleteModal && countdown > 0) {
            timer = setInterval(() => setCountdown(c => c - 1), 1000);
        }
        return () => clearInterval(timer);
    }, [showDeleteModal, countdown]);

    const styles = {
        container: { maxWidth: '800px', margin: '40px auto', padding: '0 20px', fontFamily: 'system-ui' },
        tabHeader: { display: 'flex', borderBottom: '1px solid #e2e8f0', marginBottom: '30px' },
        tabBtn: (isActive) => ({ padding: '15px 20px', cursor: 'pointer', border: 'none', background: 'none', fontSize: '16px', fontWeight: isActive ? 'bold' : 'normal', color: isActive ? '#3182ce' : '#4a5568', borderBottom: isActive ? '3px solid #3182ce' : '3px solid transparent' }),
        formGroup: { marginBottom: '20px' },
        label: { display: 'block', marginBottom: '8px', fontWeight: '500' },
        req: { color: 'red' },
        input: { width: '100%', padding: '10px', border: '1px solid #cbd5e0', borderRadius: '6px' },
        btnSave: { padding: '10px 20px', background: '#3182ce', color: 'white', border: 'none', borderRadius: '6px', cursor: 'pointer', marginTop: '10px' },
        pwdWrapper: { position: 'relative' },
        eyeIcon: { position: 'absolute', right: '10px', top: '10px', cursor: 'pointer' },
        
        // Modal styles
        modalOverlay: { position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000 },
        modalBox: { background: 'white', padding: '30px', borderRadius: '8px', textAlign: 'center', width: '400px' },
        btnDanger: { background: '#e53e3e', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer' },
        btnDisabled: { background: '#feb2b2', color: 'white', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'not-allowed' },
        btnCancel: { background: '#edf2f7', padding: '10px 20px', border: 'none', borderRadius: '6px', cursor: 'pointer', marginLeft: '10px' }
    };

    return (
        <div>
            <Navbar />
            <div style={styles.container}>
                <h2>Quản lý tài khoản</h2>
                <div style={styles.tabHeader}>
                    <button style={styles.tabBtn(activeTab === 'overview')} onClick={() => setActiveTab('overview')}>Tổng quan</button>
                    <button style={styles.tabBtn(activeTab === 'contact')} onClick={() => setActiveTab('contact')}>Thông tin liên lạc</button>
                    <button style={styles.tabBtn(activeTab === 'security')} onClick={() => setActiveTab('security')}>Tài khoản & Bảo mật</button>
                </div>

                {/* TAB 1: TỔNG QUAN */}
                {activeTab === 'overview' && (
                    <div>
                        <div style={{display: 'flex', gap: '20px', alignItems: 'center', marginBottom: '30px'}}>
                            <div style={{width: '60px', height: '60px', borderRadius: '50%', background: '#ccc'}}></div>
                            <div>
                                <button style={{padding: '5px 10px'}}>Upload avatar</button>
                                <p style={{fontSize: '12px', color: '#718096', marginTop: '5px'}}>Max size: 2MB. Formats: JPG, PNG.</p>
                            </div>
                        </div>
                        <div style={styles.formGroup}><label style={styles.label}>Tên người dùng <span style={styles.req}>*</span></label><input style={styles.input} /></div>
                        <div style={styles.formGroup}><label style={styles.label}>Họ và tên <span style={styles.req}>*</span></label><input style={styles.input} /></div>
                        <div style={styles.formGroup}><label style={styles.label}>Tiểu sử</label><textarea style={{...styles.input, height: '80px'}} /></div>
                        <div style={styles.formGroup}><label style={styles.label}>Địa chỉ email <span style={styles.req}>*</span></label><input style={styles.input} type="email" /></div>
                        <button style={styles.btnSave}>Lưu thay đổi</button>
                    </div>
                )}

                {/* TAB 2: LIÊN LẠC */}
                {activeTab === 'contact' && (
                    <div>
                        <div style={styles.formGroup}><label style={styles.label}>Nơi làm việc hiện tại</label><input style={styles.input} /></div>
                        <div style={styles.formGroup}><label style={styles.label}>Số điện thoại</label><input style={styles.input} /></div>
                        <div style={styles.formGroup}><label style={styles.label}>Tên Github</label><input style={styles.input} /></div>
                        <div style={styles.formGroup}><label style={styles.label}>Tên Linkedin</label><input style={styles.input} /></div>
                        <button style={styles.btnSave}>Lưu thay đổi</button>
                    </div>
                )}

                {/* TAB 3: BẢO MẬT */}
                {activeTab === 'security' && (
                    <div>
                        <h3 style={{marginBottom: '15px'}}>Thay đổi mật khẩu</h3>
                        {['Mật khẩu hiện tại', 'Mật khẩu mới', 'Xác nhận mật khẩu mới'].map((label, i) => (
                            <div style={styles.formGroup} key={i}>
                                <label style={styles.label}>{label}</label>
                                <div style={styles.pwdWrapper}>
                                    <input style={styles.input} type={showPassword ? "text" : "password"} />
                                    <span style={styles.eyeIcon} onClick={() => setShowPassword(!showPassword)}>{showPassword ? '🙈' : '👁️'}</span>
                                </div>
                            </div>
                        ))}
                        <button style={styles.btnSave}>Lưu mật khẩu</button>

                        <hr style={{margin: '40px 0', borderColor: '#edf2f7'}} />
                        
                        <h3 style={{color: '#e53e3e'}}>Xóa tài khoản</h3>
                        <p style={{color: '#718096', fontSize: '14px', marginBottom: '15px'}}>Nếu bạn xóa tài khoản, bạn sẽ mất quyền truy cập vĩnh viễn vào tài khoản này mà không có cách nào khôi phục. Dữ liệu cá nhân và tiến trình của bạn sẽ bị mất.</p>
                        <button style={styles.btnDanger} onClick={() => {setShowDeleteModal(true); setCountdown(5);}}>Xóa tài khoản</button>
                    </div>
                )}
            </div>

            {/* MODAL XÓA TÀI KHOẢN */}
            {showDeleteModal && (
                <div style={styles.modalOverlay}>
                    <div style={styles.modalBox}>
                        <h2>Xóa tài khoản?</h2>
                        <p style={{margin: '20px 0'}}>Hành động này không thể hoàn tác!</p>
                        <button 
                            style={countdown > 0 ? styles.btnDisabled : styles.btnDanger} 
                            disabled={countdown > 0}
                        >
                            Có {countdown > 0 ? `(${countdown}s)` : ''}
                        </button>
                        <button style={styles.btnCancel} onClick={() => setShowDeleteModal(false)}>Không</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default AccountSettingsPage;