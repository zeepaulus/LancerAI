import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { getRecommendations } from '../api/matching';

/**
 * JobRecommendationsPage — Ranked job list based on CV.
 * Calls GET /jobs/recommendations/{cv_id}
 */
const JobRecommendationsPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const cvId = location.state?.cvId || '';

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [jobs, setJobs] = useState([]);

    useEffect(() => {
        if (cvId) fetchJobs();
    }, [cvId]);

    const fetchJobs = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await getRecommendations(cvId, 10);
            setJobs(data || []);
        } catch (err) {
            setError(err.message || 'Không thể tải gợi ý.');
        } finally {
            setLoading(false);
        }
    };

    if (!cvId) {
        return (
            <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
                <Navbar />
                <div style={styles.container}>
                    <div style={{textAlign: 'center', padding: 'var(--sp-section) 0'}}>
                        <p className="title-md">Cần upload CV trước</p>
                        <p style={{color: 'var(--muted)', marginBottom: 'var(--sp-lg)'}}>Hệ thống sẽ gợi ý việc làm dựa trên CV.</p>
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

                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>GỢI Ý VIỆC LÀM</p>
                <h1 className="display-sm" style={{marginBottom: 'var(--sp-xl)'}}>Công việc phù hợp với CV</h1>

                {loading && (
                    <div style={{textAlign: 'center', padding: 'var(--sp-xxl)'}}>
                        <p className="title-sm" style={{color: 'var(--muted)'}}>Đang tìm kiếm...</p>
                    </div>
                )}

                {error && (
                    <div className="card" style={{padding: 'var(--sp-lg)', textAlign: 'center'}}>
                        <p style={{color: 'var(--semantic-error)'}}>{error}</p>
                        <button className="btn-outline" style={{marginTop: 'var(--sp-sm)'}} onClick={fetchJobs}>Thử lại</button>
                    </div>
                )}

                {!loading && !error && jobs.length === 0 && (
                    <div className="card" style={{padding: 'var(--sp-xl)', textAlign: 'center'}}>
                        <p style={{color: 'var(--muted)'}}>Không tìm thấy gợi ý việc làm phù hợp.</p>
                    </div>
                )}

                <div style={styles.jobList}>
                    {jobs.map((job, i) => (
                        <div key={job.job_id || i} className="card" style={styles.jobCard}>
                            <div style={styles.jobMain}>
                                <div style={{flex: 1}}>
                                    <h3 className="title-sm" style={{marginBottom: 'var(--sp-xxs)'}}>{job.title}</h3>
                                    <p style={{color: 'var(--body)', fontSize: '14px'}}>{job.company}</p>
                                    <p style={{color: 'var(--muted)', fontSize: '13px', marginTop: 'var(--sp-xxs)'}}>📍 {job.location}</p>
                                </div>
                                <div style={styles.scoreCol}>
                                    <span style={{fontSize: '24px', fontWeight: 300, fontFamily: 'var(--font-display)', color: 'var(--ink)'}}>{Math.round(job.match_score)}</span>
                                    <span style={{fontSize: '11px', color: 'var(--muted)'}}>% phù hợp</span>
                                </div>
                            </div>
                            {job.url && (
                                <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn-outline" style={{fontSize: '13px', height: '32px', padding: '6px 14px', marginTop: 'var(--sp-sm)', display: 'inline-flex'}}>
                                    Xem chi tiết →
                                </a>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: 'var(--sp-xl) var(--sp-lg)' },
    jobList: { display: 'flex', flexDirection: 'column', gap: 'var(--sp-sm)' },
    jobCard: { padding: 'var(--sp-lg)' },
    jobMain: { display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--sp-lg)' },
    scoreCol: { display: 'flex', flexDirection: 'column', alignItems: 'center', flexShrink: 0 },
};

export default JobRecommendationsPage;
