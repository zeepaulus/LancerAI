import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { Alert, EmptyState, MetricCard, Page, PageHero, Panel, ScoreBar, StatusBadge } from '../components/Common/AppUI';
import { AssetIllustration, FeatureIcon } from '../components/Common/Visuals';
import { getJobListings, matchCV } from '../api/matching';
import { IT_ROLES } from '../data/questionBank';

function scoreTone(score) {
    if (score >= 70) return 'success';
    if (score >= 40) return 'warning';
    return 'danger';
}

function jobId(job) {
    return job?.job_id || job?.id || job?.source_url || job?.title || '';
}

function jobSkills(job) {
    return job?.skills || job?.requirements?.skills || job?.requirements?.tags || job?.tags || [];
}

function jobRole(job) {
    return job.role || inferRoleFromJob(job);
}

function inferRoleFromJob(job) {
    const text = `${job?.title || ''} ${job?.description || ''}`.toLowerCase();
    if (text.includes('frontend') || text.includes('react')) return 'Frontend Developer';
    if (text.includes('backend') || text.includes('fastapi') || text.includes('node')) return 'Backend Developer';
    if (text.includes('devops') || text.includes('docker') || text.includes('kubernetes')) return 'DevOps Engineer';
    if (text.includes('data analyst')) return 'Data Analyst';
    if (text.includes('data scientist') || text.includes('machine learning')) return 'Data Scientist';
    if (text.includes('qa') || text.includes('tester')) return 'QA Engineer';
    return 'Fullstack Developer';
}

function jobToText(job) {
    if (!job) return '';
    const requirements = job.requirements?.raw_requirements
        || (Array.isArray(job.requirements) ? job.requirements.join(', ') : JSON.stringify(job.requirements || {}));
    return [
        `${job.title || 'Việc làm đã chọn'} - ${job.company || 'Chưa có tên công ty'}`,
        `Địa điểm: ${job.location || 'Chưa cung cấp'}`,
        `Lương: ${job.salary_range || 'Chưa cung cấp'}`,
        job.description,
        `Yêu cầu: ${requirements}`,
        `Kỹ năng: ${jobSkills(job).join(', ')}`,
        job.source_url ? `Nguồn: ${job.source_url}` : '',
    ].filter(Boolean).join('\n\n');
}

const JobMatchingPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const cvId = location.state?.cvId || '';

    const [jobs, setJobs] = useState([]);
    const [jobsLoading, setJobsLoading] = useState(false);
    const [jobsError, setJobsError] = useState('');
    const [jobQuery, setJobQuery] = useState('');
    const [roleFilter, setRoleFilter] = useState('All');
    const [selectedJobId, setSelectedJobId] = useState('');
    const [manualMode, setManualMode] = useState(false);
    const [jdText, setJdText] = useState('');
    const [jdUrl, setJdUrl] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);

    useEffect(() => {
        let active = true;
        async function loadJobs() {
            setJobsLoading(true);
            setJobsError('');
            try {
                const data = await getJobListings({ source: 'topcv', limit: 60 });
                const nextJobs = Array.isArray(data) ? data : [];
                if (!active) return;
                setJobs(nextJobs);
                setSelectedJobId(nextJobs.length ? jobId(nextJobs[0]) : '');
                if (!nextJobs.length) setManualMode(true);
            } catch (err) {
                if (!active) return;
                setJobs([]);
                setJobsError('Hiện chưa tải được danh sách việc làm từ TopCV.');
                setSelectedJobId('');
                setManualMode(true);
            } finally {
                if (active) setJobsLoading(false);
            }
        }
        loadJobs();
        return () => {
            active = false;
        };
    }, []);

    const selectedJob = selectedJobId ? jobs.find((job) => jobId(job) === selectedJobId) || null : jobs[0] || null;

    useEffect(() => {
        if (selectedJob && !manualMode) setJdText(jobToText(selectedJob));
    }, [manualMode, selectedJob]);

    const filteredJobs = useMemo(() => {
        const query = jobQuery.trim().toLowerCase();
        return jobs.filter((job) => {
            const matchesRole = roleFilter === 'All' || jobRole(job) === roleFilter;
            const searchable = [
                job.title,
                job.company,
                job.location,
                job.description,
                ...jobSkills(job),
            ].join(' ').toLowerCase();
            return matchesRole && (!query || searchable.includes(query));
        });
    }, [jobQuery, jobs, roleFilter]);

    const handleSelectJob = (job) => {
        if (!job) return;
        setSelectedJobId(jobId(job));
        setManualMode(false);
        setResult(null);
        setError('');
        setJdText(jobToText(job));
    };

    const handleMatch = async () => {
        if (!cvId) {
            setError('Vui lòng tải và phân tích CV trước khi so khớp.');
            return;
        }
        if (!manualMode && !selectedJob) {
            setError('Vui lòng chọn một việc làm hoặc chuyển sang chế độ dán JD.');
            return;
        }
        if (manualMode && !jdText.trim() && !jdUrl.trim()) {
            setError('Vui lòng dán mô tả công việc hoặc nhập URL JD công khai trước khi so khớp.');
            return;
        }

        setLoading(true);
        setError('');
        try {
            const payload = { cv_id: cvId };
            if (manualMode && jdUrl.trim() && !jdText.trim()) payload.jd_url = jdUrl.trim();
            else payload.jd_text = jdText || jobToText(selectedJob);
            setResult(await matchCV(payload));
        } catch (err) {
            setError('Chưa thể hoàn tất so khớp. Vui lòng kiểm tra nội dung JD và thử lại.');
        } finally {
            setLoading(false);
        }
    };

    const prepareInterview = () => {
        if (!selectedJob) return;
        navigate('/interview', {
            state: {
                jobPreset: {
                    title: selectedJob.title,
                    role: jobRole(selectedJob),
                    level: selectedJob.experience_level,
                    jdText: jdText || jobToText(selectedJob),
                    focusArea: `Chuẩn bị cho ${selectedJob.title}. Tập trung vào kỹ năng còn thiếu, độ phù hợp vai trò và bằng chứng dự án.`,
                },
            },
        });
    };

    const score = Math.round(Number(result?.overall_score || 0));

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="So khớp việc làm"
                    title="So sánh CV với mô tả công việc IT"
                    description="Chọn một việc làm, kiểm tra nội dung JD, rồi xem CV đang phù hợp ở điểm nào và thiếu gì."
                    visual={<AssetIllustration name="match" />}
                    tone="match"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/cv-upload')}>Tải CV</button>
                            <button className="btn-outline" onClick={() => navigate('/job-recommendations', { state: { cvId } })} disabled={!cvId}>Gợi ý việc làm</button>
                            <button className="btn-primary" onClick={handleMatch} disabled={loading || !cvId}>{loading ? 'Đang phân tích...' : 'So khớp ngay'}</button>
                        </>
                    )}
                />

                {!cvId && (
                    <div className="ui-section-gap-bottom">
                        <EmptyState
                            visual={<AssetIllustration name="cv" compact />}
                            title="Chưa chọn CV"
                            description="So khớp việc làm cần CV đã được trích xuất. Hãy tải CV hoặc mở từ kết quả phân tích CV."
                            action={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>}
                        />
                    </div>
                )}

                {jobsError && (
                    <div className="ui-section-gap-bottom">
                        <Alert tone="warning" title="Chưa tải được danh sách việc làm">
                            {jobsError}
                        </Alert>
                    </div>
                )}

                <div className="job-match-workspace">
                    <Panel title="Danh sách việc làm" subtitle="Chọn một vai trò, kiểm tra JD, rồi chạy so khớp với CV.">
                        <div className="job-filter-bar">
                            <input
                                className="text-input"
                                placeholder="Tìm React, SQL, Docker, công ty..."
                                value={jobQuery}
                                onChange={(event) => setJobQuery(event.target.value)}
                            />
                            <select className="text-input" value={roleFilter} onChange={(event) => setRoleFilter(event.target.value)}>
                                {['All', ...IT_ROLES].map((role) => <option key={role} value={role}>{role === 'All' ? 'Tất cả vai trò' : role}</option>)}
                            </select>
                            <button className="btn-outline" type="button" onClick={() => { setJobQuery(''); setRoleFilter('All'); }}>Xóa lọc</button>
                        </div>

                        <div className="job-collection-list">
                            {jobsLoading ? (
                                <StatusBadge tone="ai">Đang tải việc làm...</StatusBadge>
                            ) : filteredJobs.length === 0 ? (
                                <EmptyState title="Không tìm thấy việc làm" description="Thử từ khóa khác, xóa bộ lọc hoặc dán JD thật ở phần nhập liệu." />
                            ) : filteredJobs.map((job, index) => (
                                <button
                                    key={jobId(job) || `${job.title}-${index}`}
                                    type="button"
                                    className={`card ui-card-button ${jobId(selectedJob) === jobId(job) ? 'is-active' : ''}`}
                                    onClick={() => handleSelectJob(job)}
                                >
                                    <div>
                                        <strong>{job.title || 'Chưa có tiêu đề'}</strong>
                                        <p className="caption">{[job.company, job.location].filter(Boolean).join(' - ') || 'Chưa có tên công ty'}</p>
                                    </div>
                                    <div className="ui-cluster">
                                        <StatusBadge tone="success">TopCV</StatusBadge>
                                        {job.experience_level && <StatusBadge tone="ai">{job.experience_level}</StatusBadge>}
                                    </div>
                                </button>
                            ))}
                        </div>
                    </Panel>

                    <Panel title="Chi tiết việc làm đã chọn" subtitle="Kiểm tra nguồn, kỹ năng và nội dung JD trước khi so khớp.">
                        {selectedJob ? (
                            <div className="ui-stack ui-stack--md">
                                <div className="job-detail-snapshot" aria-hidden="true">
                                    <span className="job-detail-snapshot__mark"><FeatureIcon type="match" /></span>
                                    <div>
                                        <span />
                                        <span />
                                        <span />
                                    </div>
                                </div>
                                <div>
                                    <h2 className="title-sm">{selectedJob.title || 'Việc làm đã chọn'}</h2>
                                    <p className="caption">{[selectedJob.company, selectedJob.location, selectedJob.salary_range].filter(Boolean).join(' - ')}</p>
                                </div>
                                <div className="ui-cluster">
                                    <StatusBadge tone="success">Tin từ TopCV</StatusBadge>
                                    {selectedJob.crawled_at && <StatusBadge>{new Date(selectedJob.crawled_at).toLocaleDateString()}</StatusBadge>}
                                </div>
                                <p className="ui-copy">{selectedJob.description}</p>
                                <div className="ui-cluster">
                                    {jobSkills(selectedJob).slice(0, 10).map((tag) => <StatusBadge key={tag}>{tag}</StatusBadge>)}
                                </div>
                                {selectedJob.source_url && <a className="btn-outline" href={selectedJob.source_url} target="_blank" rel="noopener noreferrer">Xem nguồn</a>}
                            </div>
                        ) : (
                            <EmptyState title="Chưa chọn việc làm" description="Chọn một việc làm trong danh sách hoặc dán JD thật ở bên dưới." />
                        )}
                    </Panel>

                    <Panel title="Nguồn JD dùng để so khớp" subtitle="Mặc định dùng việc làm đã chọn. Có thể dán JD hoặc URL cho một lần kiểm tra riêng.">
                        <div className="ui-cluster">
                            <button className={!manualMode ? 'btn-primary' : 'btn-outline'} onClick={() => setManualMode(false)}>Việc làm đã chọn</button>
                            <button className={manualMode ? 'btn-primary' : 'btn-outline'} onClick={() => setManualMode(true)}>Dán JD / URL</button>
                        </div>

                        <div className="ui-stack ui-stack--md ui-section-gap">
                            {manualMode && (
                                <input
                                    className="text-input"
                                    placeholder="URL JD công khai nếu có"
                                    value={jdUrl}
                                    onChange={(event) => setJdUrl(event.target.value)}
                                />
                            )}
                            <textarea
                                className="text-input ui-textarea-tall"
                                placeholder="Mô tả công việc đã chọn sẽ hiển thị ở đây..."
                                value={jdText}
                                onChange={(event) => { setJdText(event.target.value); setManualMode(true); }}
                            />
                            {error && <div className="ui-error-box" role="alert">{error}</div>}
                            <button className="btn-primary" onClick={handleMatch} disabled={loading || !cvId}>
                                {loading ? 'Đang so khớp...' : 'Chạy so khớp'}
                            </button>
                        </div>
                    </Panel>
                </div>

                {result && (
                    <div className="ui-section-gap">
                        <div className="metric-grid ui-section-gap-bottom">
                            <MetricCard label="Điểm phù hợp" value={`${score}/100`} detail="Tổng hợp từ CV và JD" tone={scoreTone(score)} />
                            <MetricCard label="Trùng yêu cầu" value={`${Math.round(result.frequency_score || 0)}/100`} detail="Từ khóa và kỹ năng trong JD" tone="brand" />
                            <MetricCard label="Kinh nghiệm phù hợp" value={`${Math.round(result.position_score || 0)}/100`} detail="Bằng chứng liên quan trong CV" tone="ai" />
                            <MetricCard label="Mức phù hợp vai trò" value={`${Math.round(result.semantic_score || 0)}/100`} detail="So sánh nội dung CV với JD" tone="success" />
                        </div>

                        <div className="dashboard-grid">
                            <Panel className="span-5" title="Thành phần điểm" subtitle="Xem phần nào kéo điểm lên hoặc xuống trước khi chọn bước tiếp theo.">
                                {[
                                    ['Trùng yêu cầu', result.frequency_score || 0],
                                    ['Kinh nghiệm phù hợp', result.position_score || 0],
                                    ['Mức phù hợp vai trò', result.semantic_score || 0],
                                ].map(([label, value]) => (
                                    <div key={label} className="ui-section-gap-bottom">
                                        <div className="ui-spread ui-row-gap-bottom">
                                            <span>{label}</span>
                                            <StatusBadge tone={scoreTone(value)}>{Math.round(value)}/100</StatusBadge>
                                        </div>
                                        <ScoreBar value={value} tone="auto" />
                                    </div>
                                ))}
                            </Panel>

                            <Panel className="span-7" title="Bước nên làm" subtitle="Dùng phần này như gợi ý tham khảo trước khi chỉnh CV hoặc luyện phỏng vấn.">
                                {result.improvement_feedback ? <p className="ui-copy">{result.improvement_feedback}</p> : <p className="caption">Dịch vụ so khớp chưa trả về nhận xét bằng văn bản.</p>}
                                <div className="ui-cluster ui-section-gap">
                                    <button className="btn-primary" onClick={() => navigate('/cv-optimization', { state: { cvId } })}>Xem gợi ý cải thiện CV</button>
                                    <button className="btn-outline" onClick={prepareInterview}>Luyện phỏng vấn</button>
                                </div>
                            </Panel>

                            <Panel className="span-12" title="Kỹ năng nên bổ sung" subtitle="Dùng danh sách này để bổ sung ví dụ trong CV hoặc chuẩn bị câu chuyện dự án.">
                                {result.missing_skills?.length > 0 ? (
                                    <table className="data-table">
                                        <thead>
                                            <tr>
                                                <th>Kỹ năng</th>
                                                <th>Mức ảnh hưởng</th>
                                                <th>Giải thích</th>
                                                <th>Bước nên làm</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {result.missing_skills.map((gap, index) => (
                                                <tr key={`${gap.skill_name}-${index}`}>
                                                    <td><strong className="ui-row-title">{gap.skill_name}</strong></td>
                                                    <td><StatusBadge tone={gap.impact_level === 'critical' ? 'danger' : 'warning'}>{gap.impact_level || 'cần xem'}</StatusBadge></td>
                                                    <td>{gap.reason || 'Chưa có giải thích chi tiết.'}</td>
                                                    <td>Bổ sung ví dụ trong CV hoặc chuẩn bị một câu chuyện dự án liên quan.</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                ) : (
                                    <EmptyState title="Chưa có kỹ năng thiếu nổi bật" description="Vẫn nên đọc phần giải thích và chuẩn bị bằng chứng cho yêu cầu chính của JD." />
                                )}
                            </Panel>
                        </div>
                    </div>
                )}
            </Page>
        </div>
    );
};

export default JobMatchingPage;
