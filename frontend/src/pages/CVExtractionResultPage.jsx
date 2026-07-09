import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { CVDocumentGraphic } from '../components/Common/Visuals';

const CVExtractionResultPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const extractionData = location.state?.extractionData || null;
    const cvId = location.state?.cvId || extractionData?.cv_id;

    if (!cvId) {
        return (
            <div className="app-screen">
                <Navbar />
                <Page narrow>
                    <EmptyState
                        visual={<CVDocumentGraphic />}
                        title="Chưa có CV để phân tích"
                        description="Hãy tải CV lên trước, sau đó LancerAI sẽ chuyển bạn đến phần phân tích CV."
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
                    kicker="Phân tích CV"
                    title="CV đã sẵn sàng để phân tích"
                    description="Hãy bắt đầu phân tích để xem điểm ATS, điểm yếu cần sửa và gợi ý viết lại."
                    visual={<CVDocumentGraphic />}
                    tone="cv"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/cv-upload')}>Tải CV khác</button>
                            <button className="btn-primary" onClick={() => navigate('/cv-optimization', { state: { cvId } })}>Phân tích CV</button>
                        </>
                    )}
                />

                <div className="dashboard-grid">
                    <Panel className="span-12" title="Nội dung phân tích" subtitle="Các mục tập trung vào quyết định tiếp theo của người dùng.">
                        <div className="ui-stack ui-stack--md">
                            {[
                                ['Điểm ATS', 'Đánh giá cấu trúc, mức độ rõ ràng và khả năng phù hợp với bộ lọc tuyển dụng.'],
                                ['Điểm yếu cần sửa', 'Tìm câu mô tả mơ hồ, thiếu số liệu, thiếu bằng chứng hoặc chưa khớp vai trò mục tiêu.'],
                                ['Gợi ý viết lại', 'Đưa ra đề xuất để bạn duyệt thủ công trước khi xuất CV hoặc so khớp JD.'],
                            ].map(([title, body]) => (
                                <div className="card ui-card-compact ui-spread" key={title}>
                                    <div>
                                        <strong className="ui-row-title">{title}</strong>
                                        <p className="caption">{body}</p>
                                    </div>
                                    <StatusBadge tone="ai">Phân tích</StatusBadge>
                                </div>
                            ))}
                        </div>
                    </Panel>
                </div>
            </Page>
        </div>
    );
};

export default CVExtractionResultPage;
