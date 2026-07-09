import React, { useMemo, useState } from 'react';
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
    ScoreBar,
    StatusBadge,
} from '../components/Common/AppUI';
import { CVDocumentGraphic, ProductMockupGraphic } from '../components/Common/Visuals';
import { optimizeCV } from '../api/optimization';

const INDUSTRIES = [
    { value: 'technology', label: 'Kỹ thuật phần mềm' },
    { value: 'data_ai', label: 'Data / AI' },
    { value: 'devops_cloud', label: 'DevOps / Cloud' },
    { value: 'qa_testing', label: 'QA / Testing' },
];

function scoreTone(score) {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'danger';
}

function formatMetricLabel(key) {
    return ({
        profile: 'Hồ sơ',
        experience: 'Kinh nghiệm',
        impact: 'Bằng chứng tác động',
        skills: 'Độ khớp kỹ năng',
        structure: 'Cấu trúc ATS',
        target_alignment: 'Độ khớp mục tiêu',
    }[key] || key.replaceAll('_', ' '));
}

function issueTypeLabel(type) {
    return ({
        vague_claim: 'Diễn đạt mơ hồ',
        buzzword: 'Từ khóa sáo rỗng',
        missing_metric: 'Thiếu số liệu',
        weak_verb: 'Động từ yếu',
        generic_statement: 'Câu chung chung',
    }[type] || type || 'Cần xem');
}

function severityTone(severity) {
    if (severity === 'critical' || severity === 'high') return 'danger';
    if (severity === 'medium') return 'warning';
    return 'neutral';
}

function formatFieldPath(path) {
    if (!path) return 'Phần trong CV';
    const labels = {
        personal_info: 'Hồ sơ',
        education: 'Học vấn',
        experience: 'Kinh nghiệm',
        projects: 'Dự án',
        skills_matrix: 'Kỹ năng',
        certifications: 'Chứng chỉ',
        languages: 'Ngoại ngữ',
        school: 'Trường',
        degree: 'Bằng cấp',
        major: 'Major',
        gpa: 'GPA',
        period: 'Thời gian',
        company: 'Công ty',
        title: 'Chức danh',
        descriptions: 'Mô tả',
        key_impacts: 'Tác động',
        tech_stack: 'Tech stack',
        name: 'Tên',
        role: 'Vai trò',
        description: 'Mô tả',
        frameworks: 'Frameworks',
        tools: 'Tools',
        soft_skills: 'Kỹ năng mềm',
    };
    return String(path)
        .split('.')
        .map((part) => {
            const match = part.match(/^([a-zA-Z_]+)\[(\d+)\]$/);
            if (match) {
                const label = labels[match[1]] || match[1].replaceAll('_', ' ');
                return `${label} ${Number(match[2]) + 1}`;
            }
            return labels[part] || part.replaceAll('_', ' ');
        })
        .join(' · ');
}

const CVOptimizationPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const cvId = location.state?.cvId;

    const [jobTitle, setJobTitle] = useState('');
    const [industry, setIndustry] = useState('technology');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [result, setResult] = useState(null);

    const auditScore = Math.round(Number(result?.audit_score || 0));
    const cvScorecard = result?.cv_scorecard || {};
    const sectionScores = cvScorecard.section_scores || {};

    const issueCounts = useMemo(() => {
        const issues = result?.roast_issues || [];
        return {
            critical: issues.filter((item) => item.severity === 'critical').length,
            high: issues.filter((item) => item.severity === 'high').length,
            total: issues.length,
        };
    }, [result]);

    const handleAnalyze = async () => {
        if (!cvId) {
            setError('Chưa chọn CV. Hãy tải hoặc trích xuất CV trước khi tối ưu.');
            return;
        }

        setLoading(true);
        setError('');
        try {
            const data = await optimizeCV(cvId, {
                target_job_title: jobTitle,
                target_industry: industry,
                mode: 'standard',
            });
            setResult(data);
        } catch (err) {
            setError(err.message || 'Chưa thể tối ưu CV. Vui lòng thử lại.');
        } finally {
            setLoading(false);
        }
    };

    if (!cvId) {
        return (
            <div className="app-screen">
                <Navbar />
                <Page narrow>
                    <EmptyState
                        visual={<CVDocumentGraphic />}
                        title="Chưa chọn CV"
                        description="Tối ưu CV cần dữ liệu CV đã trích xuất. Hãy tải CV trước rồi quay lại để xem điểm ATS và gợi ý viết lại."
                        action={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>}
                    />
                </Page>
            </div>
        );
    }

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Tối ưu CV"
                    title="Xem điểm yếu của CV trước khi xuất file"
                    description="Kiểm tra điểm ATS, câu diễn đạt yếu, kỹ năng còn thiếu và gợi ý viết lại trước khi tải PDF."
                    visual={<ProductMockupGraphic variant="cv" />}
                    tone="cv"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/cv-review')}>Lịch sử CV</button>
                            <button className="btn-primary" onClick={handleAnalyze} disabled={loading}>
                                {loading ? 'Đang phân tích...' : result ? 'Phân tích lại' : 'Bắt đầu phân tích'}
                            </button>
                        </>
                    )}
                />

                {error && (
                    <div className="ui-section-gap-bottom">
                        <Alert tone="danger" title="Chưa thể tối ưu CV">{error}</Alert>
                    </div>
                )}

                {!result && (
                    <Panel
                        title="Ngữ cảnh phân tích CV"
                        subtitle="Chọn vai trò mục tiêu nếu bạn muốn hệ thống so CV sát hơn với vị trí ứng tuyển."
                    >
                        <div className="cv-analysis-setup">
                            <label htmlFor="target-role" className="ui-field">
                                <span>Vai trò mục tiêu</span>
                                <input
                                    id="target-role"
                                    className="text-input"
                                    placeholder="Frontend Developer"
                                    value={jobTitle}
                                    onChange={(event) => setJobTitle(event.target.value)}
                                />
                            </label>

                            <label htmlFor="target-industry" className="ui-field">
                                <span>Lĩnh vực</span>
                                <select
                                    id="target-industry"
                                    className="text-input"
                                    value={industry}
                                    onChange={(event) => setIndustry(event.target.value)}
                                >
                                    {INDUSTRIES.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
                                </select>
                            </label>
                        </div>

                        <div className="cv-analysis-preview" aria-label="Kết quả phân tích sẽ gồm">
                            <span>Điểm ATS</span>
                            <span>Lỗi có bằng chứng</span>
                            <span>Gợi ý viết lại</span>
                        </div>
                    </Panel>
                )}

                {loading && (
                    <div className={result ? '' : 'ui-section-gap'}>
                        <Panel title="AI đang phân tích CV" subtitle="Thời gian thường mất 30-60 giây tùy độ dài tài liệu.">
                            <div className="cv-opt-loading-grid">
                                {['Tìm bằng chứng trong CV', 'Phát hiện câu diễn đạt yếu', 'Soạn gợi ý viết lại', 'Kiểm tra tính an toàn nội dung'].map((item, index) => (
                                    <div key={item} className="card cv-opt-loading-step">
                                        <span className="lancer-nav-icon">{index + 1}</span>
                                        <div>
                                            <strong>{item}</strong>
                                            <div className="skeleton skeleton-line" />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </Panel>
                    </div>
                )}

                {result && (
                    <>
                        <div className="metric-grid ui-section-gap-bottom">
                            <MetricCard label="Điểm ATS" value={`${auditScore}/100`} detail="Sức khỏe tổng thể của CV" tone={scoreTone(auditScore)} />
                            <MetricCard label="Vấn đề tìm thấy" value={issueCounts.total} detail={`${issueCounts.critical + issueCounts.high} ưu tiên cao`} tone={issueCounts.total ? 'warning' : 'success'} />
                            <MetricCard label="Gợi ý viết lại" value={result.rewritten_sections?.length || 0} detail="Cần xem trước khi dùng" tone="ai" />
                            <MetricCard label="Kỹ năng đã khớp" value={cvScorecard.matched_skills?.length || 0} detail="Có trong CV và vai trò mục tiêu" tone="success" />
                        </div>

                        <div className="dashboard-grid">
                            <Panel className="span-5" title="Bảng điểm ATS" subtitle="Điểm cho hồ sơ, kinh nghiệm, tác động, kỹ năng, cấu trúc và độ khớp mục tiêu.">
                                {Object.keys(sectionScores).length === 0 ? (
                                    <EmptyState title="Chưa có điểm từng phần" description="Lần phân tích này chưa trả về điểm chi tiết theo từng phần." />
                                ) : (
                                    <div className="ui-stack">
                                        {Object.entries(sectionScores).map(([key, value]) => (
                                            <div key={key}>
                                                <div className="ui-spread ui-row-gap-bottom">
                                                    <span>{formatMetricLabel(key)}</span>
                                                    <StatusBadge tone={scoreTone(value)}>{Math.round(value)}/100</StatusBadge>
                                                </div>
                                                <ScoreBar value={value} tone="auto" />
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </Panel>

                            <div className="span-7">
                                <AIResponsePanel
                                    title="Tóm tắt tối ưu CV"
                                    subtitle="Dùng như gợi ý nghề nghiệp. Hãy kiểm tra dữ kiện trước khi dùng nội dung AI."
                                    footer={<StatusBadge tone="ai">Cần duyệt thủ công</StatusBadge>}
                                >
                                    <p className="ui-copy ui-prewrap">
                                        {result.roast_summary || 'CV đã được phân tích. Hãy xem điểm yếu và gợi ý viết lại trước khi xuất file.'}
                                    </p>
                                </AIResponsePanel>
                            </div>

                            <Panel className="span-6" title="Kỹ năng đã khớp" subtitle="Các kỹ năng đã có trong CV.">
                                <div className="ui-cluster">
                                    {(cvScorecard.matched_skills || []).length > 0
                                        ? cvScorecard.matched_skills.map((skill) => <StatusBadge key={skill} tone="success">{skill}</StatusBadge>)
                                        : <p className="caption">Chưa trả về kỹ năng khớp rõ ràng.</p>}
                                </div>
                            </Panel>

                            <Panel className="span-6" title="Khoảng trống cần kiểm tra" subtitle="Dùng các mục này để chuẩn bị câu hỏi phỏng vấn hoặc bổ sung CV.">
                                <div className="ui-cluster">
                                    {(cvScorecard.missing_skills || []).length > 0
                                        ? cvScorecard.missing_skills.map((skill) => <StatusBadge key={skill} tone="warning">{skill}</StatusBadge>)
                                        : <p className="caption">Chưa phát hiện khoảng trống lớn so với vai trò.</p>}
                                </div>
                            </Panel>

                            {result.roast_issues?.length > 0 && (
                                <Panel className="span-12" title="Điểm yếu cần sửa" subtitle="Ưu tiên lỗi nghiêm trọng và các câu mô tả tác động còn mơ hồ.">
                                    <div className="ui-stack ui-stack--md">
                                        {result.roast_issues.map((issue, index) => (
                                            <article key={`${issue.field}-${index}`} className="card">
                                                <div className="cv-opt-issue-header">
                                                    <div className="ui-cluster">
                                                        <StatusBadge tone={severityTone(issue.severity)}>{issue.severity || 'cần xem'}</StatusBadge>
                                                        <StatusBadge>{issueTypeLabel(issue.issue_type)}</StatusBadge>
                                                    </div>
                                                    <span className="caption">{formatFieldPath(issue.field)}</span>
                                                </div>
                                                {issue.original_text && (
                                                    <blockquote className="cv-opt-quote">{issue.original_text}</blockquote>
                                                )}
                                                <p className="ui-copy">{issue.explanation}</p>
                                            </article>
                                        ))}
                                    </div>
                                </Panel>
                            )}

                            {result.rewritten_sections?.length > 0 && (
                                <Panel className="span-12" title="Gợi ý viết lại" subtitle="So sánh bản gốc với đề xuất của AI trước khi xuất hoặc sao chép.">
                                    <div className="ui-stack ui-stack--md">
                                        {result.rewritten_sections.map((section, index) => (
                                            <article key={`${section.field}-${index}`} className="card">
                                                <div className="cv-opt-issue-header">
                                                    <span className="caption">{formatFieldPath(section.field)}</span>
                                                    <StatusBadge tone="ai">{section.formula_used?.toUpperCase() || 'Rewrite'}</StatusBadge>
                                                </div>
                                                <div className="cv-opt-compare-grid">
                                                    <div>
                                                    <span className="page-kicker">Bản gốc</span>
                                                        <p className="cv-opt-compare-text">{section.original}</p>
                                                    </div>
                                                    <div>
                                                    <span className="page-kicker">Đề xuất</span>
                                                        <p className="cv-opt-compare-text cv-opt-compare-text--strong">{section.rewritten}</p>
                                                    </div>
                                                </div>
                                                <div className="cv-opt-review-footer">
                                                    <span className="caption">Mức cải thiện: {Math.round(Number(section.improvement_score || 0) * 100)}%</span>
                                                    <StatusBadge tone="warning">Xem lại trước khi dùng</StatusBadge>
                                                </div>
                                            </article>
                                        ))}
                                    </div>
                                </Panel>
                            )}

                            <Panel className="span-12" title="Bước tiếp theo" subtitle="Dùng kết quả phân tích để so khớp CV với mô tả công việc.">
                                <div className="ui-cluster">
                                    <button className="btn-primary" onClick={() => navigate('/job-matching', { state: { cvId } })}>
                                        So khớp với JD
                                    </button>
                                    <button className="btn-outline" onClick={() => navigate('/cv-upload')}>
                                        Phân tích CV khác
                                    </button>
                                </div>
                            </Panel>
                        </div>
                    </>
                )}
            </Page>
        </div>
    );
};

export default CVOptimizationPage;
