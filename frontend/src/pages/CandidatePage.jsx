import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, MetricCard, Page, PageHero, Panel, SkeletonRows, StatusBadge } from '../components/Common/AppUI';
import { CandidateAvatar, CandidateClusterGraphic } from '../components/Common/Visuals';
import { getSessions } from '../api/interview';

function formatDate(isoString) {
    if (!isoString) return 'Chưa có';
    return new Date(isoString).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit' });
}

const CandidatePage = () => {
    const navigate = useNavigate();
    const [sessions, setSessions] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        let active = true;
        setLoading(true);
        getSessions()
            .then((data) => {
                if (active) setSessions(Array.isArray(data) ? data : []);
            })
            .catch(() => {
                if (active) setSessions([]);
            })
            .finally(() => {
                if (active) setLoading(false);
            });
        return () => {
            active = false;
        };
    }, []);

    const candidateRows = useMemo(() => {
        if (!sessions.length) return [];
        return sessions.map((session, index) => {
            const score = Math.round(Number(session.overall_confidence || 0));
            return {
                id: session.session_id,
                name: session.candidate_name || `Phiên luyện tập ${index + 1}`,
                role: session.job_title || session.focus_area || 'Phỏng vấn IT',
                stage: session.status === 'incomplete' ? 'Đang chờ' : score >= 70 ? 'Đạt yêu cầu' : 'Cần xem lại',
                score,
                owner: 'You',
                activity: session.created_at,
            };
        });
    }, [sessions]);

    const needsReview = candidateRows.filter((row) => row.stage === 'Cần xem lại' || row.stage === 'Đang chờ').length;

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Hồ sơ của tôi"
                    title="CV và phỏng vấn"
                    description="Xem lịch sử luyện phỏng vấn, điểm đánh giá và các phiên cần xử lý."
                    visual={<CandidateClusterGraphic />}
                    tone="ai"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/cv-upload')}>Tải CV</button>
                            <button className="btn-primary" onClick={() => navigate('/interview')}>Phỏng vấn</button>
                        </>
                    )}
                />

                {candidateRows.length > 0 && (
                    <div className="metric-grid ui-section-gap-bottom">
                        <MetricCard label="Phiên" value={candidateRows.length} detail="Từ tài khoản hiện tại" tone="brand" />
                        <MetricCard label="Phiên cần xử lý" value={needsReview} detail="Chưa hoàn tất hoặc dưới 70 điểm" tone={needsReview ? 'warning' : 'success'} />
                        <MetricCard label="Phiên đạt yêu cầu" value={candidateRows.filter((row) => row.stage === 'Đạt yêu cầu').length} detail="Điểm từ 70 trở lên" tone="success" />
                    </div>
                )}

                <div className="split-grid">
                    <Panel title="Lịch sử phỏng vấn" subtitle="Bấm vào một phiên để xem báo cáo và transcript.">
                        {loading ? (
                            <SkeletonRows rows={6} />
                        ) : candidateRows.length === 0 ? (
                            <EmptyState
                                visual={<CandidateClusterGraphic />}
                                title="Chưa có phiên luyện tập"
                                description="Tải CV hoặc tạo phiên phỏng vấn để bắt đầu lưu bằng chứng."
                                action={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>}
                            />
                        ) : (
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Phiên</th>
                                        <th>Vai trò</th>
                                        <th>Trạng thái</th>
                                        <th>Điểm</th>
                                        <th>Ngày</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {candidateRows.map((row) => (
                                        <tr key={row.id} onClick={() => navigate('/interview-report', { state: { sessionId: row.id } })} className="ui-clickable-row">
                                            <td>
                                                <div className="ui-cluster">
                                                    <CandidateAvatar name={row.name} size={34} status={row.stage === 'Đạt yêu cầu' ? 'success' : 'warning'} />
                                                    <strong className="ui-row-title">{row.name}</strong>
                                                </div>
                                            </td>
                                            <td>{row.role}</td>
                                            <td><StatusBadge tone={row.stage === 'Đạt yêu cầu' ? 'success' : 'warning'} compact>{row.stage}</StatusBadge></td>
                                            <td className="data-table__score">{row.score ? `${row.score}/100` : 'Đang chờ'}</td>
                                            <td>{formatDate(row.activity)}</td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </Panel>

                    {candidateRows.length > 0 && (
                        <Panel title="Bước nên làm" subtitle="Hành động tiếp theo dựa trên lịch sử luyện tập.">
                            <div className="ui-stack ui-stack--md">
                                <StatusBadge tone={needsReview ? 'warning' : 'ai'} compact>{needsReview ? 'Ưu tiên báo cáo' : 'Tiếp tục luyện tập'}</StatusBadge>
                                <p className="ui-copy">
                                    {needsReview
                                        ? 'Mở phiên có điểm thấp hoặc chưa hoàn tất để đọc transcript, ghi chú và luyện lại phần còn yếu.'
                                        : 'Chưa có phiên yếu. Bạn có thể luyện thêm câu hỏi theo vai trò hoặc tạo phiên phỏng vấn mới.'}
                                </p>
                                <div className="ui-cluster">
                                    <button className="btn-primary" onClick={() => navigate(needsReview ? '/reports' : '/question-bank')}>{needsReview ? 'Mở báo cáo' : 'Mở câu hỏi'}</button>
                                    <button className="btn-outline" onClick={() => navigate('/cv-review')}>Xem CV</button>
                                </div>
                            </div>
                        </Panel>
                    )}
                </div>
            </Page>
        </div>
    );
};

export default CandidatePage;
