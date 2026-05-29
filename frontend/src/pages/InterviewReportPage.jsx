import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

/**
 * InterviewReportPage — STAR-scored interview report.
 * Receives report data via location.state.
 */
const InterviewReportPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const report = location.state?.report;

    if (!report) {
        return (
            <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
                <Navbar />
                <div style={styles.container}>
                    <div style={{textAlign: 'center', padding: 'var(--sp-section) 0'}}>
                        <p className="title-md">Không tìm thấy báo cáo</p>
                        <p style={{color: 'var(--muted)', marginBottom: 'var(--sp-lg)'}}>Vui lòng hoàn thành một buổi phỏng vấn trước.</p>
                        <button className="btn-primary" onClick={() => navigate('/interview')}>Về trang Phỏng vấn</button>
                    </div>
                </div>
            </div>
        );
    }

    const { session_id, overall_confidence, total_questions, star_scores, logic_issues, improvement_suggestions } = report;

    const avgSTAR = star_scores?.length > 0
        ? star_scores.reduce((acc, s) => ({
            situation: acc.situation + s.situation,
            task: acc.task + s.task,
            action: acc.action + s.action,
            result: acc.result + s.result,
        }), { situation: 0, task: 0, action: 0, result: 0 })
        : null;

    if (avgSTAR && star_scores.length > 0) {
        const n = star_scores.length;
        avgSTAR.situation /= n;
        avgSTAR.task /= n;
        avgSTAR.action /= n;
        avgSTAR.result /= n;
    }

    const getConfidenceColor = (score) =>
        score >= 70 ? 'var(--gradient-mint)' : score >= 40 ? 'var(--gradient-peach)' : 'var(--gradient-rose)';

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <button className="btn-tertiary" style={{marginBottom: 'var(--sp-base)'}} onClick={() => navigate('/interview')}>← Về trang Phỏng vấn</button>

                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>BÁO CÁO PHỎNG VẤN</p>
                <h1 className="display-sm" style={{marginBottom: 'var(--sp-xxs)'}}>Kết quả đánh giá</h1>
                <p style={{color: 'var(--muted)', fontSize: '13px', marginBottom: 'var(--sp-xl)'}}>
                    Session: <code style={{backgroundColor: 'var(--surface-strong)', padding: '2px 6px', borderRadius: 'var(--rounded-xs)', fontSize: '11px'}}>{session_id}</code>
                </p>

                {/* Confidence Score */}
                <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)', textAlign: 'center'}}>
                    <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-sm)'}}>ĐỘ TỰ TIN TỔNG THỂ</p>
                    <div style={{fontSize: '56px', fontWeight: 300, fontFamily: 'var(--font-display)', color: 'var(--ink)'}}>
                        {Math.round(overall_confidence)}
                        <span style={{fontSize: '20px', color: 'var(--muted)'}}>/100</span>
                    </div>
                    <div style={{...styles.progressBar, marginTop: 'var(--sp-sm)', maxWidth: '300px', marginLeft: 'auto', marginRight: 'auto'}}>
                        <div style={{height: '100%', width: `${overall_confidence}%`, backgroundColor: getConfidenceColor(overall_confidence), borderRadius: 'var(--rounded-pill)', transition: 'width 0.5s ease'}}></div>
                    </div>
                    <p style={{color: 'var(--muted)', fontSize: '13px', marginTop: 'var(--sp-sm)'}}>Tổng câu hỏi: {total_questions}</p>
                </div>

                {/* STAR Scores */}
                {avgSTAR && (
                    <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>⭐ Điểm STAR trung bình</h3>
                        <div style={styles.starGrid}>
                            {[
                                { key: 'S', label: 'Situation', score: avgSTAR.situation },
                                { key: 'T', label: 'Task', score: avgSTAR.task },
                                { key: 'A', label: 'Action', score: avgSTAR.action },
                                { key: 'R', label: 'Result', score: avgSTAR.result },
                            ].map(s => (
                                <div key={s.key} style={styles.starItem}>
                                    <div style={styles.starLetter}>{s.key}</div>
                                    <div style={{flex: 1}}>
                                        <div style={{display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--sp-xxs)'}}>
                                            <span style={{fontSize: '14px', color: 'var(--ink)'}}>{s.label}</span>
                                            <span style={{fontSize: '14px', fontWeight: 500, color: 'var(--ink)'}}>{s.score.toFixed(1)}/10</span>
                                        </div>
                                        <div style={styles.progressBar}>
                                            <div style={{height: '100%', width: `${s.score * 10}%`, backgroundColor: getConfidenceColor(s.score * 10), borderRadius: 'var(--rounded-pill)'}}></div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Logic Issues */}
                {logic_issues?.length > 0 && (
                    <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>⚠️ Vấn đề logic phát hiện</h3>
                        <ul style={styles.issueList}>
                            {logic_issues.map((issue, i) => <li key={i}>{issue}</li>)}
                        </ul>
                    </div>
                )}

                {/* Improvement Suggestions */}
                {improvement_suggestions?.length > 0 && (
                    <div className="card" style={{padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)'}}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>💡 Gợi ý cải thiện</h3>
                        <ul style={styles.issueList}>
                            {improvement_suggestions.map((sug, i) => <li key={i}>{sug}</li>)}
                        </ul>
                    </div>
                )}

                <div style={{display: 'flex', gap: 'var(--sp-sm)'}}>
                    <button className="btn-primary" onClick={() => navigate('/interview')}>Phỏng vấn lại</button>
                    <button className="btn-outline" onClick={() => navigate('/dashboard')}>Về Dashboard</button>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: 'var(--sp-xl) var(--sp-lg)' },
    progressBar: { width: '100%', height: '8px', backgroundColor: 'var(--hairline)', borderRadius: 'var(--rounded-pill)', overflow: 'hidden' },
    starGrid: { display: 'flex', flexDirection: 'column', gap: 'var(--sp-base)' },
    starItem: { display: 'flex', alignItems: 'center', gap: 'var(--sp-base)' },
    starLetter: {
        width: '36px', height: '36px', borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)', display: 'flex', alignItems: 'center',
        justifyContent: 'center', fontWeight: 600, fontSize: '14px', color: 'var(--ink)', flexShrink: 0,
    },
    issueList: { paddingLeft: 'var(--sp-lg)', color: 'var(--body)', fontSize: '14px', lineHeight: 1.8 },
};

export default InterviewReportPage;
