import React, { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { CVDocumentGraphic } from '../components/Common/Visuals';
import { uploadCV } from '../api/extraction';

const VALID_TYPES = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg', 'image/webp'];
const MAX_SIZE_BYTES = 10 * 1024 * 1024;

const CVUploadPage = () => {
    const navigate = useNavigate();
    const inputRef = useRef(null);
    const [dragActive, setDragActive] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [uploadState, setUploadState] = useState('idle');
    const [selectedFile, setSelectedFile] = useState(null);

    const validateAndStage = (file) => {
        setErrorMsg('');
        if (!VALID_TYPES.includes(file.type)) {
            setErrorMsg('Vui lòng chọn file PDF, JPG, PNG hoặc WebP.');
            return;
        }
        if (file.size > MAX_SIZE_BYTES) {
            setErrorMsg('File quá lớn. Vui lòng chọn file dưới 10 MB.');
            return;
        }
        setSelectedFile(file);
    };

    const handleUpload = async () => {
        if (!selectedFile) return;
        setUploadState('uploading');
        setErrorMsg('');
        try {
            const extractionData = await uploadCV(selectedFile);
            navigate('/cv-extraction-result', {
                state: {
                    cvId: extractionData.cv_id,
                    extractionData,
                },
            });
        } catch (err) {
            setUploadState('idle');
            if (err?.status === 401) setErrorMsg('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.');
            else if (err?.status === 413) setErrorMsg('File quá lớn. Dung lượng tối đa là 10 MB.');
            else if (err?.status === 415) setErrorMsg('Định dạng file này chưa được hỗ trợ.');
            else if (err?.status >= 500) setErrorMsg('Máy chủ đang gặp lỗi. Vui lòng thử lại sau.');
            else setErrorMsg(err?.message || 'Tải CV thất bại. Vui lòng thử lại.');
        }
    };

    const isLoading = uploadState === 'uploading';

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Phân tích CV"
                    title="Tải CV để trích xuất thông tin"
                    description="LancerAI sẽ đọc CV, bóc tách các mục quan trọng và cho bạn kiểm tra lại trước khi chạy đánh giá."
                    visual={<CVDocumentGraphic />}
                    tone="cv"
                    actions={<button className="btn-outline" onClick={() => navigate('/cv-review')}>Xem lịch sử CV</button>}
                />

                <div className="split-grid">
                    <Panel title="Tải CV" subtitle="Hỗ trợ PDF, JPG, PNG và WebP. Dung lượng tối đa 10 MB.">
                        <div
                            className={`ui-dropzone ${dragActive ? 'is-active' : ''} ${selectedFile ? 'has-file' : ''}`}
                            onDragEnter={(event) => { event.preventDefault(); setDragActive(true); }}
                            onDragOver={(event) => event.preventDefault()}
                            onDragLeave={() => setDragActive(false)}
                            onDrop={(event) => {
                                event.preventDefault();
                                setDragActive(false);
                                if (event.dataTransfer.files?.[0]) validateAndStage(event.dataTransfer.files[0]);
                            }}
                        >
                            {isLoading ? (
                                <>
                                    <StatusBadge tone="ai">Đang xử lý</StatusBadge>
                                    <h2 className="title-md">Đang chuẩn bị phân tích CV</h2>
                                    <p className="page-subtitle ui-copy">Hệ thống đang đọc file và chuẩn bị dữ liệu cho bước phân tích.</p>
                                    <div className="progress-track ui-progress-narrow">
                                        <div className="progress-fill progress-fill--indeterminate" />
                                    </div>
                                </>
                            ) : selectedFile ? (
                                <>
                                    <StatusBadge tone="success">Sẵn sàng trích xuất</StatusBadge>
                                    <h2 className="title-md">{selectedFile.name}</h2>
                                    <p className="caption">Đã chọn {Math.round(selectedFile.size / 1024)} KB</p>
                                    {errorMsg && <p className="ui-error-text">{errorMsg}</p>}
                                    <div className="ui-cluster ui-cluster--center">
                                        <button className="btn-primary" onClick={handleUpload}>Trích xuất thông tin</button>
                                        <button className="btn-outline" onClick={() => { setSelectedFile(null); setErrorMsg(''); if (inputRef.current) inputRef.current.value = ''; }}>Chọn file khác</button>
                                    </div>
                                </>
                            ) : (
                                <>
                                    <StatusBadge tone="ai">AI trích xuất</StatusBadge>
                                    <div className="ui-visual-narrow">
                                        <CVDocumentGraphic />
                                    </div>
                                    <h2 className="title-md">Kéo CV vào đây</h2>
                                    <p className="page-subtitle ui-copy">hoặc chọn file để bắt đầu phân tích.</p>
                                    <button className="btn-primary" onClick={() => inputRef.current?.click()}>Chọn CV</button>
                                    <p className="caption">PDF, JPG, PNG, WebP. Tối đa 10 MB.</p>
                                    {errorMsg && <p className="ui-error-text">{errorMsg}</p>}
                                </>
                            )}
                            <input
                                ref={inputRef}
                                type="file"
                                accept="application/pdf,image/jpeg,image/png,image/webp"
                                onChange={(event) => {
                                    if (event.target.files?.[0]) validateAndStage(event.target.files[0]);
                                }}
                                className="ui-hidden-input"
                            />
                        </div>
                    </Panel>

                    <Panel title="Sau khi tải lên" subtitle="Bạn sẽ kiểm tra dữ liệu đã bóc tách trước khi chạy đánh giá CV.">
                        <div className="ui-stack ui-stack--md">
                            {[
                                ['Điểm ATS', 'Đánh giá mức độ rõ ràng, cấu trúc và khả năng vượt bộ lọc tuyển dụng.'],
                                ['Điểm yếu cần sửa', 'Chỉ ra câu mô tả mơ hồ, thiếu số liệu hoặc thiếu bằng chứng tác động.'],
                                ['Gợi ý viết lại', 'Đề xuất cách diễn đạt tốt hơn để bạn xem lại trước khi dùng.'],
                                ['So khớp JD', 'Dùng CV đã phân tích để đối chiếu với mô tả công việc khi cần.'],
                            ].map(([title, body]) => (
                                <div key={title} className="card">
                                    <strong className="ui-row-title">{title}</strong>
                                    <p className="caption">{body}</p>
                                </div>
                            ))}
                        </div>
                    </Panel>
                </div>
            </Page>
        </div>
    );
};

export default CVUploadPage;
