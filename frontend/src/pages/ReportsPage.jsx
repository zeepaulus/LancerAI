import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, MetricCard, Page, PageHero, Panel, SkeletonRows, StatusBadge } from '../components/Common/AppUI';
import { ProductMockupGraphic } from '../components/Common/Visuals';
import { getSessions } from '../api/interview';

function formatDate(isoString) {
    if (!isoString) return 'Chưa có ngày';
    return new Date(isoString).toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

const ReportsPage = () => {
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

    const stats = useMemo(() => {
        const available = sessions.filter((item) => item.status !== 'incomplete');
        const lowConfidence = available.filter((item) => Number(item.overall_confidence || 0) < 60);
        const avg = available.length
            ? Math.round(available.reduce((sum, item) => sum + Number(item.overall_confidence || 0), 0) / available.length)
            : 0;
        return { available: available.length, lowConfidence: lowConfidence.length, avg };
    }, [sessions]);

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Báo cáo"
                    title="Xem lại kết quả phỏng vấn"
                    description="Mở từng báo cáo để xem điểm, transcript, ghi chú đánh giá và phần cần cải thiện."
                    visual={<ProductMockupGraphic variant="report" />}
                    tone="analytics"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/dashboard')}>Dashboard</button>
                            <button className="btn-primary" onClick={() => navigate('/interview')}>Tạo phiên mới</button>
                        </>
                    )}
                />

                {sessions.length > 0 && (
                    <div className="metric-grid ui-section-gap-bottom">
                        <MetricCard label="Báo cáo sẵn sàng" value={stats.available} detail="Phiên đã hoàn tất" tone="success" />
                        <MetricCard label="Điểm trung bình" value={stats.avg ? `${stats.avg}/100` : 'Chưa có'} detail="Tính trên các báo cáo" tone="brand" />
                        <MetricCard label="Điểm thấp" value={stats.lowConfidence} detail="Cần đọc lại transcript" tone={stats.lowConfidence ? 'warning' : 'success'} />
                    </div>
                )}

                <div className="dashboard-grid">
                    <Panel className="span-12" title="Danh sách báo cáo" subtitle="Bấm vào một phiên để xem điểm, transcript và ghi chú cải thiện.">
                        {loading ? (
                            <SkeletonRows rows={6} />
                        ) : sessions.length === 0 ? (
                            <EmptyState
                                visual={<ProductMockupGraphic variant="report" />}
                                title="Chưa có báo cáo"
                                description="Hoàn tất một phiên phỏng vấn để tạo báo cáo có điểm và transcript."
                                action={<button className="btn-primary" onClick={() => navigate('/interview')}>Tạo phiên phỏng vấn</button>}
                            />
                        ) : (
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Báo cáo</th>
                                        <th>Ngày</th>
                                        <th>Trạng thái</th>
                                        <th>Điểm</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {sessions.map((item) => {
                                        const score = Math.round(Number(item.overall_confidence || 0));
                                        const done = item.status !== 'incomplete';
                                        return (
                                            <tr key={item.session_id} onClick={() => navigate('/interview-report', { state: { sessionId: item.session_id } })} className="ui-clickable-row">
                                                <td>
                                                    <strong className="ui-row-title">{item.title || 'Báo cáo phỏng vấn'}</strong>
                                                    {item.focus_area && <div className="caption">{item.focus_area}</div>}
                                                </td>
                                                <td>{formatDate(item.created_at)}</td>
                                                <td><StatusBadge tone={done ? 'success' : 'warning'}>{done ? 'Đã có báo cáo' : 'Đang chờ'}</StatusBadge></td>
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

export default ReportsPage;
