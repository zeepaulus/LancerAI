import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import * as keys from '../config/storageKeys';
import { login as apiLogin, me as apiMe, signup as apiSignup, googleLogin as apiGoogleLogin } from '../api/auth';
import { validateAuthForm } from '../utils/validation';

import googleLogo from '../assets/Logo/google_logo.png';
import microsoftLogo from '../assets/Logo/microsoft_logo.png';
import githubLogo from '../assets/Logo/github_logo.png';
import linkedinLogo from '../assets/Logo/linkedin_logo.png';
import logoImg from '../assets/Logo/lancerai_logo.png';
import { ProductMockupGraphic } from '../components/Common/Visuals';

const socials = [
    { src: googleLogo, alt: 'Google' },
    { src: microsoftLogo, alt: 'Microsoft' },
    { src: linkedinLogo, alt: 'LinkedIn' },
    { src: githubLogo, alt: 'GitHub' },
];

const initialForm = {
    username: '',
    email: '',
    usernameOrEmail: '',
    password: '',
};

const AuthPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const isLogin = location.pathname === '/login';

    const [formData, setFormData] = useState(initialForm);
    const [errors, setErrors] = useState({});
    const [submitting, setSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState('');

    useEffect(() => {
        setFormData(initialForm);
        setErrors({});
        setSubmitError('');
    }, [isLogin]);

    const handleInputChange = (event) => {
        const { name, value } = event.target;
        setFormData((current) => ({ ...current, [name]: value }));
        setErrors((current) => ({ ...current, [name]: '' }));
        setSubmitError('');
    };

    const handleSocialLogin = async (provider) => {
        // Microsoft, LinkedIn, GitHub, Google: use dynamic sandbox accounts
        setSubmitting(true);
        setSubmitError('');
        
        const mockEmail = `candidate.${provider.toLowerCase()}@lancerai.com`;
        const mockPassword = "SocialLoginPassword123!";
        const mockName = `${provider} Candidate`;

        try {
            let data;
            try {
                data = await apiLogin({
                    identifier: mockEmail,
                    password: mockPassword,
                });
            } catch (err) {
                await apiSignup({
                    email: mockEmail,
                    password: mockPassword,
                    display_name: mockName,
                });
                data = await apiLogin({
                    identifier: mockEmail,
                    password: mockPassword,
                });
            }

            if (data?.access_token) {
                localStorage.setItem(keys.LANCERAI_ACCESS_TOKEN, data.access_token);
                try {
                    const profile = await apiMe();
                    localStorage.setItem(keys.LANCERAI_USER_PROFILE, JSON.stringify(profile));
                } catch {
                    // Ignored
                }
                localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
                navigate('/dashboard');
            }
        } catch (err) {
            setSubmitError(`Lỗi kết nối ${provider}: ${err instanceof Error ? err.message : String(err)}`);
        } finally {
            setSubmitting(false);
        }
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        const validationErrors = validateAuthForm(isLogin, formData);

        if (Object.keys(validationErrors).length > 0) {
            setErrors(validationErrors);
            return;
        }

        setSubmitting(true);
        setSubmitError('');

        try {
            if (isLogin) {
                const data = await apiLogin({
                    identifier: formData.usernameOrEmail.trim(),
                    password: formData.password,
                });

                if (data?.access_token) {
                    localStorage.setItem(keys.LANCERAI_ACCESS_TOKEN, data.access_token);
                }

                try {
                    const profile = await apiMe();
                    localStorage.setItem(keys.LANCERAI_USER_PROFILE, JSON.stringify(profile));
                } catch {
                    // Keep login usable when profile hydration is not available.
                }

                localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
                navigate('/dashboard');
            } else {
                await apiSignup({
                    email: formData.email.trim(),
                    password: formData.password,
                    display_name: formData.username.trim(),
                });
                localStorage.removeItem(keys.LANCERAI_MOCK_USER_LEGACY);
                navigate('/login', { replace: false, state: { signupOk: true } });
            }
        } catch (err) {
            setSubmitError(err instanceof Error ? err.message : String(err));
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="auth-redesign-shell auth-shell">
            <section className="auth-visual-panel" aria-label="Xem trước các tính năng chính">
                <span className="status-badge status-badge--ai">CV, việc làm và phỏng vấn</span>
                <h1 className="title-lg">Tiếp tục phân tích CV và luyện phỏng vấn.</h1>
                <p className="caption">
                    Truy cập CV đã tải, phiên phỏng vấn giọng nói, kết quả so khớp việc làm và báo cáo.
                </p>
                <ProductMockupGraphic variant="workspace" />
            </section>

            <section className="auth-card" aria-label={isLogin ? 'Form đăng nhập' : 'Form đăng ký'}>
                <div className="auth-card__header">
                    <img src={logoImg} alt="LancerAI logo" className="auth-logo" />
                    <h2 className="display-sm">{isLogin ? 'Chào mừng quay lại' : 'Tạo tài khoản'}</h2>
                    <p>{isLogin ? 'Đăng nhập để xem CV, phiên phỏng vấn và báo cáo.' : 'Tạo tài khoản để lưu phân tích CV và báo cáo phỏng vấn.'}</p>
                </div>

                {isLogin && location.state?.signupOk && (
                    <div className="auth-banner auth-banner--success">Đã tạo tài khoản. Đăng nhập để bắt đầu.</div>
                )}

                <form onSubmit={handleSubmit} className="auth-form">
                    {submitError && <div className="auth-banner auth-banner--danger">{submitError}</div>}

                    {isLogin ? (
                        <div className="auth-field">
                            <input
                                className="text-input"
                                name="usernameOrEmail"
                                type="text"
                                autoComplete="username"
                                placeholder="Email hoặc tên hiển thị"
                                value={formData.usernameOrEmail}
                                onChange={handleInputChange}
                            />
                            {errors.usernameOrEmail && <span className="ui-error-text">{errors.usernameOrEmail}</span>}
                        </div>
                    ) : (
                        <>
                            <div className="auth-field">
                                <input
                                    className="text-input"
                                    name="username"
                                    placeholder="Tên hiển thị"
                                    value={formData.username}
                                    onChange={handleInputChange}
                                />
                                {errors.username && <span className="ui-error-text">{errors.username}</span>}
                            </div>
                            <div className="auth-field">
                                <input
                                    className="text-input"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    placeholder="Email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                />
                                {errors.email && <span className="ui-error-text">{errors.email}</span>}
                            </div>
                        </>
                    )}

                    <div className="auth-field">
                        <input
                            className="text-input"
                            name="password"
                            type="password"
                            autoComplete={isLogin ? 'current-password' : 'new-password'}
                            placeholder="Mật khẩu"
                            value={formData.password}
                            onChange={handleInputChange}
                        />
                        {errors.password && <span className="ui-error-text">{errors.password}</span>}
                    </div>

                    <button type="submit" disabled={submitting} className="btn-primary auth-submit">
                        {submitting ? 'Đang xử lý...' : (isLogin ? 'Đăng nhập' : 'Đăng ký')}
                    </button>
                </form>

                <div className="auth-divider">
                    <span />
                    <strong>hoặc tiếp tục với</strong>
                    <span />
                </div>

                <div className="auth-socials">
                    {socials.map((social) => (
                        <button
                            key={social.alt}
                            type="button"
                            className="auth-social-btn"
                            aria-label={`Tiếp tục với ${social.alt}`}
                            onClick={() => handleSocialLogin(social.alt)}
                        >
                            <img src={social.src} alt="" />
                        </button>
                    ))}
                </div>

                <div className="auth-footer">
                    {isLogin ? (
                        <p>Chưa có tài khoản? <button type="button" className="auth-link" onClick={() => { navigate('/signup'); setErrors({}); setSubmitError(''); }}>Tạo tài khoản</button></p>
                    ) : (
                        <p>Đã có tài khoản? <button type="button" className="auth-link" onClick={() => { navigate('/login'); setErrors({}); setSubmitError(''); }}>Đăng nhập</button></p>
                    )}
                </div>
            </section>
        </div>
    );
};

export default AuthPage;
