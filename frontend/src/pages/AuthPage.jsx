import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import * as keys from '../config/storageKeys';
import { login as apiLogin, me as apiMe, signup as apiSignup } from '../api/auth';
import { validateAuthForm } from '../utils/validation';

import googleLogo from '../assets/Logo/google_logo.png';
import microsoftLogo from '../assets/Logo/microsoft_logo.png';
import githubLogo from '../assets/Logo/github_logo.png';
import linkedinLogo from '../assets/Logo/linkedin_logo.png';
import logoImg from '../assets/Logo/lancerai_logo.png'

const AuthPage = () => {
    const navigate = useNavigate();
    const location = useLocation(); 
    
    const isLogin = location.pathname === '/login'; 
    
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        usernameOrEmail: '',
        password: ''
    });
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState('');

    // Reset form when switching between Login and Signup
    React.useEffect(() => {
        setFormData({
            username: '',
            email: '',
            usernameOrEmail: '',
            password: ''
        });
        setErrors({});
        setSubmitError('');
    }, [isLogin]);

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setErrors({ ...errors, [e.target.name]: '' });
        setSubmitError('');
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const validationErrors = validateAuthForm(isLogin, formData);
        
        if (Object.keys(validationErrors).length > 0) {
            setErrors(validationErrors);
            return;
        }

        setSubmitting(true);
        setSubmitError('');

        try {
            if (isLogin) {
                const identifier = formData.usernameOrEmail.trim();
                const data = await apiLogin({
                    identifier,
                    password: formData.password
                });
                if (data?.access_token) {
                    localStorage.setItem(keys.LANCERAI_ACCESS_TOKEN, data.access_token);
                }
                try {
                    const profile = await apiMe();
                    localStorage.setItem(keys.LANCERAI_USER_PROFILE, JSON.stringify(profile));
                } catch {
                    /** /me có thể 401/501 tùy cấu hình — vẫn cho vào dashboard nếu đã có token */
                }
                localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
                navigate('/dashboard');
            } else {
                await apiSignup({
                    email: formData.email.trim(),
                    password: formData.password,
                    display_name: formData.username.trim()
                });
                localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
                navigate('/login', {
                    replace: false,
                    state: { signupOk: true }
                });
            }
        } catch (err) {
            const msg = err instanceof Error ? err.message : String(err);
            setSubmitError(msg);
        } finally {
            setSubmitting(false);
        }
    };

    const signupBanner = location.state?.signupOk;

    const socials = [
        { src: googleLogo, alt: 'Google' },
        { src: microsoftLogo, alt: 'Microsoft' },
        { src: linkedinLogo, alt: 'LinkedIn' },
        { src: githubLogo, alt: 'GitHub' },
    ];

    return (
        <div style={styles.wrapper}>
            {/* Subtle background orbs */}
            <div className="gradient-orb gradient-orb--lavender" style={{width: '500px', height: '500px', top: '-150px', right: '-100px'}}></div>
            <div className="gradient-orb gradient-orb--mint" style={{width: '400px', height: '400px', bottom: '-100px', left: '-80px'}}></div>

            <div style={styles.card}>
                <div style={styles.header}>
                    <img src={logoImg} alt="Logo" style={styles.authLogo} />
                    <h2 className="display-sm" style={{marginBottom: 'var(--sp-xs)'}}>
                        {isLogin ? 'Chào mừng trở lại' : 'Tạo tài khoản mới'}
                    </h2>
                    <p style={styles.subtitle}>
                        {isLogin ? 'Đăng nhập để tiếp tục rèn luyện phỏng vấn' : 'Bắt đầu hành trình chinh phục nhà tuyển dụng'}
                    </p>
                </div>

                {isLogin && signupBanner && (
                    <div style={styles.bannerOk}>
                        🎉 Đăng ký thành công! Vui lòng đăng nhập để bắt đầu.
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    {submitError ? (
                        <div style={styles.bannerErr}>{submitError}</div>
                    ) : null}

                    {isLogin ? (
                        <div style={styles.inputGroup}>
                            <input className="text-input" name="usernameOrEmail" type="text" autoComplete="username" placeholder="Email hoặc Tên người dùng" value={formData.usernameOrEmail} onChange={handleInputChange} />
                            {errors.usernameOrEmail && <span style={styles.errorText}>{errors.usernameOrEmail}</span>}
                        </div>
                    ) : (
                        <>
                            <div style={styles.inputGroup}>
                                <input className="text-input" name="username" placeholder="Tên tài khoản (Chữ & Số)" value={formData.username} onChange={handleInputChange} />
                                {errors.username && <span style={styles.errorText}>{errors.username}</span>}
                            </div>
                            <div style={styles.inputGroup}>
                                <input className="text-input" name="email" type="email" autoComplete="email" placeholder="Địa chỉ Email" value={formData.email} onChange={handleInputChange} />
                                {errors.email && <span style={styles.errorText}>{errors.email}</span>}
                            </div>
                        </>
                    )}

                    <div style={styles.inputGroup}>
                        <input className="text-input" name="password" type="password" autoComplete={isLogin ? 'current-password' : 'new-password'} placeholder="Mật khẩu" value={formData.password} onChange={handleInputChange} />
                        {errors.password && <span style={styles.errorText}>{errors.password}</span>}
                    </div>

                    <button 
                        type="submit"
                        disabled={submitting}
                        className="btn-primary"
                        style={{width: '100%', marginTop: 'var(--sp-sm)', height: '44px', fontSize: '16px'}}
                    >
                        {submitting ? 'Đang xử lý...' : (isLogin ? 'Đăng nhập' : 'Đăng ký')}
                    </button>
                </form>

                <div style={styles.dividerBox}>
                    <div style={styles.line}></div>
                    <span style={styles.dividerText}>hoặc tiếp tục với</span>
                    <div style={styles.line}></div>
                </div>

                <div style={styles.socialGroup}>
                    {socials.map(s => (
                        <button key={s.alt} type="button" style={styles.socialBtn}>
                            <img src={s.src} alt={s.alt} style={styles.socialIcon} />
                        </button>
                    ))}
                </div>

                <div style={styles.footerInfo}>
                    {isLogin ? (
                        <p>Chưa có tài khoản? <span style={styles.link} onClick={() => { navigate('/signup'); setErrors({}); setSubmitError(''); }}>Đăng ký ngay</span></p>
                    ) : (
                        <p>Đã có tài khoản? <span style={styles.link} onClick={() => { navigate('/login'); setErrors({}); setSubmitError(''); }}>Đăng nhập</span></p>
                    )}
                </div>
            </div>
        </div>
    );
};

const styles = {
    wrapper: {
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        backgroundColor: 'var(--canvas)',
        fontFamily: 'var(--font-body)',
        padding: 'var(--sp-lg)',
        position: 'relative',
        overflow: 'hidden',
    },
    card: {
        width: '100%',
        maxWidth: '420px',
        backgroundColor: 'var(--surface-card)',
        padding: '40px',
        borderRadius: 'var(--rounded-xl)',
        border: '1px solid var(--hairline)',
        boxShadow: 'var(--shadow-soft)',
        position: 'relative',
        zIndex: 1,
    },
    header: {
        textAlign: 'center',
        marginBottom: 'var(--sp-xl)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
    },
    authLogo: {
        width: '48px',
        height: 'auto',
        marginBottom: 'var(--sp-base)',
    },
    subtitle: {
        fontSize: '14px',
        color: 'var(--muted)',
        letterSpacing: '0.15px',
    },
    inputGroup: {
        marginBottom: 'var(--sp-base)',
    },
    errorText: {
        color: 'var(--semantic-error)',
        fontSize: '13px',
        marginTop: 'var(--sp-xxs)',
        display: 'block',
    },
    bannerOk: {
        padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-md)',
        fontSize: '14px',
        marginBottom: 'var(--sp-base)',
        backgroundColor: '#dcfce7',
        color: '#166534',
        border: '1px solid #bbf7d0',
    },
    bannerErr: {
        padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-md)',
        fontSize: '14px',
        marginBottom: 'var(--sp-base)',
        backgroundColor: '#fef2f2',
        color: '#991b1b',
        border: '1px solid #fecaca',
    },
    dividerBox: {
        display: 'flex',
        alignItems: 'center',
        margin: 'var(--sp-xl) 0',
    },
    line: {
        flex: 1,
        height: '1px',
        backgroundColor: 'var(--hairline)',
    },
    dividerText: {
        padding: '0 var(--sp-base)',
        color: 'var(--muted-soft)',
        fontSize: '13px',
        whiteSpace: 'nowrap',
    },
    socialGroup: {
        display: 'flex',
        justifyContent: 'center',
        gap: 'var(--sp-base)',
    },
    socialBtn: {
        width: '48px',
        height: '48px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        border: '1px solid var(--hairline)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        cursor: 'pointer',
        transition: 'all var(--transition-fast)',
        padding: 0,
    },
    socialIcon: {
        width: '20px',
        height: '20px',
        objectFit: 'contain',
    },
    footerInfo: {
        textAlign: 'center',
        marginTop: 'var(--sp-xl)',
        fontSize: '14px',
        color: 'var(--muted)',
    },
    link: {
        color: 'var(--ink)',
        fontWeight: 500,
        cursor: 'pointer',
        textDecoration: 'underline',
        textUnderlineOffset: '2px',
    },
};

export default AuthPage;
