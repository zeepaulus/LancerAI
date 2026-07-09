import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { Alert, EmptyState, Page, PageHero, Panel, SkeletonRows, StatusBadge } from '../components/Common/AppUI';
import { AssetIllustration } from '../components/Common/Visuals';
import { createSession, getSessions, scrapeJD } from '../api/interview';
import { uploadCV } from '../api/extraction';
import * as keys from '../config/storageKeys';
import { IT_LEVELS, IT_ROLES } from '../data/questionBank';

const LEVELS = IT_LEVELS;
const MODES = [
    { value: 'practice', label: 'Luyện tập', desc: 'Có định hướng và phản hồi mang tính xây dựng.' },
    { value: 'mock', label: 'Mô phỏng', desc: 'Giống phỏng vấn thật hơn, ít gợi ý hơn.' },
];
const VALID_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE = 10 * 1024 * 1024;

function formatDate(isoString) {
    if (!isoString) return 'Chưa có ngày';
    return new Date(isoString).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function scoreTone(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

const InterviewPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const profile = JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');
    const fileInputRef = useRef(null);
    const practiceQuestion = location.state?.practiceQuestion || null;
    const questionBankSession = Array.isArray(location.state?.questionBankSession) ? location.state.questionBankSession : [];
    const jobPreset = location.state?.jobPreset || null;
    const presetRole = practiceQuestion?.role || questionBankSession[0]?.role || jobPreset?.role || '';
    const presetLevel = practiceQuestion?.level || questionBankSession[0]?.level || '';
    const presetQuestions = practiceQuestion
        ? [practiceQuestion.question]
        : questionBankSession.map((item) => item.question).filter(Boolean);
    const presetFocus = presetQuestions.length
        ? presetQuestions.join('\n')
        : jobPreset?.focusArea || '';
    const presetSessionName = presetQuestions.length
        ? 'Luyện từ ngân hàng câu hỏi'
        : jobPreset?.title
            ? `Luyện cho ${jobPreset.title}`
            : '';

    const [showModal, setShowModal] = useState(Boolean(practiceQuestion || questionBankSession.length || jobPreset));
    const [sessionName, setSessionName] = useState(presetSessionName);
    const [industry, setIndustry] = useState(presetRole);
    const [position, setPosition] = useState(presetRole || jobPreset?.title || '');
    const [level, setLevel] = useState(presetLevel);
    const [mode, setMode] = useState('practice');
    const [jdUrl, setJdUrl] = useState('');
    const [jdText, setJdText] = useState(jobPreset?.jdText || '');
    const [practiceFocus, setPracticeFocus] = useState(presetFocus);
    const [isScraping, setIsScraping] = useState(false);
    const [scrapeError, setScrapeError] = useState('');
    const [cvFile, setCvFile] = useState(null);
    const [cvDragActive, setCvDragActive] = useState(false);
    const [cvError, setCvError] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [formError, setFormError] = useState('');
    const [history, setHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    useEffect(() => {
        let active = true;
        setHistoryLoading(true);
        getSessions()
            .then((data) => {
                if (active) setHistory(Array.isArray(data) ? data : []);
            })
            .catch(() => {
                if (active) setHistory([]);
            })
            .finally(() => {
                if (active) setHistoryLoading(false);
            });
        return () => {
            active = false;
        };
    }, []);

    const resetForm = () => {
        setSessionName(presetSessionName);
        setIndustry(presetRole);
        setPosition(presetRole || jobPreset?.title || '');
        setLevel(presetLevel);
        setMode('practice');
        setJdUrl('');
        setJdText(jobPreset?.jdText || '');
        setPracticeFocus(presetFocus);
        setIsScraping(false);
        setScrapeError('');
        setCvFile(null);
        setCvError('');
        setFormError('');
    };

    const closeModal = () => {
        setShowModal(false);
        resetForm();
    };

    const validateCvFile = (file) => {
        setCvError('');
        if (!VALID_TYPES.includes(file.type)) {
            setCvError('Vui lòng chọn file PDF, JPG, PNG hoặc WebP.');
            return false;
        }
        if (file.size > MAX_SIZE) {
            setCvError('File quá lớn. Dung lượng tối đa là 10 MB.');
            return false;
        }
        return true;
    };

    const handleCvDrop = (event) => {
        event.preventDefault();
        event.stopPropagation();
        setCvDragActive(false);
        const file = event.dataTransfer.files?.[0];
        if (file && validateCvFile(file)) setCvFile(file);
    };

    const handleScrapeJD = async () => {
        if (!jdUrl.trim()) return;
        setIsScraping(true);
        setScrapeError('');
        try {
            const data = await scrapeJD(jdUrl);
            if (data.job_title) setPosition(data.job_title);
            if (data.jd_text) setJdText(data.jd_text);
        } catch (err) {
            setScrapeError(err.message || 'Không thể đọc URL JD này. Bạn có thể dán mô tả công việc thủ công.');
        } finally {
            setIsScraping(false);
        }
    };

    const roleTitle = (position.trim() || industry || '').trim();
    const canSubmit = sessionName.trim() && industry && level && cvFile && !submitting;

    const handleStart = async () => {
        if (!canSubmit) return;
        setSubmitting(true);
        setFormError('');

        try {
            const extractionData = await uploadCV(cvFile);
            const cvId = extractionData.cv_id;
            const sessionRes = await createSession({
                cv_id: cvId,
                mode,
                focus_area: [industry, level, practiceFocus.trim()].filter(Boolean).join(' | '),
                duration_minutes: 20,
                jd_text: jdText.trim() || undefined,
                jd_url: jdUrl.trim() || undefined,
                job_title: roleTitle || undefined,
            });

            navigate('/chat', {
                state: {
                    sessionId: sessionRes.session_id,
                    cvId,
                    extractionData,
                    sessionName: sessionName.trim(),
                    industry,
                    position: roleTitle,
                    level,
                    mode,
                    practiceFocus,
                    userName: profile.display_name || 'bạn',
                },
            });
        } catch (err) {
            if (err?.status === 401) setFormError('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
            else if (err?.status >= 500) setFormError('Máy chủ đang gặp lỗi. Vui lòng thử lại sau.');
            else setFormError(err?.message || 'Chưa thể tạo phiên phỏng vấn. Vui lòng thử lại.');
            setSubmitting(false);
        }
    };

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Phỏng vấn giọng nói"
                    title="Tạo phiên phỏng vấn có trọng tâm"
                    description="Chọn vai trò, cấp độ, CV và JD; sau đó vào phòng phỏng vấn bằng micro, transcript và camera nếu có."
                    visual={<AssetIllustration name="voice" />}
                    actions={<button className="btn-primary" onClick={() => { resetForm(); setShowModal(true); }}>Tạo phiên phỏng vấn</button>}
                    tone="voice"
                />

                {(practiceQuestion || questionBankSession.length > 0 || jobPreset) && (
                    <div className="ui-section-gap-bottom">
                        <Alert tone="ai" title="Đã nạp ngữ cảnh luyện tập">
                            {practiceQuestion
                                ? `Câu hỏi đã chọn: ${practiceQuestion.question}`
                                : questionBankSession.length
                                    ? `${questionBankSession.length} câu hỏi đã sẵn sàng cho phiên này.`
                                    : `Đã nạp ngữ cảnh việc làm cho ${jobPreset?.title || jobPreset?.role || 'vai trò IT này'}.`}
                        </Alert>
                    </div>
                )}

                <Panel title="Phiên phỏng vấn" subtitle="Các phiên gần đây và lối vào báo cáo.">
                    {historyLoading ? (
                        <SkeletonRows rows={5} />
                    ) : history.length === 0 ? (
                        <EmptyState
                            visual={<AssetIllustration name="emptyInterview" compact />}
                            title="Chưa có phiên phỏng vấn"
                            description="Tạo phiên phỏng vấn với CV, vai trò IT mục tiêu và JD nếu có."
                            action={<button className="btn-primary" onClick={() => setShowModal(true)}>Tạo phiên phỏng vấn</button>}
                        />
                    ) : (
                        <table className="data-table">
                            <thead>
                                <tr>
                                    <th>Phiên</th>
                                    <th>Ngày</th>
                                    <th>Chế độ</th>
                                    <th>Trạng thái</th>
                                    <th>Điểm</th>
                                </tr>
                            </thead>
                            <tbody>
                                {history.map((item) => {
                                    const score = Math.round(Number(item.overall_confidence || 0));
                                    return (
                                        <tr key={item.session_id} onClick={() => navigate('/interview-report', { state: { sessionId: item.session_id } })} className="ui-clickable-row">
                                            <td>
                                                <strong className="ui-row-title">{item.title || 'Phiên phỏng vấn'}</strong>
                                                {item.focus_area && <div className="caption">{item.focus_area}</div>}
                                            </td>
                                            <td>{formatDate(item.created_at)}</td>
                                            <td>{item.mode === 'mock' ? 'Mô phỏng' : 'Luyện tập'}</td>
                                            <td>
                                                <StatusBadge tone={item.status === 'incomplete' ? 'warning' : 'success'}>
                                                    {item.status === 'incomplete' ? 'Chưa hoàn tất' : 'Đã đánh giá'}
                                                </StatusBadge>
                                            </td>
                                            <td>{score ? <StatusBadge tone={scoreTone(score)}>{score}/100</StatusBadge> : 'Đang chờ'}</td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    )}
                </Panel>
            </Page>

            {showModal && (
                <div className="ui-modal-overlay" onClick={(event) => event.target === event.currentTarget && closeModal()}>
                    <div className="ui-modal-card" role="dialog" aria-modal="true" aria-labelledby="create-interview-title">
                        <div className="panel-header">
                            <div>
                                <h2 className="title-md" id="create-interview-title">Tạo phiên phỏng vấn</h2>
                                <p className="caption">Chọn vai trò IT, cấp độ, JD, CV và trọng tâm luyện tập trước khi bắt đầu.</p>
                            </div>
                            <button className="btn-ghost" onClick={closeModal}>Đóng</button>
                        </div>

                        <div className="ui-modal-body">
                            <label htmlFor="session-name" className="ui-field">
                                <span>Tên phiên</span>
                                <input id="session-name" className="text-input" placeholder="Frontend Developer - vòng tháng 7" value={sessionName} onChange={(e) => setSessionName(e.target.value)} />
                            </label>

                            <div className="ui-two-col">
                                <label htmlFor="interview-industry" className="ui-field">
                                    <span>Vai trò IT mục tiêu</span>
                                    <select
                                        id="interview-industry"
                                        className="text-input"
                                        value={industry}
                                        onChange={(e) => {
                                            setIndustry(e.target.value);
                                            if (!position.trim()) setPosition(e.target.value);
                                        }}
                                    >
                                        <option value="">Chọn vai trò IT</option>
                                        {IT_ROLES.map((item) => <option key={item} value={item}>{item}</option>)}
                                    </select>
                                </label>
                                <label htmlFor="interview-level" className="ui-field">
                                    <span>Cấp độ</span>
                                    <select id="interview-level" className="text-input" value={level} onChange={(e) => setLevel(e.target.value)}>
                                        <option value="">Chọn cấp độ</option>
                                        {LEVELS.map((item) => <option key={item} value={item}>{item}</option>)}
                                    </select>
                                </label>
                            </div>

                            <label htmlFor="interview-role" className="ui-field">
                                <span>Chức danh cụ thể trong JD</span>
                                <input id="interview-role" className="text-input" placeholder="React Frontend Developer" value={position} onChange={(e) => setPosition(e.target.value)} />
                            </label>

                            <div className="ui-field">
                                <span>Chế độ phỏng vấn</span>
                                <div className="ui-two-col">
                                    {MODES.map((item) => (
                                        <button
                                            key={item.value}
                                            type="button"
                                            className={`card ui-select-card ${mode === item.value ? 'is-active' : ''}`}
                                            onClick={() => setMode(item.value)}
                                        >
                                            <strong className="ui-row-title">{item.label}</strong>
                                            <p className="caption">{item.desc}</p>
                                        </button>
                                    ))}
                                </div>
                            </div>

                            <label htmlFor="jd-url" className="ui-field">
                                <span>URL mô tả công việc</span>
                                <div className="ui-field-row">
                                    <input id="jd-url" className="text-input" placeholder="https://..." value={jdUrl} onChange={(e) => setJdUrl(e.target.value)} disabled={isScraping} />
                                    <button className="btn-outline" type="button" onClick={handleScrapeJD} disabled={!jdUrl.trim() || isScraping}>
                                        {isScraping ? 'Đang đọc...' : 'Lấy JD'}
                                    </button>
                                </div>
                                {scrapeError && <span className="ui-error-text" role="alert">{scrapeError}</span>}
                            </label>

                            <label htmlFor="jd-text" className="ui-field">
                                <span>Nội dung mô tả công việc</span>
                                <textarea id="jd-text" className="text-input" placeholder="Dán JD để câu hỏi phỏng vấn sát vai trò hơn..." value={jdText} onChange={(e) => setJdText(e.target.value)} disabled={isScraping} />
                            </label>

                            <label htmlFor="practice-focus" className="ui-field">
                                <span>Trọng tâm luyện tập</span>
                                <textarea
                                    id="practice-focus"
                                    className="text-input"
                                    placeholder="Có thể nhập câu hỏi đã chọn, khoảng trống trong CV hoặc chủ đề theo JD..."
                                    value={practiceFocus}
                                    onChange={(e) => setPracticeFocus(e.target.value)}
                                />
                            </label>

                            <div className="ui-field">
                                <span>CV của bạn</span>
                                {cvFile ? (
                                    <div className="ui-file-card">
                                        <strong>{cvFile.name}</strong>
                                        <span className="caption">{Math.round(cvFile.size / 1024)} KB</span>
                                        <button className="btn-ghost" onClick={() => setCvFile(null)}>Gỡ file</button>
                                    </div>
                                ) : (
                                    <div
                                        className={`ui-dropzone ${cvDragActive ? 'is-active' : ''}`}
                                        onDragEnter={(event) => { event.preventDefault(); setCvDragActive(true); }}
                                        onDragOver={(event) => event.preventDefault()}
                                        onDragLeave={() => setCvDragActive(false)}
                                        onDrop={handleCvDrop}
                                    >
                                        <strong>Kéo CV vào đây</strong>
                                        <p className="caption">PDF, JPG, PNG hoặc WebP, tối đa 10 MB.</p>
                                        <button className="btn-outline" type="button" onClick={() => fileInputRef.current?.click()}>Chọn file</button>
                                        <input
                                            ref={fileInputRef}
                                            type="file"
                                            accept="application/pdf,image/jpeg,image/png,image/webp"
                                            onChange={(event) => {
                                                const file = event.target.files?.[0];
                                                if (file && validateCvFile(file)) setCvFile(file);
                                            }}
                                            className="ui-hidden-input"
                                        />
                                    </div>
                                )}
                                {cvError && <span className="ui-error-text" role="alert">{cvError}</span>}
                            </div>

                            {formError && <div className="ui-error-box" role="alert">{formError}</div>}
                        </div>

                        <div className="ui-modal-footer">
                            <button className="btn-outline" onClick={closeModal} disabled={submitting}>Hủy</button>
                            <button className="btn-primary" onClick={handleStart} disabled={!canSubmit}>
                                {submitting ? 'Đang chuẩn bị...' : 'Bắt đầu phiên'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default InterviewPage;
