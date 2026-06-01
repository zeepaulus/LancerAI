// import React from 'react';
// import { useNavigate } from 'react-router-dom';
// import Navbar from '../components/Layout/Navbar';

// const InterviewPage = () => {
//     const navigate = useNavigate();

//     const history = [
//         { id: 1, title: 'Phỏng vấn Frontend Developer', date: '24/10/2023', score: 85 },
//         { id: 2, title: 'Phỏng vấn Backend Node.js', date: '20/10/2023', score: 72 },
//         { id: 3, title: 'Phỏng vấn Hành vi (Behavioral)', date: '15/10/2023', score: 90 },
//     ];

//     const getScoreStyle = (score) => ({
//         backgroundColor: score >= 80 ? 'var(--gradient-mint)' : 'var(--gradient-peach)',
//         color: 'var(--ink)',
//     });

//     return (
//         <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
//             <Navbar />
//             <div style={styles.container}>
//                 <div style={styles.header}>
//                     <div>
//                         <h2 className="display-sm">Phỏng vấn AI</h2>
//                     </div>
//                     <button className="btn-primary" onClick={() => navigate('/chat')}>
//                         + Bắt đầu phỏng vấn
//                     </button>
//                 </div>

//                 <p className="caption-uppercase" style={styles.sectionLabel}>LỊCH SỬ PHỎNG VẤN</p>
//                 <div style={styles.cardList}>
//                     {history.map(item => (
//                         <div 
//                             key={item.id} 
//                             className="card"
//                             style={styles.historyCard}
//                             onClick={() => navigate('/chat')}
//                             onMouseEnter={(e) => {
//                                 e.currentTarget.style.borderColor = 'var(--hairline-strong)';
//                                 e.currentTarget.style.boxShadow = 'var(--shadow-soft)';
//                             }}
//                             onMouseLeave={(e) => {
//                                 e.currentTarget.style.borderColor = 'var(--hairline)';
//                                 e.currentTarget.style.boxShadow = 'none';
//                             }}
//                         >
//                             <div>
//                                 <h4 className="title-sm" style={{margin: '0 0 var(--sp-xs) 0'}}>{item.title}</h4>
//                                 <span style={styles.dateBadge}>Ngày: {item.date}</span>
//                             </div>
//                             <span className="badge-pill" style={getScoreStyle(item.score)}>
//                                 {item.score} Điểm
//                             </span>
//                         </div>
//                     ))}
//                 </div>
//             </div>
//         </div>
//     );
// };

// const styles = {
//     container: {
//         maxWidth: '800px',
//         margin: '0 auto',
//         padding: 'var(--sp-xl) var(--sp-lg)',
//     },
//     header: {
//         display: 'flex',
//         justifyContent: 'space-between',
//         alignItems: 'center',
//         marginBottom: 'var(--sp-xl)',
//     },
//     sectionLabel: {
//         color: 'var(--muted)',
//         marginBottom: 'var(--sp-base)',
//         letterSpacing: '0.96px',
//     },
//     cardList: {
//         display: 'flex',
//         flexDirection: 'column',
//         gap: 'var(--sp-sm)',
//     },
//     historyCard: {
//         display: 'flex',
//         justifyContent: 'space-between',
//         alignItems: 'center',
//         cursor: 'pointer',
//         transition: 'all var(--transition-base)',
//     },
//     dateBadge: {
//         fontSize: '13px',
//         color: 'var(--muted)',
//         letterSpacing: '0.15px',
//     },
// };

// export default InterviewPage;

import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { createSession } from '../api/interview';
import { uploadCV } from '../api/extraction';
import * as keys from '../config/storageKeys';

// ─── Constants ────────────────────────────────────────────────────────────────

const INDUSTRIES = [
    'Công nghệ thông tin', 'Kinh tế / Tài chính', 'Y tế / Dược',
    'Giáo dục', 'Kỹ thuật / Xây dựng', 'Marketing / Truyền thông',
    'Luật / Hành chính', 'Khác',
];

const LEVELS = ['Fresher', 'Junior', 'Middle', 'Senior', 'Lead / Manager'];

const VALID_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 10 * 1024 * 1024;

// mode backend: "practice" = chuẩn, "mock" = khắt khe
const MODES = [
    { value: 'practice', label: 'Chuẩn', desc: 'Có gợi ý và phản hồi mang tính xây dựng' },
    { value: 'mock',     label: 'Khắt khe', desc: 'Mô phỏng phỏng vấn thực tế, ít gợi ý hơn' },
];

// ─── Helpers ──────────────────────────────────────────────────────────────────

function formatDate(isoString) {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function scoreColor(score) {
    if (score >= 80) return 'var(--semantic-success, #22c55e)';
    if (score >= 60) return 'var(--semantic-warning, #f59e0b)';
    return 'var(--semantic-error, #ef4444)';
}

// ─── Component ────────────────────────────────────────────────────────────────

const InterviewPage = () => {
    const navigate = useNavigate();
    const profile = JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');

    // Modal state
    const [showModal, setShowModal] = useState(false);

    // Form fields
    const [sessionName, setSessionName] = useState('');
    const [industry, setIndustry]       = useState('');
    const [position, setPosition]       = useState('');
    const [level, setLevel]             = useState('');
    const [mode, setMode]               = useState('practice');

    // CV upload inside modal
    const [cvFile, setCvFile]           = useState(null);
    const [cvDragActive, setCvDragActive] = useState(false);
    const [cvError, setCvError]         = useState('');
    const fileInputRef = useRef(null);

    // Submission
    const [submitting, setSubmitting]   = useState(false);
    const [formError, setFormError]     = useState('');

    // History (placeholder — sẽ gọi API list sessions khi backend hỗ trợ)
    const [history, setHistory]         = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    // Reset form khi đóng modal
    const resetForm = () => {
        setSessionName(''); setIndustry(''); setPosition('');
        setLevel(''); setMode('practice');
        setCvFile(null); setCvError(''); setFormError('');
    };

    const openModal  = () => { resetForm(); setShowModal(true); };
    const closeModal = () => { setShowModal(false); resetForm(); };

    // ── CV drag-drop ────────────────────────────────────────────────────────

    const handleCvDrag = (e) => {
        e.preventDefault(); e.stopPropagation();
        if (e.type === 'dragenter' || e.type === 'dragover') setCvDragActive(true);
        else if (e.type === 'dragleave') setCvDragActive(false);
    };

    const validateCvFile = (file) => {
        setCvError('');
        if (!VALID_TYPES.includes(file.type)) {
            setCvError('Định dạng không hợp lệ. Chọn PDF, JPG, PNG hoặc WebP.');
            return false;
        }
        if (file.size > MAX_SIZE) {
            setCvError('File quá lớn (tối đa 10 MB).');
            return false;
        }
        return true;
    };

    const handleCvDrop = (e) => {
        e.preventDefault(); e.stopPropagation(); setCvDragActive(false);
        const file = e.dataTransfer.files?.[0];
        if (file && validateCvFile(file)) setCvFile(file);
    };

    const handleCvChange = (e) => {
        const file = e.target.files?.[0];
        if (file && validateCvFile(file)) setCvFile(file);
    };

    // ── Submit ───────────────────────────────────────────────────────────────

    const canSubmit = sessionName.trim() && industry && position.trim() && level && cvFile && !submitting;

    const handleStart = async () => {
        if (!canSubmit) return;
        setSubmitting(true);
        setFormError('');

        try {
            // 1. Upload CV → lấy cv_id
            const extractionData = await uploadCV(cvFile);
            const cvId = extractionData.cv_id;

            // 2. Tạo session trên backend
            const sessionRes = await createSession({
                cv_id: cvId,
                mode,
                focus_area: `${industry} — ${position} — ${level}`,
                duration_minutes: 20,
            });

            // 3. Chuyển sang ChatPage với đầy đủ context
            navigate('/chat', {
                state: {
                    sessionId:     sessionRes.session_id,
                    cvId,
                    extractionData,
                    sessionName:   sessionName.trim(),
                    industry,
                    position:      position.trim(),
                    level,
                    mode,
                    userName:      profile.display_name || 'bạn',
                },
            });
        } catch (err) {
            const msg = err?.message || 'Có lỗi xảy ra. Vui lòng thử lại.';
            if (err?.status === 401) setFormError('Phiên đăng nhập hết hạn. Vui lòng đăng nhập lại.');
            else if (err?.status >= 500) setFormError('Server đang gặp lỗi. Vui lòng thử lại sau.');
            else setFormError(msg);
            setSubmitting(false);
        }
    };

    // ─── Render ──────────────────────────────────────────────────────────────

    return (
        <div style={{ backgroundColor: 'var(--canvas)', minHeight: '100vh' }}>
            <Navbar />

            <div style={styles.container}>
                {/* Header */}
                <div style={styles.header}>
                    <div>
                        <h2 className="display-sm">Phỏng vấn AI</h2>
                        <p style={{ color: 'var(--muted)', marginTop: 'var(--sp-xs)', fontSize: '14px' }}>
                            Luyện tập phỏng vấn với AI, nhận đánh giá theo tiêu chí STAR.
                        </p>
                    </div>
                    <button className="btn-primary" onClick={openModal}>
                        + Bắt đầu phỏng vấn
                    </button>
                </div>

                {/* History */}
                <p className="caption-uppercase" style={styles.sectionLabel}>LỊCH SỬ PHỎNG VẤN</p>

                {historyLoading ? (
                    <div style={styles.emptyState}>
                        <div style={styles.spinner} />
                    </div>
                ) : history.length === 0 ? (
                    <div style={styles.emptyState}>
                        <p style={{ color: 'var(--muted)', fontSize: '14px' }}>
                            Chưa có buổi phỏng vấn nào. Nhấn <strong>+ Bắt đầu phỏng vấn</strong> để thử ngay.
                        </p>
                    </div>
                ) : (
                    <div style={styles.cardList}>
                        {history.map(item => (
                            <div
                                key={item.session_id}
                                className="card"
                                style={styles.historyCard}
                                onClick={() => navigate('/interview-report', { state: { sessionId: item.session_id } })}
                                onMouseEnter={e => {
                                    e.currentTarget.style.borderColor = 'var(--hairline-strong)';
                                    e.currentTarget.style.boxShadow  = 'var(--shadow-soft)';
                                }}
                                onMouseLeave={e => {
                                    e.currentTarget.style.borderColor = 'var(--hairline)';
                                    e.currentTarget.style.boxShadow  = 'none';
                                }}
                            >
                                <div>
                                    <h4 className="title-sm" style={{ margin: '0 0 var(--sp-xs) 0' }}>
                                        {item.title || 'Buổi phỏng vấn'}
                                    </h4>
                                    <span style={styles.dateBadge}>{formatDate(item.created_at)}</span>
                                </div>
                                <span
                                    className="badge-pill"
                                    style={{ backgroundColor: scoreColor(item.overall_confidence), color: '#fff' }}
                                >
                                    {Math.round(item.overall_confidence)} điểm
                                </span>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* ── Modal ── */}
            {showModal && (
                <div style={styles.overlay} onClick={(e) => e.target === e.currentTarget && closeModal()}>
                    <div style={styles.modal}>
                        {/* Modal header */}
                        <div style={styles.modalHeader}>
                            <h3 className="title-lg" style={{ margin: 0 }}>Thiết lập buổi phỏng vấn</h3>
                            <button onClick={closeModal} style={styles.closeBtn}>✕</button>
                        </div>

                        <div style={styles.modalBody}>
                            {/* Tên buổi phỏng vấn */}
                            <div style={styles.field}>
                                <label style={styles.label}>Tên buổi phỏng vấn <span style={styles.required}>*</span></label>
                                <input
                                    className="text-input"
                                    placeholder="VD: Phỏng vấn Frontend tháng 6"
                                    value={sessionName}
                                    onChange={e => setSessionName(e.target.value)}
                                />
                            </div>

                            {/* Ngành nghề */}
                            <div style={styles.field}>
                                <label style={styles.label}>Ngành nghề <span style={styles.required}>*</span></label>
                                <select
                                    className="text-input"
                                    value={industry}
                                    onChange={e => setIndustry(e.target.value)}
                                    style={{ cursor: 'pointer' }}
                                >
                                    <option value="">-- Chọn ngành --</option>
                                    {INDUSTRIES.map(i => <option key={i} value={i}>{i}</option>)}
                                </select>
                            </div>

                            {/* Vị trí & Trình độ */}
                            <div style={{ display: 'flex', gap: 'var(--sp-base)' }}>
                                <div style={{ ...styles.field, flex: 2 }}>
                                    <label style={styles.label}>Vị trí ứng tuyển <span style={styles.required}>*</span></label>
                                    <input
                                        className="text-input"
                                        placeholder="VD: Frontend Developer"
                                        value={position}
                                        onChange={e => setPosition(e.target.value)}
                                    />
                                </div>
                                <div style={{ ...styles.field, flex: 1 }}>
                                    <label style={styles.label}>Trình độ <span style={styles.required}>*</span></label>
                                    <select
                                        className="text-input"
                                        value={level}
                                        onChange={e => setLevel(e.target.value)}
                                        style={{ cursor: 'pointer' }}
                                    >
                                        <option value="">-- Chọn --</option>
                                        {LEVELS.map(l => <option key={l} value={l}>{l}</option>)}
                                    </select>
                                </div>
                            </div>

                            {/* Chế độ đánh giá */}
                            <div style={styles.field}>
                                <label style={styles.label}>Chế độ đánh giá</label>
                                <div style={{ display: 'flex', gap: 'var(--sp-sm)' }}>
                                    {MODES.map(m => (
                                        <div
                                            key={m.value}
                                            onClick={() => setMode(m.value)}
                                            style={{
                                                ...styles.modeCard,
                                                borderColor: mode === m.value ? 'var(--ink)' : 'var(--hairline)',
                                                backgroundColor: mode === m.value ? 'var(--surface-strong)' : 'var(--canvas-soft)',
                                            }}
                                        >
                                            <span style={{ fontWeight: 600, fontSize: '14px' }}>{m.label}</span>
                                            <span style={{ color: 'var(--muted)', fontSize: '12px', marginTop: '2px' }}>{m.desc}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* CV Upload */}
                            <div style={styles.field}>
                                <label style={styles.label}>Upload CV <span style={styles.required}>*</span></label>
                                {cvFile ? (
                                    <div style={styles.fileCard}>
                                        <span>{cvFile.type === 'application/pdf' ? '📄' : '🖼️'}</span>
                                        <span style={{ flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '14px' }}>
                                            {cvFile.name}
                                        </span>
                                        <span style={{ color: 'var(--muted)', fontSize: '13px', flexShrink: 0 }}>
                                            {(cvFile.size / 1024).toFixed(0)} KB
                                        </span>
                                        <button
                                            onClick={() => { setCvFile(null); setCvError(''); }}
                                            style={styles.removeBtn}
                                        >✕</button>
                                    </div>
                                ) : (
                                    <div
                                        style={{
                                            ...styles.dropzone,
                                            borderColor: cvDragActive ? 'var(--ink)' : 'var(--hairline-strong)',
                                            backgroundColor: cvDragActive ? 'var(--surface-strong)' : 'var(--canvas-soft)',
                                        }}
                                        onDragEnter={handleCvDrag}
                                        onDragLeave={handleCvDrag}
                                        onDragOver={handleCvDrag}
                                        onDrop={handleCvDrop}
                                    >
                                        <span style={{ fontSize: '20px' }}>📎</span>
                                        <span style={{ fontSize: '13px', color: 'var(--muted)' }}>
                                            Kéo thả hoặc{' '}
                                            <span
                                                style={{ color: 'var(--ink)', textDecoration: 'underline', cursor: 'pointer' }}
                                                onClick={() => fileInputRef.current?.click()}
                                            >chọn file</span>
                                        </span>
                                        <span style={{ fontSize: '11px', color: 'var(--muted-soft)' }}>PDF, JPG, PNG, WebP — tối đa 10 MB</span>
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept="application/pdf,image/jpeg,image/png,image/webp"
                                            onChange={handleCvChange}
                                            style={{ display: 'none' }}
                                        />
                                    </div>
                                )}
                                {cvError && <p style={styles.errorText}>{cvError}</p>}
                            </div>

                            {formError && <p style={styles.errorText}>{formError}</p>}
                        </div>

                        {/* Modal footer */}
                        <div style={styles.modalFooter}>
                            <button className="btn-outline" onClick={closeModal} disabled={submitting}>
                                Huỷ
                            </button>
                            <button
                                className="btn-primary"
                                onClick={handleStart}
                                disabled={!canSubmit}
                                style={{ minWidth: '160px' }}
                            >
                                {submitting ? 'Đang xử lý...' : 'Bắt đầu phỏng vấn →'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = {
    container: {
        maxWidth: '800px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg)',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'flex-start',
        marginBottom: 'var(--sp-xl)',
    },
    sectionLabel: {
        color: 'var(--muted)',
        marginBottom: 'var(--sp-base)',
        letterSpacing: '0.96px',
    },
    cardList: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-sm)',
    },
    historyCard: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        transition: 'all var(--transition-base)',
    },
    dateBadge: {
        fontSize: '13px',
        color: 'var(--muted)',
    },
    emptyState: {
        padding: 'var(--sp-xxl)',
        textAlign: 'center',
        border: '1px dashed var(--hairline)',
        borderRadius: 'var(--rounded-xl)',
    },
    spinner: {
        width: '28px', height: '28px',
        border: '3px solid var(--hairline)',
        borderTop: '3px solid var(--ink)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
        margin: '0 auto',
    },
    // Modal
    overlay: {
        position: 'fixed', inset: 0,
        backgroundColor: 'rgba(0,0,0,0.45)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        zIndex: 1000,
        padding: 'var(--sp-lg)',
    },
    modal: {
        backgroundColor: 'var(--surface-card)',
        borderRadius: 'var(--rounded-xxl)',
        border: '1px solid var(--hairline)',
        width: '100%',
        maxWidth: '560px',
        maxHeight: '90vh',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden',
        boxShadow: 'var(--shadow-lg, 0 20px 60px rgba(0,0,0,0.2))',
    },
    modalHeader: {
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        padding: 'var(--sp-lg) var(--sp-xl)',
        borderBottom: '1px solid var(--hairline)',
        flexShrink: 0,
    },
    modalBody: {
        padding: 'var(--sp-lg) var(--sp-xl)',
        overflowY: 'auto',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-base)',
    },
    modalFooter: {
        padding: 'var(--sp-base) var(--sp-xl)',
        borderTop: '1px solid var(--hairline)',
        display: 'flex',
        justifyContent: 'flex-end',
        gap: 'var(--sp-sm)',
        flexShrink: 0,
    },
    closeBtn: {
        background: 'none', border: 'none', cursor: 'pointer',
        color: 'var(--muted)', fontSize: '18px',
        padding: '4px 8px', borderRadius: 'var(--rounded-sm)',
        lineHeight: 1,
    },
    field: {
        display: 'flex', flexDirection: 'column', gap: 'var(--sp-xs)',
    },
    label: {
        fontSize: '13px', fontWeight: 600, color: 'var(--ink)',
        letterSpacing: '0.1px',
    },
    required: { color: 'var(--semantic-error, #ef4444)' },
    modeCard: {
        flex: 1, padding: 'var(--sp-sm) var(--sp-base)',
        border: '2px solid', borderRadius: 'var(--rounded-lg)',
        cursor: 'pointer', transition: 'all var(--transition-base)',
        display: 'flex', flexDirection: 'column',
    },
    dropzone: {
        border: '2px dashed',
        borderRadius: 'var(--rounded-lg)',
        padding: 'var(--sp-lg)',
        display: 'flex', flexDirection: 'column',
        alignItems: 'center', gap: 'var(--sp-xs)',
        textAlign: 'center', transition: 'all var(--transition-base)',
    },
    fileCard: {
        display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)',
        padding: 'var(--sp-sm) var(--sp-base)',
        backgroundColor: 'var(--surface-strong)',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-lg)',
    },
    removeBtn: {
        background: 'none', border: 'none', cursor: 'pointer',
        color: 'var(--muted)', fontSize: '13px',
        padding: '2px 6px', borderRadius: 'var(--rounded-sm)',
        flexShrink: 0, lineHeight: 1,
    },
    errorText: {
        color: 'var(--semantic-error, #ef4444)',
        fontSize: '13px', fontWeight: 500, margin: 0,
    },
};

export default InterviewPage;
