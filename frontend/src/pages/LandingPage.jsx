import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
    const navigate = useNavigate();

    const handleViewReport = () => {
        const pdfUrl = '/report.pdf'; 
        window.open(pdfUrl, '_blank');
    };

    // --- Inline Styles (Tạm thời sử dụng inline CSS để bạn copy chạy được ngay) ---
    const styles = {
        container: { fontFamily: 'system-ui, sans-serif', color: '#333', lineHeight: '1.6', paddingBottom: '50px' },
        hero: { textAlign: 'center', padding: '80px 20px', background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)' },
        title: { fontSize: '2.5rem', fontWeight: 'bold', color: '#1a202c', marginBottom: '15px' },
        subtitle: { fontSize: '1.2rem', color: '#4a5568', maxWidth: '800px', margin: '0 auto 30px' },
        buttonGroup: { display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '20px' },
        btnLogin: { 
            padding: '12px 25px', fontSize: '16px', fontWeight: 'bold', 
            color: 'white', backgroundColor: '#3182ce', // Chữ trắng, nền xanh lam
            border: 'none', borderRadius: '6px', cursor: 'pointer', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' 
        },
        btnSignup: { 
            padding: '12px 25px', fontSize: '16px', fontWeight: 'bold', 
            color: 'black', backgroundColor: 'white', // Chữ đen, nền trắng
            border: '1px solid #3182ce', borderRadius: '6px', cursor: 'pointer' 
        },        section: { maxWidth: '1000px', margin: '60px auto 0', padding: '0 20px' },
        sectionTitle: { textAlign: 'center', fontSize: '2rem', marginBottom: '40px', color: '#2d3748' },
        grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '30px' },
        card: { background: 'white', padding: '25px', borderRadius: '10px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', borderTop: '4px solid #3182ce' },
        cardIcon: { fontSize: '2rem', marginBottom: '15px' },
        vsBox: { background: '#f8fafc', padding: '20px', borderRadius: '8px', borderLeft: '4px solid #e2e8f0', marginBottom: '15px' },
        footer: { 
            textAlign: 'center', padding: '40px 0', marginTop: '60px', 
            borderTop: '1px solid #eee', backgroundColor: '#fff' 
        },
        btnReport: {
            padding: '10px 20px', fontSize: '14px', backgroundColor: '#4a5568', 
            color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer'
        }
    };

    return (
        <div style={styles.container}>
            <header style={styles.hero}>
                <h1 style={styles.title}>Trang bị kiến thức và kỹ năng phỏng vấn chuyên nghiệp!</h1>
                <p style={styles.subtitle}>
                    <strong>LancerAI</strong> - Hệ thống trợ lý AI đóng vai trò như một Mentor thực chiến. 
                    Giúp sinh viên IT vượt qua vòng lọc CV tự động (ATS) và tự tin đối mặt với các hội đồng phỏng vấn kỹ thuật dồn ép.
                </p>
                <div style={styles.buttonGroup}>
                    <button style={styles.btnLogin} onClick={() => navigate('/auth')}>
                        Đăng nhập
                    </button>
                    <button style={styles.btnSignup} onClick={() => navigate('/auth')}>
                        Đăng ký
                    </button>
                </div>
            </header>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>Tại sao ứng viên IT thường đánh mất cơ hội?</h2>
                <div style={styles.grid}>
                    <div style={styles.card}>
                        <div style={styles.cardIcon}>📄</div>
                        <h3 style={{marginBottom: '10px'}}>Lỗi "Mù" hệ thống ATS</h3>
                        <p>CV của bạn có thể rất tốt, nhưng bị hệ thống tự động loại bỏ từ "vòng gửi xe" chỉ vì không tối ưu từ khóa và định dạng.</p>
                    </div>
                    <div style={styles.card}>
                        <div style={styles.cardIcon}>😨</div>
                        <h3 style={{marginBottom: '10px'}}>Áp lực phòng phỏng vấn</h3>
                        <p>Thiếu kinh nghiệm thực chiến dẫn đến tâm lý hoảng sợ, mất bình tĩnh khi bị hội đồng kỹ thuật hỏi xoáy, hỏi bám đuổi.</p>
                    </div>
                </div>
            </section>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>Giải pháp từ AI Mentor của chúng tôi</h2>
                <div style={styles.grid}>
                    <div style={styles.card}>
                        <div style={styles.cardIcon}>🔍</div>
                        <h3>Chấm điểm CV & Kiểm chứng Logic</h3>
                        <p>Không chỉ đếm từ khóa! Hệ thống áp dụng <strong>RAG & Chain-of-Thought</strong> để phân tích sâu độ tương thích giữa CV và Job Description (JD). Đảm bảo nhận xét chính xác, trích dẫn rõ ràng, không bịa đặt (No Hallucination).</p>
                    </div>
                    <div style={styles.card}>
                        <div style={styles.cardIcon}>🎙️</div>
                        <h3>Phỏng vấn Giọng nói (Voice AI)</h3>
                        <p>Trải nghiệm phỏng vấn dồn ép thời gian thực với độ trễ dưới 1.5s. AI tự động đặt câu hỏi bám sát CV của bạn. Đặc biệt: <strong>Dữ liệu giọng nói của bạn không bị lưu trữ</strong> để bảo vệ quyền riêng tư.</p>
                    </div>
                    <div style={styles.card}>
                        <div style={styles.cardIcon}>📝</div>
                        <h3>Bóc tách CV thông minh (OCR)</h3>
                        <p>Hệ thống nhận diện thị giác máy tính đọc hiểu các format CV phức tạp. Kết hợp cơ chế <strong>Human-in-the-loop</strong>, cho phép bạn toàn quyền kiểm tra và chỉnh sửa dữ liệu trước khi phân tích.</p>
                    </div>
                </div>
            </section>

            <section style={styles.section}>
                <h2 style={styles.sectionTitle}>Sự khác biệt của chúng tôi</h2>
                <div>
                    <div style={styles.vsBox}>
                        <h4>❌ Khác với TopCV hay Canva:</h4>
                        <p>Chúng tôi không chỉ cung cấp Template đẹp. AI của chúng tôi đánh giá logic sâu bên trong kỹ năng của bạn và cung cấp môi trường luyện nói thực tế.</p>
                    </div>
                    <div style={styles.vsBox}>
                        <h4>❌ Khác với ChatGPT thông thường:</h4>
                        <p>ChatGPT đưa ra lời khuyên quá an toàn và dễ bịa đặt thông tin kỹ thuật. Hệ thống của chúng tôi (Local LLM) được tinh chỉnh riêng để tạo ra môi trường phỏng vấn dồn ép, độ trễ thấp và bám sát thực tế ngành IT.</p>
                    </div>
                </div>
            </section>

            <footer style={styles.footer}>
                <button style={styles.btnLogin} onClick={handleViewReport}>
                    Xem báo cáo dự án
                </button>
            </footer>
        </div>
    );
};

export default LandingPage;