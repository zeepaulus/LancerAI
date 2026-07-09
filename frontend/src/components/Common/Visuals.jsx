import React from 'react';

import careerJourney from '../../assets/illustrations/ai-career-journey.svg';
import cvPipeline from '../../assets/illustrations/cv-analysis-pipeline.svg';
import interviewStates from '../../assets/illustrations/interview-states.svg';
import questionLibrary from '../../assets/illustrations/question-library.svg';
import jobMatchPipeline from '../../assets/illustrations/job-match-pipeline.svg';
import reportAnalytics from '../../assets/illustrations/report-analytics.svg';
import candidateWorkspace from '../../assets/illustrations/candidate-workspace.svg';
import productWorkspace from '../../assets/illustrations/product-workspace.svg';
import emptyInterviews from '../../assets/illustrations/empty-interviews.svg';

import brainIcon from '../../assets/icons/brain.svg';
import briefcaseIcon from '../../assets/icons/briefcase.svg';
import clipboardIcon from '../../assets/icons/clipboard.svg';
import microphoneIcon from '../../assets/icons/microphone.svg';
import questionIcon from '../../assets/icons/question.svg';
import reportIcon from '../../assets/icons/report.svg';
import resumeIcon from '../../assets/icons/resume.svg';
import targetIcon from '../../assets/icons/target.svg';
import uploadCloudIcon from '../../assets/icons/upload-cloud.svg';

const illustrations = {
    dashboard: careerJourney,
    journey: careerJourney,
    voice: interviewStates,
    interview: interviewStates,
    cv: cvPipeline,
    upload: cvPipeline,
    extraction: cvPipeline,
    match: jobMatchPipeline,
    report: reportAnalytics,
    analytics: reportAnalytics,
    questions: questionLibrary,
    candidate: candidateWorkspace,
    workspace: productWorkspace,
    emptyInterview: emptyInterviews,
};

const iconAssets = {
    ai: brainIcon,
    brain: brainIcon,
    cv: resumeIcon,
    upload: uploadCloudIcon,
    voice: microphoneIcon,
    interview: microphoneIcon,
    match: targetIcon,
    job: briefcaseIcon,
    report: reportIcon,
    analytics: reportIcon,
    questions: questionIcon,
    structure: clipboardIcon,
};

const labels = {
    dashboard: 'Bảng tổng quan CV, việc làm và phỏng vấn',
    journey: 'Quy trình chuẩn bị ứng tuyển từ CV đến phỏng vấn',
    voice: 'Phòng phỏng vấn giọng nói với micro, camera và transcript',
    interview: 'Phòng phỏng vấn giọng nói với micro, camera và transcript',
    cv: 'Quy trình trích xuất và đánh giá CV',
    upload: 'Quy trình tải lên và trích xuất CV',
    extraction: 'Quy trình trích xuất dữ liệu CV',
    match: 'So khớp CV với yêu cầu trong mô tả công việc',
    report: 'Báo cáo phỏng vấn với điểm, nhận xét và transcript',
    analytics: 'Báo cáo phỏng vấn với điểm, nhận xét và transcript',
    questions: 'Ngân hàng câu hỏi phỏng vấn có thể tìm kiếm',
    candidate: 'Lịch sử CV, phỏng vấn và báo cáo của ứng viên',
    workspace: 'Bảng tổng quan các tác vụ CV, việc làm và phỏng vấn',
    emptyInterview: 'Trạng thái chưa có phiên phỏng vấn',
};

export const AssetIllustration = ({ name = 'workspace', className = '', compact = false }) => {
    const src = illustrations[name] || illustrations.workspace;
    return (
        <img
            className={`asset-illustration ${compact ? 'asset-illustration--compact' : ''} ${className}`}
            src={src}
            alt={labels[name] || labels.workspace}
            loading="lazy"
        />
    );
};

export const CandidateAvatar = ({ name = 'Candidate', size = 40, status = 'neutral' }) => {
    const initials = name
        .split(/\s+/)
        .filter(Boolean)
        .slice(0, 2)
        .map((part) => part[0]?.toUpperCase())
        .join('') || 'C';

    return (
        <span
            role="img"
            aria-label={`${name} avatar`}
            className="candidate-avatar"
            style={{ width: size, height: size, fontSize: Math.max(11, size * 0.34), '--avatar-status': statusColor(status) }}
        >
            {initials}
            <span className="candidate-avatar__status" />
        </span>
    );
};

export const AIAssistantMark = ({ active = false, size = 72 }) => (
    <div
        role="img"
        aria-label="Biểu tượng hỗ trợ phân tích"
        className={`ai-assistant-mark ${active ? 'is-active' : ''}`}
        style={{ width: size, height: size }}
    >
        <img src={brainIcon} alt="" aria-hidden="true" />
    </div>
);

export const ProductMockupGraphic = ({ variant = 'dashboard' }) => (
    <AssetIllustration name={variant} className={`product-mockup product-mockup--${variant}`} />
);

export const CVDocumentGraphic = () => (
    <AssetIllustration name="cv" className="cv-document-graphic" />
);

export const CameraPlaceholder = ({
    label = 'Không mở được camera',
    name = 'Ứng viên',
    hint = 'Video ứng viên sẽ hiển thị sau khi cấp quyền camera.',
}) => (
    <div role="img" aria-label={label} className="camera-placeholder">
        <CandidateAvatar name={name} size={64} status="warning" />
        <strong>{label}</strong>
        <span>{hint}</span>
    </div>
);

export const CandidateClusterGraphic = () => (
    <AssetIllustration name="candidate" className="candidate-cluster-graphic" />
);

export const EvaluationScoreGraphic = ({ score = null }) => (
    <div role="img" className="evaluation-score-graphic" aria-label={score == null ? 'Báo cáo đánh giá' : `Điểm báo cáo ${score} trên 100`}>
        <AssetIllustration name="report" />
        <span>{score == null ? '—' : score}</span>
    </div>
);

export const FeatureIcon = ({ type = 'ai' }) => (
    <span className={`feature-icon feature-icon--${type}`} aria-hidden="true">
        <img src={iconAssets[type] || iconAssets.ai} alt="" />
    </span>
);

function statusColor(status) {
    if (status === 'success') return 'var(--color-success)';
    if (status === 'warning') return 'var(--color-warning)';
    if (status === 'danger') return 'var(--color-danger)';
    return 'var(--color-brand-primary)';
}

export default ProductMockupGraphic;
