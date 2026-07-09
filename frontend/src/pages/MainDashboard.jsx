import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, MetricCard, Page, PageHero, Panel, QuickActionCard, SkeletonRows, StatusBadge } from '../components/Common/AppUI';
import { AssetIllustration, FeatureIcon } from '../components/Common/Visuals';
import { getSessions } from '../api/interview';
import * as keys from '../config/storageKeys';

function formatDate(isoString) {
    if (!isoString) return 'Chưa có ngày';
    return new Date(isoString).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function averageScore(items) {
    const scored = items.filter((item) => Number(item.overall_confidence) > 0);
    if (!scored.length) return 0;
    return Math.round(scored.reduce((sum, item) => sum + Number(item.overall_confidence || 0), 0) / scored.length);
}

const MainDashboard = () => {
    const navigate = useNavigate();
    const profile = JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');
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

    const metrics = useMemo(() => {
        const completed = history.filter((item) => item.status !== 'incomplete');
        const pending = history.filter((item) => item.status === 'incomplete' || Number(item.overall_confidence || 0) < 60);
        const avg = averageScore(completed);
        return { completed: completed.length, pending: pending.length, avg };
    }, [history]);

    const featureActions = [
        {
            icon: 'voice',
            visual: 'voice',
            title: 'Phỏng vấn giọng nói',
            description: 'Vào phòng phỏng vấn, bật micro và theo dõi transcript theo thời gian thực. Camera chỉ dùng khi trình duyệt cho phép.',
            status: { label: 'Ưu tiên', tone: 'ai' },
            tone: 'voice',
            primary: <button className="btn-primary" onClick={() => navigate('/interview')}>Bắt đầu</button>,
        },
        {
            icon: 'cv',
            visual: 'cv',
            title: 'Phân tích CV',
            description: 'Tải CV lên để trích xuất kinh nghiệm, kỹ năng và bằng chứng dùng cho phỏng vấn.',
            status: { label: 'CV', tone: 'brand' },
            tone: 'cv',
            primary: <button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>,
        },
        {
            icon: 'match',
            visual: 'match',
            title: 'So khớp việc làm',
            description: 'So sánh CV với mô tả công việc thật và chuẩn bị câu trả lời theo vai trò.',
            status: { label: 'JD', tone: 'success' },
            tone: 'match',
            primary: <button className="btn-primary" onClick={() => navigate('/job-matching')}>So khớp</button>,
        },
        {
            icon: 'questions',
            visual: 'questions',
            title: 'Ngân hàng câu hỏi',
            description: 'Lọc câu hỏi theo vai trò, cấp độ và chủ đề để luyện đúng phần còn yếu.',
            status: { label: 'Luyện tập', tone: 'questions' },
            tone: 'questions',
            primary: <button className="btn-primary" onClick={() => navigate('/question-bank')}>Mở câu hỏi</button>,
        },
    ];

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Dashboard"
                    title={`Xin chào, ${profile.display_name || 'bạn'}`}
                    description="Theo dõi CV, phiên phỏng vấn và các báo cáo cần xử lý trước khi luyện tiếp."
                    visual={<AssetIllustration name="journey" />}
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/cv-upload')}>Tải CV</button>
                            <button className="btn-primary" onClick={() => navigate('/interview')}>Tạo phiên phỏng vấn</button>
                        </>
                    )}
                />

                {historyLoading ? (
                    <div className="ui-section-gap-bottom">
                        <SkeletonRows rows={1} />
                    </div>
                ) : history.length > 0 && (
                    <div className="metric-grid ui-section-gap-bottom">
                        <MetricCard label="Đã đánh giá" value={metrics.completed} detail="Phiên có báo cáo" tone="success" />
                        <MetricCard label="Điểm trung bình" value={metrics.avg ? `${metrics.avg}/100` : 'Chưa có'} detail="Tính trên phiên đã hoàn tất" tone="brand" />
                        <MetricCard label="Phiên cần xử lý" value={metrics.pending} detail="Chưa hoàn tất hoặc dưới 60 điểm" tone={metrics.pending ? 'warning' : 'neutral'} />
                    </div>
                )}

                <div className="quick-action-grid" aria-label="Tác vụ chính của LancerAI">
                    {featureActions.map((feature) => (
                        <QuickActionCard
                            key={feature.title}
                            icon={<FeatureIcon type={feature.icon} />}
                            visual={<AssetIllustration name={feature.visual} compact />}
                            title={feature.title}
                            description={feature.description}
                            meta={feature.status}
                            tone={feature.tone}
                            action={(
                                <>
                                    {feature.primary}
                                    {feature.secondary}
                                </>
                            )}
                        />
                    ))}
                </div>

                {!historyLoading && history.length > 0 && (
                    <section className="dashboard-priority-strip" aria-label="Bước nên làm">
                        <FeatureIcon type={metrics.pending ? 'report' : 'questions'} />
                    <div className="dashboard-priority-strip__copy">
                        <div className="ui-cluster">
                            <StatusBadge tone={metrics.pending ? 'warning' : 'ai'} compact>
                                Bước nên làm
                            </StatusBadge>
                            <strong>{metrics.pending ? 'Mở báo cáo của phiên yếu nhất' : 'Luyện thêm câu hỏi theo vai trò'}</strong>
                        </div>
                        <p>
                            {metrics.pending
                                ? 'Đọc transcript và ghi chú cải thiện trước khi tạo phiên phỏng vấn mới.'
                                : 'Chọn vai trò, cấp độ và chủ đề để luyện đúng phần còn thiếu.'}
                        </p>
                    </div>
                    <button className="btn-outline" onClick={() => navigate(metrics.pending ? '/candidate' : '/question-bank')}>
                        {metrics.pending ? 'Xem phiên cần xử lý' : 'Mở ngân hàng câu hỏi'}
                    </button>
                    </section>
                )}

                <div className="dashboard-grid">
                    <Panel className="span-12" title="Phiên phỏng vấn gần đây" subtitle="Bấm vào một phiên để xem điểm, transcript và ghi chú cải thiện.">
                        {historyLoading ? (
                            <SkeletonRows rows={5} />
                        ) : history.length === 0 ? (
                            <EmptyState
                                title="Chưa có phiên phỏng vấn"
                                description="Tạo một phiên phỏng vấn để bắt đầu lưu transcript và đánh giá."
                                action={<button className="btn-primary" onClick={() => navigate('/interview')}>Tạo phiên</button>}
                            />
                        ) : (
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Phiên</th>
                                        <th>Ngày</th>
                                        <th>Trạng thái</th>
                                        <th>Điểm</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {history.slice(0, 7).map((item) => {
                                        const score = Math.round(Number(item.overall_confidence || 0));
                                        return (
                                            <tr key={item.session_id} onClick={() => navigate('/interview-report', { state: { sessionId: item.session_id } })} className="ui-clickable-row">
                                                <td>
                                                    <strong className="ui-row-title">{item.title || 'Phiên phỏng vấn'}</strong>
                                                    {item.focus_area && <div className="caption">{item.focus_area}</div>}
                                                </td>
                                                <td>{formatDate(item.created_at)}</td>
                                                <td>
                                                    <StatusBadge tone={item.status === 'incomplete' ? 'warning' : 'success'} compact>
                                                        {item.status === 'incomplete' ? 'Đang chờ' : 'Đã đánh giá'}
                                                    </StatusBadge>
                                                </td>
                                                <td>{score ? `${score}/100` : 'Đang chờ'}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        )}
                    </Panel>

                </div>
            </Page>
        </div>
    );
};

export default MainDashboard;
