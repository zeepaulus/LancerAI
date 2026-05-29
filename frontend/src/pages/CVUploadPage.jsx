import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const CVUploadPage = () => {
    const navigate = useNavigate();
    const [dragActive, setDragActive] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            processFile(e.target.files[0]);
        }
    };

    const processFile = (file) => {
        setErrorMsg('');
        
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            setErrorMsg('Định dạng không hợp lệ! Vui lòng chỉ tải lên file PDF hoặc Hình ảnh (JPG, PNG).');
            return;
        }

        if (file.size > 5 * 1024 * 1024) {
            setErrorMsg('File quá lớn! Vui lòng chọn file dưới 5MB.');
            return;
        }

        setIsUploading(true);

        setTimeout(() => {
            setIsUploading(false);
            navigate('/chat');
        }, 1500);
    };

    const onButtonClick = () => {
        inputRef.current.click();
    };

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <h1 className="display-lg" style={styles.title}>Upload CV</h1>

                {/* Upload Zone */}
                <div 
                    style={{
                        ...styles.uploadBox,
                        backgroundColor: dragActive ? 'var(--surface-strong)' : 'var(--canvas-soft)',
                        borderColor: dragActive ? 'var(--ink)' : 'var(--hairline-strong)',
                    }}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    {/* Decorative orb */}
                    <div className="gradient-orb gradient-orb--sky" style={{width: '200px', height: '200px', top: '-50px', right: '-50px', opacity: 0.15}}></div>

                    <div style={{position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center'}}>
                        <div style={styles.uploadIcon}>
                            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                                <polyline points="17 8 12 3 7 8" />
                                <line x1="12" y1="3" x2="12" y2="15" />
                            </svg>
                        </div>
                        
                        {isUploading ? (
                            <div>
                                <p className="title-sm" style={{color: 'var(--ink)', marginBottom: 'var(--sp-xs)'}}>Đang xử lý file...</p>
                                <div style={styles.progressBar}>
                                    <div style={styles.progressFill}></div>
                                </div>
                            </div>
                        ) : (
                            <>
                                <button className="btn-outline" onClick={onButtonClick} style={{marginBottom: 'var(--sp-sm)'}}>
                                    Chọn CV
                                </button>
                                <span style={{color: 'var(--muted)', fontSize: '14px'}}>hoặc kéo thả CV vào đây</span>
                                <span style={{color: 'var(--muted-soft)', fontSize: '12px', marginTop: 'var(--sp-xs)'}}>PDF, JPG, PNG — Tối đa 5MB</span>
                                <input 
                                    ref={inputRef}
                                    type="file" 
                                    accept="application/pdf, image/jpeg, image/png, image/jpg" 
                                    onChange={handleChange} 
                                    style={{ display: 'none' }} 
                                />
                                {errorMsg && <p style={styles.errorText}>{errorMsg}</p>}
                            </>
                        )}
                    </div>
                </div>

                {/* Features */}
                <p className="caption-uppercase" style={{textAlign: 'center', color: 'var(--muted)', marginBottom: 'var(--sp-lg)'}}>
                    CV CỦA BẠN SẼ ĐƯỢC SỬ DỤNG CHO
                </p>
                <div style={styles.featuresGrid}>
                    {[
                        { icon: '🕒', title: 'Phân tích CV', desc: 'Đánh giá kỹ năng, kinh nghiệm và mức độ phù hợp với vị trí ứng tuyển.' },
                        { icon: '👥', title: 'Phỏng vấn giả lập', desc: 'Luyện tập phỏng vấn với các câu hỏi thực tế và phản hồi tức thì.' },
                        { icon: '⭐', title: 'Gợi ý việc làm', desc: 'Đề xuất công việc phù hợp dựa trên kỹ năng và nội dung CV của bạn.' },
                    ].map(f => (
                        <div key={f.title} style={styles.featureCard}>
                            <div style={styles.featureIcon}>{f.icon}</div>
                            <h4 className="title-sm" style={{marginBottom: 'var(--sp-xs)'}}>{f.title}</h4>
                            <p style={{color: 'var(--muted)', fontSize: '14px', lineHeight: 1.6}}>{f.desc}</p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '900px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg)',
        textAlign: 'center',
    },
    title: {
        textAlign: 'center',
        marginBottom: 'var(--sp-xl)',
    },
    uploadBox: {
        position: 'relative',
        overflow: 'hidden',
        border: '2px dashed var(--hairline-strong)',
        borderRadius: 'var(--rounded-xxl)',
        padding: '60px var(--sp-lg)',
        transition: 'all var(--transition-base)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 'var(--sp-xxl)',
    },
    uploadIcon: {
        width: '64px',
        height: '64px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--muted)',
        marginBottom: 'var(--sp-lg)',
    },
    progressBar: {
        width: '200px',
        height: '4px',
        backgroundColor: 'var(--hairline)',
        borderRadius: 'var(--rounded-pill)',
        overflow: 'hidden',
        marginTop: 'var(--sp-sm)',
    },
    progressFill: {
        height: '100%',
        width: '60%',
        backgroundColor: 'var(--ink)',
        borderRadius: 'var(--rounded-pill)',
        animation: 'pulse 1.5s ease-in-out infinite',
    },
    errorText: {
        color: 'var(--semantic-error)',
        marginTop: 'var(--sp-base)',
        fontWeight: 500,
        fontSize: '14px',
    },
    featuresGrid: {
        display: 'flex',
        gap: 'var(--sp-xl)',
        justifyContent: 'center',
        flexWrap: 'wrap',
    },
    featureCard: {
        flex: 1,
        minWidth: '200px',
        maxWidth: '280px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        textAlign: 'center',
    },
    featureIcon: {
        fontSize: '24px',
        marginBottom: 'var(--sp-sm)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '48px',
        height: '48px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
    },
};

export default CVUploadPage;