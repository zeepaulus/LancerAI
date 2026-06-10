import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { uploadCV } from '../api/extraction';

const VALID_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
const MAX_SIZE_BYTES = 10 * 1024 * 1024; // 10 MB — khớp với backend MAX_FILE_SIZE

const CVUploadPage = () => {
    const navigate = useNavigate();
    const [dragActive, setDragActive] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [uploadState, setUploadState] = useState('idle'); // 'idle' | 'uploading' | 'processing'
    const [selectedFile, setSelectedFile] = useState(null);
    const inputRef = useRef(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') setDragActive(true);
        else if (e.type === 'dragleave') setDragActive(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files?.[0]) validateAndStage(e.dataTransfer.files[0]);
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files?.[0]) validateAndStage(e.target.files[0]);
    };

    // ------------------------------------------------------------------ validate → stage
    const validateAndStage = (file) => {
        setErrorMsg('');

        // Backend chấp nhận: pdf, png, jpeg, webp (415 nếu sai)
        if (!VALID_TYPES.includes(file.type)) {
            setErrorMsg('Định dạng không hợp lệ. Vui lòng chọn file PDF, JPG, PNG hoặc WebP.');
            return;
        }
        if (file.size > MAX_SIZE_BYTES) {
            setErrorMsg('File quá lớn. Vui lòng chọn file dưới 10 MB.');
            return;
        }

        setSelectedFile(file);
    };

    // ------------------------------------------------------------------ submit
    const handleUpload = async () => {
        if (!selectedFile) return;

        setUploadState('uploading');
        setErrorMsg('');

        try {
            // Giai đoạn 1: gửi file lên server
            setUploadState('uploading');
            const extractionData = await uploadCV(selectedFile);
            // extractionData là CVExtractionResponse: { cv_id, personal_info, education, ... }

            // Giai đoạn 2: navigate với data → CVExtractionResultPage sẽ nhận qua location.state
            navigate('/cv-extraction-result', { state: { extractionData } });
        } catch (err) {
            setUploadState('idle');
            const msg = err?.message || 'Upload thất bại. Vui lòng thử lại.';
            // Map một số HTTP status code sang tiếng Việt dễ hiểu
            if (err?.status === 401) {
                setErrorMsg('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
            } else if (err?.status === 413) {
                setErrorMsg('File quá lớn (tối đa 10 MB).');
            } else if (err?.status === 415) {
                setErrorMsg('Định dạng file không được hỗ trợ.');
            } else if (err?.status >= 500) {
                setErrorMsg('Server đang xử lý lỗi. Vui lòng thử lại sau ít phút.');
            } else {
                setErrorMsg(msg);
            }
        }
    };

    const resetFile = () => {
        setSelectedFile(null);
        setErrorMsg('');
        if (inputRef.current) inputRef.current.value = '';
    };

    const isLoading = uploadState === 'uploading' || uploadState === 'processing';

    return (
        <div style={{ backgroundColor: 'var(--canvas)', minHeight: '100vh' }}>
            <Navbar />
            <div style={styles.container}>
                <h1 className="display-lg" style={styles.title}>Upload CV</h1>

                {/* Upload Zone */}
                <div
                    style={{
                        ...styles.uploadBox,
                        backgroundColor: dragActive ? 'var(--surface-strong)' : 'var(--canvas-soft)',
                        borderColor: dragActive ? 'var(--ink)' : selectedFile ? 'var(--ink)' : 'var(--hairline-strong)',
                        borderStyle: selectedFile ? 'solid' : 'dashed',
                    }}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={isLoading ? undefined : handleDrop}
                >
                    {/* <div className="gradient-orb gradient-orb--sky" style={{ width: '200px', height: '200px', top: '-50px', right: '-50px', opacity: 0.15 }} /> */}

                    <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', width: '100%' }}>
                        {/* Icon */}
                        <div style={{
                            ...styles.uploadIcon,
                            backgroundColor: selectedFile ? 'var(--ink)' : 'var(--surface-strong)',
                            color: selectedFile ? 'var(--canvas)' : 'var(--muted)',
                        }}>
                            {selectedFile ? (
                                // Checkmark khi đã chọn file
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                    <polyline points="20 6 9 17 4 12" />
                                </svg>
                            ) : (
                                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                                    <polyline points="17 8 12 3 7 8" />
                                    <line x1="12" y1="3" x2="12" y2="15" />
                                </svg>
                            )}
                        </div>

                        {/* Loading state */}
                        {isLoading ? (
                            <div style={{ textAlign: 'center' }}>
                                <p className="title-sm" style={{ color: 'var(--ink)', marginBottom: 'var(--sp-xs)' }}>
                                    {uploadState === 'uploading' ? 'Đang tải lên...' : 'Đang trích xuất CV...'}
                                </p>
                                <p style={{ color: 'var(--muted)', fontSize: '13px', marginBottom: 'var(--sp-sm)' }}>
                                    {uploadState === 'uploading'
                                        ? 'Đang gửi file đến server'
                                        : 'LLM đang phân tích nội dung CV — có thể mất 15–30 giây'}
                                </p>
                                <div style={styles.progressBar}>
                                    <div style={styles.progressFill} />
                                </div>
                            </div>

                        /* File đã chọn, chờ confirm */
                        ) : selectedFile ? (
                            <div style={{ textAlign: 'center', width: '100%', maxWidth: '400px' }}>
                                {/* File info card */}
                                <div style={styles.fileCard}>
                                    <div style={styles.fileIcon}>
                                        {selectedFile.type === 'application/pdf' ? '📄' : '🖼️'}
                                    </div>
                                    <div style={{ flex: 1, textAlign: 'left', overflow: 'hidden' }}>
                                        <p className="title-sm" style={{ margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                                            {selectedFile.name}
                                        </p>
                                        <p style={{ color: 'var(--muted)', fontSize: '13px', margin: 0 }}>
                                            {(selectedFile.size / 1024).toFixed(0)} KB
                                        </p>
                                    </div>
                                    <button
                                        onClick={resetFile}
                                        style={styles.removeBtn}
                                        title="Xóa file"
                                    >
                                        ✕
                                    </button>
                                </div>

                                {errorMsg && <p style={styles.errorText}>{errorMsg}</p>}

                                <button
                                    className="btn-primary"
                                    onClick={handleUpload}
                                    style={{ width: '100%', height: '44px', marginTop: 'var(--sp-base)' }}
                                >
                                    Trích xuất CV
                                </button>
                            </div>

                        /* Idle — chưa chọn file */
                        ) : (
                            <>
                                <button
                                    className="btn-outline"
                                    onClick={() => inputRef.current?.click()}
                                    style={{ marginBottom: 'var(--sp-sm)' }}
                                >
                                    Chọn CV
                                </button>
                                <span style={{ color: 'var(--muted)', fontSize: '14px' }}>hoặc kéo thả CV vào đây</span>
                                <span style={{ color: 'var(--muted-soft)', fontSize: '12px', marginTop: 'var(--sp-xs)' }}>
                                    PDF, JPG, PNG, WebP — Tối đa 10 MB
                                </span>
                                <input
                                    ref={inputRef}
                                    type="file"
                                    accept="application/pdf,image/jpeg,image/png,image/webp"
                                    onChange={handleChange}
                                    style={{ display: 'none' }}
                                />
                                {errorMsg && <p style={styles.errorText}>{errorMsg}</p>}
                            </>
                        )}
                    </div>
                </div>

                {/* Features */}
                <p className="caption-uppercase" style={{ textAlign: 'center', color: 'var(--muted)', marginBottom: 'var(--sp-lg)' }}>
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
                            <h4 className="title-sm" style={{ marginBottom: 'var(--sp-xs)' }}>{f.title}</h4>
                            <p style={{ color: 'var(--muted)', fontSize: '14px', lineHeight: 1.6 }}>{f.desc}</p>
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
        cursor: 'default',
    },
    uploadIcon: {
        width: '64px',
        height: '64px',
        borderRadius: 'var(--rounded-full)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        marginBottom: 'var(--sp-lg)',
        transition: 'all var(--transition-base)',
    },
    fileCard: {
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--sp-sm)',
        padding: 'var(--sp-sm) var(--sp-base)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-lg)',
        marginBottom: 'var(--sp-xs)',
    },
    fileIcon: {
        fontSize: '24px',
        flexShrink: 0,
    },
    removeBtn: {
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        color: 'var(--muted)',
        fontSize: '14px',
        padding: '4px 6px',
        borderRadius: 'var(--rounded-sm)',
        flexShrink: 0,
        lineHeight: 1,
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
        marginTop: 'var(--sp-sm)',
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
