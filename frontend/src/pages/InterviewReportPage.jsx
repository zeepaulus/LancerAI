import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import {
    AIResponsePanel,
    Alert,
    EmptyState,
    MetricCard,
    Page,
    PageHero,
    Panel,
    ProgressCard,
    ScoreBar,
    SkeletonRows,
    StatusBadge,
} from '../components/Common/AppUI';
import { EvaluationScoreGraphic } from '../components/Common/Visuals';
import { getReport } from '../api/interview';

const REPORT_RETRY_DELAYS_MS = [500, 900, 1400, 2000, 2800];

function scoreTone(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

function severityTone(severity) {
    if (severity === 'high' || severity === 'critical') return 'danger';
    if (severity === 'medium') return 'warning';
    return 'neutral';
}

function speakerLabel(role) {
    if (role === 'candidate') return 'Ứng viên';
    if (role === 'interviewer') return 'Người phỏng vấn AI';
    return 'Hệ thống';
}

const InterviewReportPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const initialReport = location.state?.report || null;
    const sessionIdFromState = location.state?.sessionId || location.state?.viewReportId || initialReport?.session_id || '';

    const [report, setReport] = useState(initialReport);
    const [loading, setLoading] = useState(Boolean(!initialReport && sessionIdFromState));
    const [error, setError] = useState('');

    useEffect(() => {
        if (report || !sessionIdFromState) return;

        let mounted = true;
        let timeoutId = null;

        const wait = (delay) => new Promise((resolve) => {
            timeoutId = window.setTimeout(resolve, delay);
        });

        async function loadReport() {
            setLoading(true);
            let lastError = null;

            for (let attempt = 0; attempt <= REPORT_RETRY_DELAYS_MS.length; attempt += 1) {
                if (!mounted) return;
                try {
                    const data = await getReport(sessionIdFromState);
                    if (!mounted) return;
                    setReport(data);
                    setError('');
                    setLoading(false);
                    return;
                } catch (err) {
                    lastError = err;
                    if (attempt < REPORT_RETRY_DELAYS_MS.length) {
                        await wait(REPORT_RETRY_DELAYS_MS[attempt]);
                    }
                }
            }

            if (!mounted) return;
            setError(lastError?.message || 'Báo cáo chưa sẵn sàng. Vui lòng thử lại sau vài giây.');
            setLoading(false);
        }

        loadReport();

        return () => {
            mounted = false;
            if (timeoutId) window.clearTimeout(timeoutId);
        };
    }, [report, sessionIdFromState]);

    const avgSTAR = useMemo(() => {
        const scores = report?.star_scores || [];
        if (scores.length === 0) return null;

        const total = scores.reduce((acc, item) => ({
            situation: acc.situation + Number(item.situation || 0),
            task: acc.task + Number(item.task || 0),
            action: acc.action + Number(item.action || 0),
            result: acc.result + Number(item.result || 0),
        }), { situation: 0, task: 0, action: 0, result: 0 });

        return Object.fromEntries(Object.entries(total).map(([key, value]) => [key, value / scores.length]));
    }, [report]);

    if (loading) {
        return (
            <div className="app-screen">
                <Navbar />
                <Page narrow>
                    <PageHero
                        kicker="Báo cáo phỏng vấn"
                        title="Đang chuẩn bị báo cáo"
                        description="Đang tải điểm đánh giá, ghi nhận trong phiên, transcript và gợi ý cải thiện."
                        visual={<EvaluationScoreGraphic />}
                        tone="analytics"
                    />
                    <Panel title="Đang tải báo cáo" subtitle="Báo cáo sẽ hiển thị ngay khi sẵn sàng.">
                        <SkeletonRows rows={6} />
                    </Panel>
                </Page>
            </div>
        );
    }

    if (!report) {
        return (
            <div className="app-screen">
                <Navbar />
                <Page narrow>
                    {error && (
                        <div className="ui-section-gap-bottom">
                            <Alert tone="danger" title="Không tải được báo cáo">{error}</Alert>
                        </div>
                    )}
                    <EmptyState
                        visual={<EvaluationScoreGraphic />}
                        title="Chưa có báo cáo phỏng vấn"
                        description="Hãy hoàn tất một phiên phỏng vấn giọng nói trước, sau đó quay lại để xem đánh giá và transcript."
                        action={<button className="btn-primary" onClick={() => navigate('/interview')}>Bắt đầu phỏng vấn</button>}
                    />
                </Page>
            </div>
        );
    }

    const {
        session_id,
        overall_confidence = 0,
        total_questions = 0,
        logic_issues = [],
        improvement_suggestions = [],
        behavior_score = 100,
        behavior_observations = [],
        transcript = [],
        scorecard = {},
    } = report;

    const roundedConfidence = Math.round(Number(overall_confidence || 0));
    const roundedBehavior = Math.round(Number(behavior_score || 0));

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                        kicker="Báo cáo phỏng vấn"
                        title="Đánh giá dựa trên bằng chứng"
                    description="Xem điểm tổng quan, nhận xét, ghi nhận trong buổi phỏng vấn và transcript trước khi đưa ra quyết định."
                    visual={<EvaluationScoreGraphic score={roundedConfidence} />}
                    tone="analytics"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/interview')}>Phỏng vấn lại</button>
                            <button className="btn-primary" onClick={() => navigate('/dashboard')}>Dashboard</button>
                        </>
                    )}
                >
                    <div className="hero-progress-grid">
                        <ProgressCard label="Điểm tổng quan" value={roundedConfidence} detail="Điểm tổng hợp dựa trên STAR, CV-JD Fit và transcript." tone={scoreTone(roundedConfidence)} />
                        <ProgressCard label="Điều kiện buổi phỏng vấn" value={roundedBehavior} detail="Ghi nhận từ việc rời tab, màn hình phụ, ánh sáng và camera." tone={scoreTone(roundedBehavior)} />
                    </div>
                </PageHero>

                {error && (
                    <div className="ui-section-gap-bottom">
                        <Alert tone="warning" title="Báo cáo có cảnh báo">{error}</Alert>
                    </div>
                )}

                <div className="metric-grid ui-section-gap-bottom">
                    <MetricCard label="Điểm tổng quan" value={`${roundedConfidence}/100`} detail="Tổng hợp từ STAR, CV-JD Fit và transcript" tone={scoreTone(roundedConfidence)} />
                    <MetricCard label="Số lượt hỏi" value={total_questions || transcript.filter(t => t.role === 'candidate').length || 0} detail="Câu trả lời được đánh giá" tone="brand" />
                    <MetricCard label="Điều kiện phiên" value={`${roundedBehavior}/100`} detail="Rời tab · màn hình phụ · camera" tone={scoreTone(roundedBehavior)} />
                    <MetricCard label="Ghi chú" value={logic_issues.length + improvement_suggestions.length} detail="Vấn đề và gợi ý" tone="ai" />
                </div>

                <div className="dashboard-grid">
                    <div className="span-12">
                        <AIResponsePanel
                            title="Tóm tắt đánh giá"
                            subtitle={`Phiên ${session_id || 'hiện tại'}, nên xem lại trước khi ra quyết định`}
                            footer={<StatusBadge tone={scoreTone(roundedConfidence)} compact>{roundedConfidence >= 80 ? 'Tín hiệu tốt' : roundedConfidence >= 60 ? 'Cần xem lại' : 'Rủi ro cao'}</StatusBadge>}
                        >
                            {scorecard?.headline && (
                                <h3 className="title-md ui-row-gap-bottom" style={{ color: 'var(--color-brand-primary)', fontStyle: 'italic', marginBottom: '10px' }}>
                                    "{scorecard.headline}"
                                </h3>
                            )}
                            <p className="ui-copy" style={{ whiteSpace: 'pre-wrap' }}>
                                {scorecard?.summary || `Ứng viên đạt điểm tổng quan ${roundedConfidence}/100. Hãy đọc transcript và các ghi chú bên dưới trước khi dùng kết quả này để ra quyết định.`}
                            </p>
                            {scorecard?.next_steps && (
                                <div className="card ui-card-compact" style={{ marginTop: '15px', backgroundColor: 'var(--color-bg-neutral-subtle)', borderLeft: '4px solid var(--color-brand-primary)', padding: '12px' }}>
                                    <strong>Khuyến nghị bước tiếp theo:</strong>
                                    <p className="caption" style={{ marginTop: '5px' }}>{scorecard.next_steps}</p>
                                </div>
                            )}
                        </AIResponsePanel>
                    </div>

                    {scorecard?.red_flags?.length > 0 && (
                        <div className="span-12">
                            <Alert tone="danger" title="Cảnh báo cần xem kỹ">
                                <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                    {scorecard.red_flags.map((flag, idx) => (
                                        <li key={idx} className="ui-copy">{flag}</li>
                                    ))}
                                </ul>
                            </Alert>
                        </div>
                    )}

                    {scorecard?.competencies?.length > 0 && (
                        <Panel className="span-12" title="Đánh giá năng lực chi tiết" subtitle="Điểm theo từng tiêu chí tuyển dụng, kèm lý do và bằng chứng trong phiên.">
                            <div className="report-note-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '20px' }}>
                                {scorecard.competencies.map((comp, idx) => {
                                    const percentage = comp.score * 20; // 0-5 scaled to 0-100%
                                    return (
                                        <div key={idx} className="card" style={{ display: 'flex', flexDirection: 'column', gap: '10px', padding: '15px' }}>
                                            <div className="ui-spread ui-row-gap-bottom">
                                                <strong>{comp.name}</strong>
                                                <StatusBadge tone={scoreTone(percentage)} compact>
                                                    {comp.score.toFixed(1)} / 5.0
                                                </StatusBadge>
                                            </div>
                                            <ScoreBar value={percentage} tone="auto" />
                                            {comp.rationale && (
                                                <p className="caption" style={{ marginTop: '5px' }}>
                                                    <strong>Nhận xét:</strong> {comp.rationale}
                                                </p>
                                            )}
                                            {comp.evidence && (
                                                <blockquote className="cv-opt-quote" style={{ margin: '5px 0 0 0', padding: '8px 12px', fontSize: '0.85rem', borderLeft: '3px solid var(--color-brand-primary)' }}>
                                                    <strong>Bằng chứng:</strong> {comp.evidence}
                                                </blockquote>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </Panel>
                    )}

                    <Panel className="span-6" title="Ghi nhận trong phiên" subtitle="Ghi nhận từ việc rời tab, màn hình phụ và camera (ánh sáng, khuôn mặt). Không phân tích ánh nhìn hay biểu cảm.">
                        {behavior_observations.length === 0 ? (
                            <EmptyState title="Không có cảnh báo" description="Không ghi nhận tín hiệu bất thường đáng chú ý trong phiên." />
                        ) : (
                            <div className="ui-stack ui-stack--md">
                                {behavior_observations.map((item, index) => (
                                    <article key={`${item.kind}-${index}`} className="card ui-card-compact">
                                        <div className="ui-spread ui-row-gap-bottom">
                                            <strong>{item.label || item.kind?.replaceAll('_', ' ') || 'Quan sát'}</strong>
                                            <StatusBadge tone={severityTone(item.severity)} compact>{item.severity || 'thông tin'}</StatusBadge>
                                        </div>
                                        <p className="caption">{item.suggestion || item.detail || 'Không có mô tả chi tiết.'}</p>
                                    </article>
                                ))}
                            </div>
                        )}
                    </Panel>

                    {avgSTAR && (
                        <Panel className="span-12" title="Điểm STAR trung bình" subtitle="Điểm được tính trung bình từ các câu trả lời trong phiên.">
                            <div className="report-star-grid">
                                {[
                                    ['Bối cảnh', avgSTAR.situation],
                                    ['Nhiệm vụ', avgSTAR.task],
                                    ['Hành động', avgSTAR.action],
                                    ['Kết quả', avgSTAR.result],
                                ].map(([label, value]) => (
                                    <div key={label} className="card ui-card-compact">
                                        <div className="ui-spread ui-row-gap-bottom">
                                            <strong>{label}</strong>
                                            <StatusBadge tone={scoreTone(value * 10)} compact>{value.toFixed(1)}/10</StatusBadge>
                                        </div>
                                        <ScoreBar value={value * 10} tone="auto" />
                                    </div>
                                ))}
                            </div>
                        </Panel>
                    )}

                    <Panel className="span-12" title="Ghi chú đánh giá" subtitle="Các vấn đề và gợi ý cải thiện được ghi nhận từ nội dung buổi phỏng vấn.">
                        {logic_issues.length === 0 && improvement_suggestions.length === 0 ? (
                            <EmptyState title="Không có ghi chú" description="Chưa ghi nhận vấn đề hoặc gợi ý cải thiện rõ ràng trong phiên này." />
                        ) : (
                            <div className="report-note-grid">
                                {logic_issues.length > 0 && (
                                    <div>
                                        <h3 className="title-sm">Vấn đề cần lưu ý</h3>
                                        <ul className="report-note-list">
                                            {logic_issues.map((issue, index) => <li key={`${issue}-${index}`}>{issue}</li>)}
                                        </ul>
                                    </div>
                                )}
                                {improvement_suggestions.length > 0 && (
                                    <div>
                                        <h3 className="title-sm">Gợi ý cải thiện</h3>
                                        <ul className="report-note-list">
                                            {improvement_suggestions.map((suggestion, index) => <li key={`${suggestion}-${index}`}>{suggestion}</li>)}
                                        </ul>
                                    </div>
                                )}
                            </div>
                        )}
                    </Panel>

                    <Panel className="span-12" title="Transcript" subtitle="Nội dung hội thoại được dùng làm bằng chứng đánh giá.">
                        {transcript.length === 0 ? (
                            <EmptyState title="Chưa có transcript" description="Báo cáo không có nội dung hội thoại." />
                        ) : (
                            <div className="report-transcript-list">
                                {transcript.map((turn, index) => (
                                    <div key={`${turn.role}-${index}`} className={`report-transcript-item report-transcript-item--${turn.role === 'candidate' ? 'candidate' : 'system'}`}>
                                        <strong>{speakerLabel(turn.role)}</strong>
                                        <p>{turn.content}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </Panel>
                </div>
            </Page>
        </div>
    );
};

export default InterviewReportPage;
