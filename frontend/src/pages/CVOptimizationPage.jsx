import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { optimizeCV, downloadPDF } from '../api/optimization';

/**
 * CVOptimizationPage — Multi-agent CV analysis pipeline.
 * Calls POST /optimization/cvs/{cv_id}/optimizations
 */
const CVOptimizationPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const cvId = location.state?.cvId;

    const [jobTitle, setJobTitle] = useState('');
    const [industry, setIndustry] = useState('technology');
    const [mode, setMode] = useState('standard');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);
    const [downloading, setDownloading] = useState(false);

    const handleAnalyze = async () => {
        if (!cvId) { setError('Không tìm thấy CV. Vui lòng upload CV trước.'); return; }
        setLoading(true);
        setError('');
        try {
            const data = await optimizeCV(cvId, {
                target_job_title: jobTitle,
                target_industry: industry,
                mode,
            });
            setResult(data);
        } catch (err) {
            setError(err.message || 'Phân tích thất bại.');
        } finally {
            setLoading(false);
        }
    };

    const handleDownloadPDF = async (template = 'harvard') => {
        if (!cvId) return;
        setDownloading(true);
        try {
            const blob = await downloadPDF(cvId, template);
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `cv_optimized_${template}.pdf`;
            a.click();
            URL.revokeObjectURL(url);
        } catch (err) {
            setError(err.message || 'Download thất bại.');
        } finally {
            setDownloading(false);
        }
    };

    if (!cvId) {
        return (
            <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
                <Navbar />
                <div style={styles.container}>
                    <div style={{textAlign: 'center', padding: 'var(--sp-section) 0'}}>
                        <p className="title-md">Không tìm thấy CV</p>
                        <p style={{color: 'var(--muted)', marginBottom: 'var(--sp-lg)'}}>Vui lòng upload CV trước.</p>
                        <button className="btn-primary" onClick={() => navigate('/cv-upload')}>Upload CV</button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <button className="btn-tertiary" style={{marginBottom: 'var(--sp-base)'}} onClick={() => navigate(-1)}>← Quay lại</button>

                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>PHÂN TÍCH CV</p>
                <h1 className="display-sm" style={{marginBottom: 'var(--sp-xl)'}}>Tối ưu hóa CV theo chuẩn ATS</h1>

                {/* Config Form */}
                {!result && (
                    <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                        <div style={styles.formRow}>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Vị trí ứng tuyển</label>
                                <input className="text-input" placeholder="VD: Frontend Developer" value={jobTitle} onChange={e => setJobTitle(e.target.value)} />
                            </div>
                            <div style={styles.formGroup}>
                                <label style={styles.label}>Ngành nghề</label>
                                <select className="text-input" value={industry} onChange={e => setIndustry(e.target.value)}>
                                    <option value="technology">Công nghệ</option>
                                    <option value="finance">Tài chính</option>
                                    <option value="education">Giáo dục</option>
                                    <option value="healthcare">Y tế</option>
                                </select>
                            </div>
                        </div>

                        <div style={{marginBottom: 'var(--sp-lg)'}}>
                            <label style={styles.label}>Chế độ đánh giá</label>
                            <div style={{display: 'flex', gap: 'var(--sp-sm)'}}>
                                {[
                                    { key: 'standard', label: '📋 Chuẩn', desc: 'Đánh giá chi tiết, gợi ý cải thiện' },
                                    { key: 'roast', label: '🔥 Roast', desc: 'Phản biện mạnh, góp ý thẳng thắn' },
                                ].map(m => (
                                    <button
                                        key={m.key}
                                        className="card"
                                        style={{
                                            ...styles.modeBtn,
                                            borderColor: mode === m.key ? 'var(--ink)' : 'var(--hairline)',
                                            borderWidth: mode === m.key ? '2px' : '1px',
                                        }}
                                        onClick={() => setMode(m.key)}
                                    >
                                        <span style={{fontSize: '16px'}}>{m.label}</span>
                                        <span style={{fontSize: '12px', color: 'var(--muted)'}}>{m.desc}</span>
                                    </button>
                                ))}
                            </div>
                        </div>

                        {error && <p style={{color: 'var(--semantic-error)', fontSize: '14px', marginBottom: 'var(--sp-sm)'}}>{error}</p>}

                        <button className="btn-primary" onClick={handleAnalyze} disabled={loading} style={{height: '44px', width: '100%'}}>
                            {loading ? 'Đang phân tích... (có thể mất 30-60s)' : 'Bắt đầu phân tích'}
                        </button>
                    </div>
                )}

                {/* Loading State */}
                {loading && (
                    <div className="card" style={{padding: 'var(--sp-xxl)', textAlign: 'center'}}>
                        <div style={styles.spinner}></div>
                        <p className="title-sm" style={{marginTop: 'var(--sp-base)'}}>Đang chạy pipeline phân tích...</p>
                        <p style={{color: 'var(--muted)', fontSize: '14px', marginTop: 'var(--sp-xs)'}}>
                            Retrieval → Roast → Rewrite → Audit
                        </p>
                    </div>
                )}

                {/* Results */}
                {result && (
                    <>
                        {/* Score & Summary Card */}
                        <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                            <div style={styles.resultGrid}>
                                <div style={{textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
                                    <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-sm)'}}>ĐIỂM ATS</p>
                                    <div style={styles.scoreCircle}>
                                        <svg viewBox="0 0 120 120" style={{width: '140px', height: '140px', transform: 'rotate(-90deg)'}}>
                                            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--hairline)" strokeWidth="8" />
                                            <circle cx="60" cy="60" r="52" fill="none"
                                                stroke={result.audit_score >= 70 ? 'var(--gradient-mint)' : result.audit_score >= 40 ? 'var(--gradient-peach)' : 'var(--gradient-rose)'}
                                                strokeWidth="8"
                                                strokeDasharray={`${2 * Math.PI * 52 * (result.audit_score / 100)} ${2 * Math.PI * 52}`}
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                        <div style={styles.scoreLabel}>
                                            <span style={{fontSize: '36px', fontWeight: 300, fontFamily: 'var(--font-display)', color: 'var(--ink)'}}>{Math.round(result.audit_score)}</span>
                                            <span style={{fontSize: '14px', color: 'var(--muted)'}}>/100</span>
                                        </div>
                                    </div>
                                </div>
                                <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center', flex: '1 1 350px'}}>
                                    <h3 className="title-md" style={{marginBottom: 'var(--sp-xs)', display: 'flex', alignItems: 'center', gap: '8px'}}>
                                        {mode === 'roast' ? '🔥 Nhận xét phê bình (Roast Summary)' : '📋 Đánh giá tổng quan'}
                                    </h3>
                                    <p style={{color: 'var(--ink)', fontSize: '15px', lineHeight: '1.6', fontStyle: mode === 'roast' ? 'italic' : 'normal', margin: 0}}>
                                        {result.roast_summary || 'CV đã được phân tích thành công. Dưới đây là các điểm cần cải thiện để tối ưu điểm số ATS.'}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {result.cv_scorecard && Object.keys(result.cv_scorecard).length > 0 && (
                            <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                                <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>
                                    Scorecard CV & trọng tâm phỏng vấn
                                </h3>
                                <div style={styles.scorecardGrid}>
                                    {Object.entries(result.cv_scorecard.section_scores || {}).map(([key, value]) => (
                                        <div key={key} style={styles.scoreMetric}>
                                            <span style={styles.metricLabel}>{formatMetricLabel(key)}</span>
                                            <strong style={styles.metricValue}>{Math.round(value)}/100</strong>
                                            <div style={styles.metricBar}>
                                                <div style={{...styles.metricFill, width: `${Math.min(100, Math.max(0, value))}%`}} />
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div style={styles.scorecardColumns}>
                                    <div>
                                        <h4 style={styles.subTitle}>Kỹ năng khớp JD/vị trí</h4>
                                        <div style={styles.chipWrap}>
                                            {(result.cv_scorecard.matched_skills || []).length > 0
                                                ? result.cv_scorecard.matched_skills.map((skill) => (
                                                    <span key={skill} style={styles.goodChip}>{skill}</span>
                                                ))
                                                : <span style={styles.mutedText}>Chưa có kỹ năng khớp rõ ràng.</span>}
                                        </div>
                                    </div>
                                    <div>
                                        <h4 style={styles.subTitle}>Khoảng trống cần hỏi sâu</h4>
                                        <div style={styles.chipWrap}>
                                            {(result.cv_scorecard.missing_skills || []).length > 0
                                                ? result.cv_scorecard.missing_skills.map((skill) => (
                                                    <span key={skill} style={styles.warnChip}>{skill}</span>
                                                ))
                                                : <span style={styles.mutedText}>Không có gap lớn theo scoring hiện tại.</span>}
                                        </div>
                                    </div>
                                </div>
                                {(result.cv_scorecard.interview_focus || []).length > 0 && (
                                    <div style={{marginTop: 'var(--sp-base)'}}>
                                        <h4 style={styles.subTitle}>Gợi ý phỏng vấn từ CV</h4>
                                        <ul style={styles.focusList}>
                                            {result.cv_scorecard.interview_focus.map((item, idx) => <li key={idx}>{item}</li>)}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Roast Issues Section */}
                        {result.roast_issues && result.roast_issues.length > 0 && (
                            <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                                <h3 className="title-md" style={{marginBottom: 'var(--sp-base)', borderBottom: '1px solid var(--hairline)', paddingBottom: '8px'}}>
                                    🔍 Các lỗi và điểm yếu cần khắc phục ({result.roast_issues.length})
                                </h3>
                                <div style={{display: 'flex', flexDirection: 'column', gap: 'var(--sp-base)'}}>
                                    {result.roast_issues.map((issue, idx) => {
                                        const sev = getSeverityColor(issue.severity);
                                        return (
                                            <div key={idx} style={styles.issueItem}>
                                                <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '8px', marginBottom: '8px'}}>
                                                    <div style={{display: 'flex', gap: '6px', flexWrap: 'wrap'}}>
                                                        <span style={{...styles.badge, backgroundColor: sev.bg, color: sev.color}}>
                                                            {issue.severity.toUpperCase()}
                                                        </span>
                                                        <span style={{...styles.badge, backgroundColor: 'var(--canvas)', color: 'var(--muted)', border: '1px solid var(--hairline)'}}>
                                                            {getIssueTypeLabel(issue.issue_type)}
                                                        </span>
                                                    </div>
                                                    <span style={{fontSize: '12px', color: 'var(--muted)'}}>Phần: {issue.field}</span>
                                                </div>
                                                <div style={{marginBottom: '6px'}}>
                                                    <span style={{fontSize: '13px', color: 'var(--muted)', fontWeight: 500}}>Văn bản gốc:</span>
                                                    <p style={styles.originalTextQuote}>"{issue.original_text}"</p>
                                                </div>
                                                <div>
                                                    <span style={{fontSize: '13px', color: 'var(--muted)', fontWeight: 500}}>Giải thích & Gợi ý cải thiện:</span>
                                                    <p style={{fontSize: '14px', color: 'var(--ink)', margin: '4px 0 0 0', lineHeight: '1.5'}}>{issue.explanation}</p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        )}

                        {/* Rewritten Sections Section */}
                        {result.rewritten_sections && result.rewritten_sections.length > 0 && (
                            <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                                <h3 className="title-md" style={{marginBottom: 'var(--sp-base)', borderBottom: '1px solid var(--hairline)', paddingBottom: '8px'}}>
                                    ✨ Đề xuất viết lại theo chuẩn Google XYZ
                                </h3>
                                <div style={{display: 'flex', flexDirection: 'column', gap: 'var(--sp-lg)'}}>
                                    {result.rewritten_sections.map((sec, idx) => (
                                        <div key={idx} style={styles.rewriteItem}>
                                            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}>
                                                <span style={{fontSize: '12px', color: 'var(--muted)'}}>Vị trí: {sec.field}</span>
                                                <span style={{...styles.badge, backgroundColor: 'var(--gradient-mint)', color: '#2e7d32'}}>
                                                    Điểm cải thiện: +{Math.round(sec.improvement_score * 100)}%
                                                </span>
                                            </div>
                                            <div style={styles.rewriteComparisonGrid}>
                                                <div style={styles.rewriteColOriginal}>
                                                    <span style={styles.rewriteColLabel}>Bản gốc:</span>
                                                    <p style={{margin: 0, fontSize: '14px', color: '#ef6c00'}}>"{sec.original}"</p>
                                                </div>
                                                <div style={styles.rewriteColOptimized}>
                                                    <span style={styles.rewriteColLabel}>Đề xuất tối ưu (Công thức {sec.formula_used.toUpperCase()}):</span>
                                                    <p style={{margin: 0, fontSize: '14px', color: '#2e7d32', fontWeight: 500}}>"{sec.rewritten}"</p>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Export Buttons */}
                        <div className="card" style={{padding: 'var(--sp-lg)', marginBottom: 'var(--sp-lg)'}}>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>📄 Xuất CV tối ưu</h3>
                            <div style={{display: 'flex', gap: 'var(--sp-sm)', flexWrap: 'wrap'}}>
                                {['harvard', 'stanford', 'modern'].map(tmpl => (
                                    <button key={tmpl} className="btn-outline" onClick={() => handleDownloadPDF(tmpl)} disabled={downloading}>
                                        {downloading ? '...' : `Tải PDF — ${tmpl.charAt(0).toUpperCase() + tmpl.slice(1)}`}
                                    </button>
                                ))}
                            </div>
                        </div>

                        {/* Action Row */}
                        <div style={{display: 'flex', gap: 'var(--sp-sm)', flexWrap: 'wrap'}}>
                            <button className="btn-primary" onClick={() => navigate('/job-matching', { state: { cvId } })}>
                                So khớp với JD
                            </button>
                            <button className="btn-outline" onClick={() => { setResult(null); setError(''); }}>
                                Phân tích lại
                            </button>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

const getSeverityColor = (severity) => {
    switch (severity) {
        case 'critical': return { bg: '#ffebee', color: '#c62828' };
        case 'high': return { bg: '#fff3e0', color: '#ef6c00' };
        case 'medium': return { bg: '#fffde7', color: '#ef6c00' }; // dark yellow/orange for readability
        case 'low': default: return { bg: '#e8f5e9', color: '#2e7d32' };
    }
};

const getIssueTypeLabel = (type) => {
    switch (type) {
        case 'vague_claim': return 'Tuyên bố mơ hồ';
        case 'buzzword': return 'Từ sáo rỗng (Buzzword)';
        case 'missing_metric': return 'Thiếu chỉ số đo lường';
        case 'weak_verb': return 'Động từ hành động yếu';
        case 'generic_statement': return 'Mô tả chung chung';
        default: return type;
    }
};

const formatMetricLabel = (key) => ({
    profile: 'Hồ sơ',
    experience: 'Kinh nghiệm',
    impact: 'Impact/số liệu',
    skills: 'Kỹ năng',
    structure: 'Cấu trúc ATS',
    target_alignment: 'Khớp vị trí',
}[key] || key.replaceAll('_', ' '));

const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: 'var(--sp-xl) var(--sp-lg)' },
    formRow: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--sp-base)', marginBottom: 'var(--sp-base)' },
    formGroup: { display: 'flex', flexDirection: 'column', gap: 'var(--sp-xs)' },
    label: { fontSize: '14px', fontWeight: 500, color: 'var(--ink)' },
    modeBtn: {
        flex: 1, padding: 'var(--sp-base)', cursor: 'pointer', display: 'flex',
        flexDirection: 'column', gap: 'var(--sp-xxs)', textAlign: 'left',
        transition: 'all var(--transition-fast)', background: 'none',
    },
    spinner: {
        width: '40px', height: '40px', border: '3px solid var(--hairline)',
        borderTop: '3px solid var(--ink)', borderRadius: '50%',
        animation: 'spin 1s linear infinite', margin: '0 auto',
    },
    scoreCircle: { position: 'relative', display: 'inline-flex', alignItems: 'center', justifyContent: 'center' },
    scoreLabel: { position: 'absolute', display: 'flex', flexDirection: 'column', alignItems: 'center' },
    resultGrid: { display: 'flex', flexDirection: 'row', gap: 'var(--sp-xl)', alignItems: 'center', flexWrap: 'wrap' },
    issueItem: { borderLeft: '4px solid var(--hairline-strong)', paddingLeft: 'var(--sp-base)', paddingBottom: 'var(--sp-xs)' },
    originalTextQuote: { margin: '4px 0 0 0', padding: '6px 12px', backgroundColor: 'rgba(0,0,0,0.02)', borderLeft: '3px solid var(--hairline-strong)', fontSize: '13.5px', color: '#555', fontStyle: 'italic' },
    badge: { fontSize: '11px', fontWeight: 600, padding: '3px 8px', borderRadius: '4px', letterSpacing: '0.5px' },
    rewriteItem: { border: '1px solid var(--hairline)', borderRadius: '8px', padding: 'var(--sp-base)' },
    rewriteComparisonGrid: { display: 'flex', flexDirection: 'row', gap: 'var(--sp-base)', marginTop: '8px', flexWrap: 'wrap', width: '100%' },
    rewriteColOriginal: { flex: '1 1 300px', backgroundColor: 'rgba(239, 108, 0, 0.05)', border: '1px dashed rgba(239, 108, 0, 0.2)', padding: '10px', borderRadius: '6px' },
    rewriteColOptimized: { flex: '1 1 300px', backgroundColor: 'rgba(46, 125, 50, 0.05)', border: '1px dashed rgba(46, 125, 50, 0.2)', padding: '10px', borderRadius: '6px' },
    rewriteColLabel: { fontSize: '11px', fontWeight: 600, color: 'var(--muted)', display: 'block', marginBottom: '4px' },
    scorecardGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: 'var(--sp-sm)', marginBottom: 'var(--sp-lg)' },
    scoreMetric: { border: '1px solid var(--hairline)', borderRadius: '8px', padding: 'var(--sp-sm)', background: 'var(--canvas-soft)' },
    metricLabel: { display: 'block', fontSize: '12px', color: 'var(--muted)', marginBottom: '6px' },
    metricValue: { display: 'block', color: 'var(--ink)', marginBottom: '8px' },
    metricBar: { height: '6px', borderRadius: '999px', background: 'var(--hairline)', overflow: 'hidden' },
    metricFill: { height: '100%', borderRadius: '999px', background: 'var(--gradient-mint)' },
    scorecardColumns: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'var(--sp-base)' },
    subTitle: { margin: '0 0 8px', fontSize: '14px', color: 'var(--ink)' },
    chipWrap: { display: 'flex', flexWrap: 'wrap', gap: '6px' },
    goodChip: { fontSize: '12px', borderRadius: '999px', padding: '4px 8px', background: 'rgba(46, 125, 50, 0.1)', color: '#2e7d32' },
    warnChip: { fontSize: '12px', borderRadius: '999px', padding: '4px 8px', background: 'rgba(239, 108, 0, 0.1)', color: '#ef6c00' },
    mutedText: { color: 'var(--muted)', fontSize: '13px' },
    focusList: { margin: 0, paddingLeft: '18px', color: 'var(--body)', fontSize: '14px', lineHeight: 1.7 },
};

export default CVOptimizationPage;
