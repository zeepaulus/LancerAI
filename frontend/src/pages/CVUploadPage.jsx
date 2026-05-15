import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const CVUploadPage = () => {
    const navigate = useNavigate();
    const [dragActive, setDragActive] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');
    const [isUploading, setIsUploading] = useState(false);
    const inputRef = useRef(null);

    // Xử lý kéo thả
    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    // Xử lý khi thả file vào
    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            processFile(e.dataTransfer.files[0]);
        }
    };

    // Xử lý khi bấm nút "Chọn CV"
    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            processFile(e.target.files[0]);
        }
    };

    // Kiểm tra định dạng và giả lập tải lên
    const processFile = (file) => {
        setErrorMsg('');
        
        // Kiểm tra loại file (MIME type)
        const validTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/jpg'];
        if (!validTypes.includes(file.type)) {
            setErrorMsg('Định dạng không hợp lệ! Vui lòng chỉ tải lên file PDF hoặc Hình ảnh (JPG, PNG).');
            return;
        }

        // Kiểm tra dung lượng (VD: giới hạn 5MB)
        if (file.size > 5 * 1024 * 1024) {
            setErrorMsg('File quá lớn! Vui lòng chọn file dưới 5MB.');
            return;
        }

        setIsUploading(true);

        /* TƯƠNG LAI: Ở đây bạn sẽ dùng FormData để gửi file lên Backend
        const formData = new FormData();
        formData.append("cv_file", file);
        await axios.post('/api/upload', formData);
        */

        // Giả lập thời gian xử lý tải file (1.5 giây) rồi chuyển trang
        setTimeout(() => {
            setIsUploading(false);
            navigate('/chat'); // Chuyển sang trang Chatbot
        }, 1500);
    };

    // Kích hoạt input file ẩn khi bấm nút
    const onButtonClick = () => {
        inputRef.current.click();
    };

    const styles = {
        container: { maxWidth: '900px', margin: '40px auto', padding: '0 20px', fontFamily: 'system-ui', color: 'var(--text-color)', textAlign: 'center' },
        title: { fontSize: '36px', fontWeight: 'bold', marginBottom: '30px' },
        
        // Vùng Kéo thả
        uploadBox: { 
            position: 'relative',
            // Sử dụng màu xanh trong suốt để vừa đẹp ở Light Mode, vừa không bị chói ở Dark Mode
            backgroundColor: dragActive ? 'rgba(99, 179, 237, 0.4)' : 'rgba(99, 179, 237, 0.15)',
            border: `2px dashed ${dragActive ? '#3182ce' : '#63b3ed'}`,
            borderRadius: '16px',
            padding: '50px 20px',
            transition: 'all 0.3s ease',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            marginBottom: '40px'
        },
        uploadIcon: { fontSize: '48px', marginBottom: '15px' },
        btnChoose: { 
            background: 'var(--bg-color)', 
            color: 'var(--text-color)', 
            border: '1px solid var(--border-color)', 
            padding: '10px 24px', 
            borderRadius: '6px', 
            fontSize: '16px', 
            cursor: 'pointer',
            marginBottom: '10px',
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)'
        },
        errorText: { color: '#e53e3e', marginTop: '15px', fontWeight: 'bold' },
        
        // Khu vực Features (3 cột)
        subtitle: { fontSize: '18px', fontWeight: 'bold', marginBottom: '30px' },
        featuresGrid: { display: 'flex', gap: '30px', justifyContent: 'center', flexWrap: 'wrap' },
        featureCard: { flex: '1', minWidth: '200px', display: 'flex', flexDirection: 'column', alignItems: 'center', textAlign: 'center' },
        featureIcon: { fontSize: '36px', marginBottom: '15px', display: 'flex', alignItems: 'center', justifyContent: 'center', width: '60px', height: '60px', borderRadius: '50%', background: 'var(--nav-bg)', border: '1px solid var(--border-color)' },
        featureTitle: { fontSize: '16px', fontWeight: 'bold', marginBottom: '10px' },
        featureDesc: { fontSize: '14px', opacity: 0.8, lineHeight: '1.5' }
    };

    return (
        <div>
            <Navbar />
            <div style={styles.container}>
                <h1 style={styles.title}>Upload CV</h1>

                {/* Vùng Upload Kéo Thả */}
                <div 
                    style={styles.uploadBox}
                    onDragEnter={handleDrag}
                    onDragLeave={handleDrag}
                    onDragOver={handleDrag}
                    onDrop={handleDrop}
                >
                    <div style={styles.uploadIcon}>📄</div>
                    
                    {isUploading ? (
                        <h3 style={{color: '#3182ce'}}>Đang xử lý file...</h3>
                    ) : (
                        <>
                            <button style={styles.btnChoose} onClick={onButtonClick}>Chọn CV ▾</button>
                            <span>hoặc kéo thả CV vào đây</span>
                            <input 
                                ref={inputRef}
                                type="file" 
                                accept="application/pdf, image/jpeg, image/png, image/jpg" 
                                onChange={handleChange} 
                                style={{ display: 'none' }} 
                            />
                            {errorMsg && <p style={styles.errorText}>{errorMsg}</p>}
                        </>
                    )}
                </div>

                {/* Phần thông tin thêm */}
                <h3 style={styles.subtitle}>CV của bạn sẽ được sử dụng cho</h3>
                <div style={styles.featuresGrid}>
                    <div style={styles.featureCard}>
                        <div style={styles.featureIcon}>🕒</div>
                        <h4 style={styles.featureTitle}>Phân tích CV</h4>
                        <p style={styles.featureDesc}>Đánh giá kỹ năng, kinh nghiệm và mức độ phù hợp với vị trí ứng tuyển.</p>
                    </div>
                    <div style={styles.featureCard}>
                        <div style={styles.featureIcon}>👥</div>
                        <h4 style={styles.featureTitle}>Phỏng vấn giả lập</h4>
                        <p style={styles.featureDesc}>Luyện tập phỏng vấn với các câu hỏi thực tế và phản hồi tức thì.</p>
                    </div>
                    <div style={styles.featureCard}>
                        <div style={styles.featureIcon}>⭐</div>
                        <h4 style={styles.featureTitle}>Gợi ý việc làm</h4>
                        <p style={styles.featureDesc}>Đề xuất công việc phù hợp dựa trên kỹ năng và nội dung CV của bạn.</p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CVUploadPage;