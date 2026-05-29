import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { matchCV } from '../api/matching';

/**
 * JobMatchingPage — CV ↔ JD scoring.
 * Calls POST /jobs/matches
 */
const JobMatchingPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const cvId = location.state?.cvId || '';

    const [jdSource, setJdSource] = useState('text'); // 'text' | 'url'
    const [jdText, setJdText] = useState('');
    const [jdUrl, setJdUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);

    const handleMatch = async () => {
        if (!cvId) { setError('Không tìm thấy CV. Vui lòng upload CV trước.'); return; }
        if (jdSource === 'text' && !jdText.trim()) { setError('Vui lòng nhập nội dung JD.'); return; }
        if (jdSource === 'url' && !jdUrl.trim()) { setError('Vui lòng nhập URL JD.'); return; }

        setLoading(true);
        setError('');
        try {
            const payload = { cv_id: cvId };
            if (jdSource === 'text') payload.jd_text = jdText;
            else payload.jd_url = jdUrl;
            const data = await matchCV(payload);
            setResult(data);
        } catch (err) {
            setError(err.message || 'So khớp thất bại.');
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score) =>
        score >= 70 ? 'var(--gradient-mint)' : score >= 40 ? 'var(--gradient-peach)' : 'var(--gradient-rose)';

    const getImpactColor = (level) => {
        switch (level) {
            case 'critical': return 'var(--semantic-error)';
            case 'important': return 'var(--gradient-peach)';
            default: return 'var(--surface-strong)';
        }
    };

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <button className="btn-tertiary" style={{marginBottom: 'var(--sp-base)'}} onClick={() => navigate(-1)}>← Quay lại</button>

                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>SO KHỚP</p>
                <h1 className="display-sm" style={{marginBottom: 'var(--sp-xl)'}}>CV ↔ Job Description</h1>

                {/* Input Form */}
                {!result && (
                    <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                        <div style={{display: 'flex', gap: 'var(--sp-sm)', marginBottom: 'var(--sp-base)'}}>
                            <button
                                className={jdSource === 'text' ? 'btn-primary' : 'btn-outline'}
                                style={{fontSize: '13px', height: '34px'}}
                                onClick={() => setJdSource('text')}
                            >Nhập JD thủ công</button>
                            <button
                                className={jdSource === 'url' ? 'btn-primary' : 'btn-outline'}
                                style={{fontSize: '13px', height: '34px'}}
                                onClick={() => setJdSource('url')}
                            >Nhập URL</button>
                        </div>

                        {jdSource === 'text' ? (
                            <textarea
                                className="text-input"
                                style={{height: '200px', resize: 'vertical'}}
                                placeholder="Dán nội dung Job Description tại đây..."
                                value={jdText}
                                onChange={e => setJdText(e.target.value)}
                            />
                        ) : (
                            <input
                                className="text-input"
                                placeholder="https://example.com/job-posting"
                                value={jdUrl}
                                onChange={e => setJdUrl(e.target.value)}
                            />
                        )}

                        {error && <p style={{color: 'var(--semantic-error)', fontSize: '14px', marginTop: 'var(--sp-sm)'}}>{error}</p>}

                        <button className="btn-primary" onClick={handleMatch} disabled={loading} style={{marginTop: 'var(--sp-base)', height: '44px', width: '100%'}}>
                            {loading ? 'Đang phân tích...' : 'So khớp ngay'}
                        </button>
                    </div>
                )}

                {/* Results */}
                {result && (
                    <>
                        {/* Overall Score */}
                        <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)', textAlign: 'center'}}>
                            <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-sm)'}}>ĐIỂM TƯƠNG THÍCH TỔNG THỂ</p>
                            <div style={{fontSize: '56px', fontWeight: 300, fontFamily: 'var(--font-display)', color: 'var(--ink)'}}>
                                {Math.round(result.overall_score)}
                                <span style={{fontSize: '20px', color: 'var(--muted)'}}>/100</span>
                            </div>
                        </div>

                        {/* Sub-scores */}
                        <div style={styles.scoreGrid}>
                            {[
                                { label: 'Keyword Overlap (TF-IDF)', score: result.frequency_score, icon: '🔤' },
                                { label: 'Section Weight', score: result.position_score, icon: '📐' },
                                { label: 'Semantic Similarity', score: result.semantic_score, icon: '🧠' },
                            ].map(s => (
                                <div key={s.label} className="card" style={{padding: 'var(--sp-lg)', textAlign: 'center'}}>
                                    <span style={{fontSize: '24px'}}>{s.icon}</span>
                                    <div style={{fontSize: '28px', fontWeight: 300, fontFamily: 'var(--font-display)', color: 'var(--ink)', margin: 'var(--sp-xs) 0'}}>
                                        {Math.round(s.score)}
                                    </div>
                                    <p style={{fontSize: '12px', color: 'var(--muted)'}}>{s.label}</p>
                                    <div style={{...styles.scoreBar, marginTop: 'var(--sp-sm)'}}>
                                        <div style={{height: '100%', width: `${s.score}%`, backgroundColor: getScoreColor(s.score), borderRadius: 'var(--rounded-pill)', transition: 'width 0.5s ease'}}></div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Feedback */}
                        {result.improvement_feedback && (
                            <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                                <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>💡 Góp ý cải thiện</h3>
                                <p style={{color: 'var(--body)', fontSize: '15px', lineHeight: 1.7, whiteSpace: 'pre-wrap'}}>{result.improvement_feedback}</p>
                            </div>
                        )}

                        {/* Missing Skills */}
                        {result.missing_skills?.length > 0 && (
                            <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                                <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>⚠️ Kỹ năng còn thiếu</h3>
                                <div style={{display: 'flex', flexDirection: 'column', gap: 'var(--sp-sm)'}}>
                                    {result.missing_skills.map((gap, i) => (
                                        <div key={i} style={styles.skillGap}>
                                            <div style={{display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)'}}>
                                                <span className="badge-pill" style={{
                                                    backgroundColor: getImpactColor(gap.impact_level),
                                                    color: gap.impact_level === 'critical' ? '#fff' : 'var(--ink)',
                                                    fontSize: '10px',
                                                }}>{gap.impact_level}</span>
                                                <strong style={{color: 'var(--ink)'}}>{gap.skill_name}</strong>
                                            </div>
                                            {gap.reason && <p style={{color: 'var(--muted)', fontSize: '13px', marginTop: 'var(--sp-xxs)'}}>{gap.reason}</p>}
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* Actions */}
                        <div style={{display: 'flex', gap: 'var(--sp-sm)', flexWrap: 'wrap'}}>
                            <button className="btn-primary" onClick={() => navigate('/cv-optimization', { state: { cvId } })}>
                                Tối ưu CV
                            </button>
                            <button className="btn-outline" onClick={() => { setResult(null); setError(''); }}>
                                So khớp JD khác
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
    scoreGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--sp-sm)', marginBottom: 'var(--sp-lg)' },
    scoreBar: { width: '100%', height: '6px', backgroundColor: 'var(--hairline)', borderRadius: 'var(--rounded-pill)', overflow: 'hidden' },
    skillGap: { padding: 'var(--sp-sm)', backgroundColor: 'var(--canvas-soft)', borderRadius: 'var(--rounded-md)', border: '1px solid var(--hairline-soft)' },
};

export default JobMatchingPage;
