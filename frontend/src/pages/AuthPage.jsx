import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { validateAuthForm } from '../utils/validation';

// Nhúng các file ảnh từ thư mục assets
import googleLogo from '../assets/google_logo.png';
import microsoftLogo from '../assets/microsoft_logo.png';
import githubLogo from '../assets/github_logo.png';
import linkedinLogo from '../assets/linkedin_logo.png';

const AuthPage = () => {
    const navigate = useNavigate();
    const [isLogin, setIsLogin] = useState(false);
    const [formData, setFormData] = useState({ username: '', email: '', usernameOrEmail: '', password: '' });
    const [errors, setErrors] = useState({});

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
        setErrors({ ...errors, [e.target.name]: '' });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const validationErrors = validateAuthForm(isLogin, formData);
        
        if (Object.keys(validationErrors).length > 0) {
            setErrors(validationErrors);
            return;
        }

        // Tạm thời lưu vào Local Storage
        const userJSON = JSON.stringify(formData);
        localStorage.setItem('mockUserDB', userJSON);
        console.log("Dữ liệu JSON đã lưu:", userJSON);

        navigate('/dashboard');
    };

    // --- Hệ thống Style giao diện hiện đại ---
    const styles = {
        wrapper: { minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#f4f7f6', fontFamily: 'system-ui, sans-serif' },
        card: { width: '100%', maxWidth: '400px', backgroundColor: '#fff', padding: '40px', borderRadius: '16px', boxShadow: '0 10px 30px rgba(0,0,0,0.08)' },
        header: { textAlign: 'center', marginBottom: '30px' },
        title: { fontSize: '24px', fontWeight: 'bold', color: '#1a1a1a', marginBottom: '8px' },
        subtitle: { fontSize: '14px', color: '#666' },
        
        inputGroup: { marginBottom: '15px' },
        input: { width: '100%', padding: '12px 15px', border: '1px solid #e1e1e1', borderRadius: '8px', fontSize: '15px', outline: 'none', transition: 'border 0.2s', boxSizing: 'border-box' },
        errorText: { color: '#e53e3e', fontSize: '13px', marginTop: '5px', display: 'block' },
        
        btnPrimary: { width: '100%', padding: '14px', backgroundColor: '#3182ce', color: '#fff', border: 'none', borderRadius: '8px', fontSize: '16px', fontWeight: 'bold', cursor: 'pointer', marginTop: '10px', transition: 'background 0.2s' },
        
        // Đường phân cách "hoặc tiếp tục với"
        dividerBox: { display: 'flex', alignItems: 'center', margin: '25px 0' },
        line: { flex: 1, height: '1px', backgroundColor: '#e1e1e1' },
        dividerText: { padding: '0 15px', color: '#888', fontSize: '14px' },
        
        // Nhóm nút mạng xã hội
        socialGroup: { display: 'flex', justifyContent: 'center', gap: '20px' },
        socialBtn: { width: '50px', height: '50px', borderRadius: '50%', backgroundColor: '#fff', border: '1px solid #e1e1e1', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', transition: 'all 0.2s', boxShadow: '0 2px 5px rgba(0,0,0,0.02)' },
        
        // Style ép kích thước ảnh logo
        socialIcon: { width: '24px', height: '24px', objectFit: 'contain' },
        
        footerInfo: { textAlign: 'center', marginTop: '30px', fontSize: '14px', color: '#666' },
        link: { color: '#3182ce', fontWeight: 'bold', cursor: 'pointer', textDecoration: 'none' }
    };

    return (
        <div style={styles.wrapper}>
            <div style={styles.card}>
                <div style={styles.header}>
                    <h2 style={styles.title}>{isLogin ? 'Chào mừng trở lại' : 'Tạo tài khoản mới'}</h2>
                    <p style={styles.subtitle}>
                        {isLogin ? 'Đăng nhập để tiếp tục rèn luyện phỏng vấn' : 'Bắt đầu hành trình chinh phục nhà tuyển dụng'}
                    </p>
                </div>
                
                <form onSubmit={handleSubmit}>
                    {isLogin ? (
                        <div style={styles.inputGroup}>
                            <input style={styles.input} name="usernameOrEmail" placeholder="Email hoặc Tên người dùng" onChange={handleInputChange} />
                            {errors.usernameOrEmail && <span style={styles.errorText}>{errors.usernameOrEmail}</span>}
                        </div>
                    ) : (
                        <>
                            <div style={styles.inputGroup}>
                                <input style={styles.input} name="username" placeholder="Tên tài khoản (Chữ & Số)" onChange={handleInputChange} />
                                {errors.username && <span style={styles.errorText}>{errors.username}</span>}
                            </div>
                            <div style={styles.inputGroup}>
                                <input style={styles.input} name="email" type="text" placeholder="Địa chỉ Email" onChange={handleInputChange} />
                                {errors.email && <span style={styles.errorText}>{errors.email}</span>}
                            </div>
                        </>
                    )}

                    <div style={styles.inputGroup}>
                        <input style={styles.input} name="password" type="password" placeholder="Mật khẩu" onChange={handleInputChange} />
                        {errors.password && <span style={styles.errorText}>{errors.password}</span>}
                    </div>

                    <button 
                        type="submit" 
                        style={styles.btnPrimary}
                        onMouseOver={(e) => e.target.style.backgroundColor = '#2b6cb0'}
                        onMouseOut={(e) => e.target.style.backgroundColor = '#3182ce'}
                    >
                        {isLogin ? 'Đăng nhập' : 'Đăng ký'}
                    </button>
                </form>

                {/* Khu vực Đăng nhập mạng xã hội */}
                <div style={styles.dividerBox}>
                    <div style={styles.line}></div>
                    <span style={styles.dividerText}>hoặc tiếp tục với</span>
                    <div style={styles.line}></div>
                </div>

                <div style={styles.socialGroup}>
                    {/* Nút Google */}
                    <button style={styles.socialBtn} onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f9f9f9'} onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}>
                        <img src={googleLogo} alt="Google" style={styles.socialIcon} />
                    </button>
                    {/* Nút Microsoft */}
                    <button style={styles.socialBtn} onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f9f9f9'} onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}>
                        <img src={microsoftLogo} alt="Microsoft" style={styles.socialIcon} />
                    </button>
                    {/* Nút LinkedIn */}
                    <button style={styles.socialBtn} onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f9f9f9'} onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}>
                        <img src={linkedinLogo} alt="LinkedIn" style={styles.socialIcon} />
                    </button>
                    {/* Nút GitHub */}
                    <button style={styles.socialBtn} onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#f9f9f9'} onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#fff'}>
                        <img src={githubLogo} alt="GitHub" style={styles.socialIcon} />
                    </button>
                </div>

                {/* Khu vực chuyển đổi giữa Đăng nhập / Đăng ký */}
                <div style={styles.footerInfo}>
                    {isLogin ? (
                        <p>Chưa có tài khoản? <span style={styles.link} onClick={() => { setIsLogin(false); setErrors({}); }}>Đăng ký ngay</span></p>
                    ) : (
                        <p>Đã có tài khoản? <span style={styles.link} onClick={() => { setIsLogin(true); setErrors({}); }}>Đăng nhập</span></p>
                    )}
                </div>
            </div>
        </div>
    );
};

export default AuthPage;