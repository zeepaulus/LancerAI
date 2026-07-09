import React, { useEffect, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import {
    EmptyState,
    MatchScoreCard,
    Page,
    PageHero,
    Panel,
    SearchFilterBar,
    SkeletonRows,
    StatusBadge,
} from '../components/Common/AppUI';
import { ProductMockupGraphic } from '../components/Common/Visuals';
import { getRecommendations } from '../api/matching';

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
            setJobs(await getRecommendations(cvId, 10) || []);
        } catch (err) {
            setError(err.message || 'Không thể tải gợi ý việc làm.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Gợi ý việc làm"
                    title="Vai trò phù hợp với CV này"
                    description="Xem danh sách việc làm được xếp hạng, rồi mở so khớp để đọc chi tiết điểm phù hợp."
                    visual={<ProductMockupGraphic variant="match" />}
                    tone="match"
                    actions={<button className="btn-outline" onClick={() => navigate('/job-matching', { state: { cvId } })}>Mở so khớp</button>}
                />

                {!cvId ? (
                    <EmptyState
                        visual={<ProductMockupGraphic variant="match" />}
                        title="Cần tải CV trước"
                        description="Gợi ý việc làm cần dữ liệu CV đã trích xuất để xếp hạng vai trò phù hợp."
                        action={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>}
                    />
                ) : (
                    <div className="split-grid">
                        <Panel title="Việc làm được gợi ý" subtitle="Mở so khớp để xem vì sao một vai trò phù hợp hoặc chưa phù hợp.">
                            <SearchFilterBar>
                                <StatusBadge tone="brand">{jobs.length} gợi ý</StatusBadge>
                                <button className="btn-outline" onClick={fetchJobs} disabled={loading}>Tải lại</button>
                            </SearchFilterBar>

                            <div className="ui-section-gap">
                                {loading ? (
                                    <SkeletonRows rows={6} />
                                ) : error ? (
                                    <EmptyState title="Không thể tải gợi ý" description={error} action={<button className="btn-outline" onClick={fetchJobs}>Thử lại</button>} />
                                ) : jobs.length === 0 ? (
                                    <EmptyState title="Chưa tìm thấy việc làm phù hợp" description="Hãy tối ưu CV hoặc so khớp với một JD cụ thể." />
                                ) : (
                                    <div className="recommendation-list">
                                        {jobs.map((job, index) => {
                                            const score = Math.round(Number(job.match_score || 0));
                                            return (
                                                <article key={job.job_id || index} className="recommendation-card">
                                                    <div className="recommendation-card__header">
                                                        <div>
                                                            <h3 className="title-sm">{job.title || 'Recommended role'}</h3>
                                                            <p className="caption">{[job.company, job.location].filter(Boolean).join(' - ') || 'Company not provided'}</p>
                                                        </div>
                                                        <StatusBadge tone={score >= 70 ? 'success' : score >= 40 ? 'warning' : 'danger'}>{score}% fit</StatusBadge>
                                                    </div>
                                                    <div className="ui-section-gap">
                                                        <MatchScoreCard
                                                            score={score}
                                                            title="Mức phù hợp"
                                                            description="Mở so khớp để so sánh vai trò này với CV chi tiết hơn."
                                                            actions={(
                                                                <>
                                                                    <button className="btn-primary" onClick={() => navigate('/job-matching', { state: { cvId } })}>Xem so khớp</button>
                                                                    {job.url && <a href={job.url} target="_blank" rel="noopener noreferrer" className="btn-outline">Xem tin tuyển dụng</a>}
                                                                </>
                                                            )}
                                                        />
                                                    </div>
                                                </article>
                                            );
                                        })}
                                    </div>
                                )}
                            </div>
                        </Panel>

                        <Panel title="Cách dùng gợi ý" subtitle="Danh sách này chỉ là danh sách rút gọn, không phải quyết định ứng tuyển tự động.">
                            <ProductMockupGraphic variant="match" />
                            <p className="caption ui-section-gap">
                                Chọn một vai trò, xem điểm so khớp với JD, rồi luyện câu hỏi cho các kỹ năng còn thiếu.
                            </p>
                        </Panel>
                    </div>
                )}
            </Page>
        </div>
    );
};

export default JobRecommendationsPage;
