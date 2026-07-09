import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, MetricCard, Page, PageHero, Panel, SkeletonRows, StatusBadge } from '../components/Common/AppUI';
import { CandidateAvatar, ProductMockupGraphic } from '../components/Common/Visuals';
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

const ProfilePage = () => {
    const navigate = useNavigate();
    const profile = JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');
    const displayName = profile.display_name || profile.email || 'Người dùng';
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

    const completedSessions = useMemo(() => sessions.filter((item) => item.status !== 'incomplete'), [sessions]);
    const avgScore = averageScore(completedSessions);

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Hồ sơ"
                    title="Hồ sơ ứng viên"
                    description="Tổng hợp phiên phỏng vấn, lịch sử CV, trạng thái so khớp việc làm và điểm báo cáo."
                    visual={<ProductMockupGraphic variant="candidate" />}
                    tone="ai"
                    actions={<StatusBadge tone="ai">Hồ sơ cá nhân</StatusBadge>}
                />

                {sessions.length > 0 && (
                    <div className="metric-grid ui-section-gap-bottom">
                        <MetricCard label="Phiên phỏng vấn" value={sessions.length} detail="Dữ liệu từ tài khoản hiện tại" tone="brand" />
                        <MetricCard label="Đã có báo cáo" value={completedSessions.length} detail="Phiên đã hoàn tất" tone="success" />
                        <MetricCard label="Điểm trung bình" value={avgScore ? `${avgScore}/100` : 'Chưa có'} detail="Tính trên phiên đã đánh giá" tone="ai" />
                    </div>
                )}

                <div className="profile-summary-grid">
                    <Panel title="Tài khoản" subtitle="Thông tin thật từ tài khoản đang đăng nhập.">
                        <div className="team-card">
                            <CandidateAvatar name={displayName} size={72} status="success" />
                            <div className="team-card__body">
                                <h2 className="title-md">{displayName}</h2>
                                {profile.email && <p className="caption">{profile.email}</p>}
                                {!profile.display_name && <p className="caption">Bạn có thể cập nhật tên hiển thị trong Cài đặt.</p>}
                            </div>
                        </div>
                    </Panel>

                    <Panel title="Hành động nhanh" subtitle="Các thao tác thường dùng trong hồ sơ.">
                        <div className="review-list">
                            {[
                                ['Tải hoặc cập nhật CV', 'Chuẩn bị dữ liệu cho phân tích và so khớp', 'cv', '/cv-upload'],
                                ['Tạo phiên phỏng vấn', 'Luyện theo vai trò mục tiêu', 'voice', '/interview'],
                                ['Xem báo cáo', 'Đọc điểm và transcript của phiên đã hoàn tất', 'analytics', '/reports'],
                            ].map(([label, description, tone, path]) => (
                                <button type="button" className="review-card ui-card-button" key={label} onClick={() => navigate(path)}>
                                    <div className="review-card__header">
                                        <strong>{label}</strong>
                                        <StatusBadge tone={tone}>Mở</StatusBadge>
                                    </div>
                                    <p className="caption">{description}</p>
                                </button>
                            ))}
                        </div>
                    </Panel>
                </div>

                <div className="dashboard-grid ui-section-gap">
                    <Panel className="span-12" title="Lịch sử phỏng vấn" subtitle="Dữ liệu được tải theo tài khoản đang đăng nhập.">
                        {loading ? (
                            <SkeletonRows rows={5} />
                        ) : sessions.length ? (
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
                                    {sessions.map((item) => {
                                        const score = Math.round(Number(item.overall_confidence || 0));
                                        const done = item.status !== 'incomplete';
                                        return (
                                            <tr key={item.session_id}>
                                                <td><strong>{item.title || 'Phiên phỏng vấn'}</strong></td>
                                                <td>{formatDate(item.created_at)}</td>
                                                <td><StatusBadge tone={done ? 'success' : 'warning'}>{done ? 'Đã đánh giá' : 'Chưa hoàn tất'}</StatusBadge></td>
                                                <td>{score ? <StatusBadge tone={score >= 70 ? 'success' : score >= 50 ? 'warning' : 'danger'}>{score}/100</StatusBadge> : 'Chưa có'}</td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        ) : (
                            <EmptyState title="Chưa có phiên phỏng vấn" description="Tạo một phiên phỏng vấn để bắt đầu lưu lịch sử luyện tập." />
                        )}
                    </Panel>
                </div>
            </Page>
        </div>
    );
};

export default ProfilePage;
