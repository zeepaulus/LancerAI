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
                        {/* Score Card */}
                        <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)', textAlign: 'center'}}>
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
};

export default CVOptimizationPage;
