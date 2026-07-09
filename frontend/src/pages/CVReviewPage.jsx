import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, ErrorState, LoadingState, Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { ProductMockupGraphic } from '../components/Common/Visuals';
import { getCVHistory } from '../api/extraction';

function formatDate(value) {
    if (!value) return '';
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return '';
    return new Intl.DateTimeFormat('vi-VN', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    }).format(date);
}

function scoreTone(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

const CVReviewPage = () => {
    const navigate = useNavigate();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const loadHistory = async () => {
        setLoading(true);
        setError('');
        try {
            const data = await getCVHistory({ limit: 50 });
            setItems(Array.isArray(data) ? data : []);
        } catch (err) {
            setError(err?.message || 'Chưa thể tải lịch sử CV.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadHistory();
    }, []);

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Lịch sử CV"
                    title="Các CV đã tải lên"
                    description="Xem lại CV đã tải lên, trạng thái phân tích và tiếp tục phân tích hoặc so khớp việc làm."
                    visual={<ProductMockupGraphic variant="cv" />}
                    tone="cv"
                    actions={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV mới</button>}
                />

                <Panel title="Lịch sử phân tích" subtitle="Danh sách được lấy từ dữ liệu CV của tài khoản hiện tại.">
                    {loading ? (
                        <LoadingState title="Đang tải lịch sử CV" description="LancerAI đang lấy các CV đã lưu trong tài khoản của bạn." />
                    ) : error ? (
                        <ErrorState
                            title="Chưa thể tải lịch sử CV"
                            description={error}
                            action={<button className="btn-outline" onClick={loadHistory}>Thử lại</button>}
                        />
                    ) : items.length === 0 ? (
                        <EmptyState
                            title="Chưa có CV nào"
                            description="Tải CV lên để bắt đầu phân tích và lưu lịch sử cho những lần dùng sau."
                            action={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>}
                        />
                    ) : (
                        <div className="ui-stack ui-stack--md">
                            {items.map((item) => (
                                <article className="card cv-history-card" key={item.cv_id}>
                                    <div className="cv-history-card__main">
                                        <div>
                                            <div className="ui-cluster">
                                                <StatusBadge tone={item.has_analysis ? 'success' : 'warning'}>
                                                    {item.has_analysis ? 'Đã phân tích' : 'Chưa phân tích'}
                                                </StatusBadge>
                                                {item.audit_score !== null && item.audit_score !== undefined && (
                                                    <StatusBadge tone={scoreTone(Number(item.audit_score))}>
                                                        ATS {Math.round(Number(item.audit_score))}/100
                                                    </StatusBadge>
                                                )}
                                            </div>
                                            <h2 className="title-sm">{item.candidate_name || item.filename || 'CV chưa đặt tên'}</h2>
                                            <p className="caption">
                                                {[item.filename, formatDate(item.created_at)].filter(Boolean).join(' · ')}
                                            </p>
                                        </div>
                                        <div className="cv-history-card__meta">
                                            <span>{Number(item.skills_count || 0)} kỹ năng</span>
                                            <span>{Number(item.experience_count || 0)} kinh nghiệm</span>
                                        </div>
                                    </div>
                                    <div className="ui-cluster">
                                        <button
                                            className="btn-primary"
                                            onClick={() => navigate('/cv-optimization', { state: { cvId: item.cv_id } })}
                                        >
                                            {item.has_analysis ? 'Phân tích lại' : 'Phân tích CV'}
                                        </button>
                                        <button
                                            className="btn-outline"
                                            onClick={() => navigate('/job-matching', { state: { cvId: item.cv_id } })}
                                        >
                                            So khớp JD
                                        </button>
                                    </div>
                                </article>
                            ))}
                        </div>
                    )}
                </Panel>
            </Page>
        </div>
    );
};

export default CVReviewPage;
