import React from 'react';
import { useNavigate } from 'react-router-dom';

const LandingPage = () => {
    const navigate = useNavigate();

    const handleViewReport = () => {
        const pdfUrl = '/report.pdf'; 
        window.open(pdfUrl, '_blank');
    };

    return (
        <div style={styles.page}>
            {/* ─── Top Nav (Landing-only, minimal) ─── */}
            <nav style={styles.topNav}>
                <span style={styles.navLogo}>LANCER AI</span>
                <div style={styles.navActions}>
                    <button className="btn-outline" onClick={() => navigate('/login')}>Đăng nhập</button>
                    <button className="btn-primary" onClick={() => navigate('/signup')}>Bắt đầu miễn phí</button>
                </div>
            </nav>

            {/* ─── Hero Band ─── */}
            <header style={styles.hero}>
                {/* Atmospheric gradient orbs */}
                <div className="gradient-orb gradient-orb--mint" style={{width: '400px', height: '400px', top: '-100px', left: '-80px'}}></div>
                <div className="gradient-orb gradient-orb--lavender" style={{width: '350px', height: '350px', bottom: '-80px', right: '-60px'}}></div>
                <div className="gradient-orb gradient-orb--peach" style={{width: '250px', height: '250px', top: '50%', left: '60%', opacity: 0.3}}></div>

                <div style={styles.heroContent}>
                    <div style={styles.heroBadge}>
                        <span className="caption-uppercase" style={{color: 'var(--muted)'}}>AI MENTOR CHO SINH VIÊN IT</span>
                    </div>
                    <h1 className="display-mega" style={styles.heroTitle}>
                        Trang bị kiến thức<br />phỏng vấn chuyên nghiệp
                    </h1>
                    <p style={styles.heroSub}>
                        <strong style={{color: 'var(--ink)', fontWeight: 500}}>LancerAI</strong> — Hệ thống trợ lý AI đóng vai trò như một Mentor thực chiến. 
                        Giúp sinh viên IT vượt qua vòng lọc CV tự động (ATS) và tự tin đối mặt với các hội đồng phỏng vấn kỹ thuật.
                    </p>
                    <div style={styles.heroButtons}>
                        <button className="btn-primary" style={{padding: '12px 28px', height: '44px', fontSize: '16px'}} onClick={() => navigate('/signup')}>
                            Bắt đầu ngay
                        </button>
                        <button className="btn-outline" style={{padding: '11px 27px', height: '44px', fontSize: '16px'}} onClick={() => navigate('/login')}>
                            Đăng nhập
                        </button>
                    </div>
                </div>
            </header>

            {/* ─── Problems Section ─── */}
            <section style={styles.section}>
                <div style={styles.sectionInner}>
                    <p className="caption-uppercase" style={styles.sectionLabel}>VẤN ĐỀ</p>
                    <h2 className="display-lg" style={styles.sectionTitle}>Tại sao ứng viên IT thường đánh mất cơ hội?</h2>
                    <div style={styles.grid2}>
                        <div className="card" style={styles.featureCard}>
                            <div style={styles.cardIconWrap}>📄</div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>Lỗi "Mù" hệ thống ATS</h3>
                            <p style={styles.cardBody}>CV của bạn có thể rất tốt, nhưng bị hệ thống tự động loại bỏ từ "vòng gửi xe" chỉ vì không tối ưu từ khóa và định dạng.</p>
                        </div>
                        <div className="card" style={styles.featureCard}>
                            <div style={styles.cardIconWrap}>😨</div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>Áp lực phòng phỏng vấn</h3>
                            <p style={styles.cardBody}>Thiếu kinh nghiệm thực chiến dẫn đến tâm lý hoảng sợ, mất bình tĩnh khi bị hội đồng kỹ thuật hỏi xoáy, hỏi bám đuổi.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── Solutions Section ─── */}
            <section style={{...styles.section, backgroundColor: 'var(--canvas-soft)'}}>
                <div style={styles.sectionInner}>
                    <p className="caption-uppercase" style={styles.sectionLabel}>GIẢI PHÁP</p>
                    <h2 className="display-lg" style={styles.sectionTitle}>Giải pháp từ AI Mentor của chúng tôi</h2>
                    <div style={styles.grid3}>
                        <div className="card" style={styles.featureCard}>
                            <div style={styles.cardIconWrap}>🔍</div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>Chấm điểm CV & Kiểm chứng Logic</h3>
                            <p style={styles.cardBody}>Hệ thống áp dụng <strong>RAG & Chain-of-Thought</strong> để phân tích sâu độ tương thích giữa CV và Job Description (JD). Đảm bảo nhận xét chính xác, không bịa đặt.</p>
                        </div>
                        <div className="card" style={styles.featureCard}>
                            <div style={styles.cardIconWrap}>🎙️</div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>Phỏng vấn Giọng nói (Voice AI)</h3>
                            <p style={styles.cardBody}>Trải nghiệm phỏng vấn dồn ép thời gian thực với độ trễ dưới 1.5s. AI tự động đặt câu hỏi bám sát CV của bạn. <strong>Dữ liệu giọng nói không bị lưu trữ.</strong></p>
                        </div>
                        <div className="card" style={styles.featureCard}>
                            <div style={styles.cardIconWrap}>📝</div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-sm)'}}>Bóc tách CV thông minh (OCR)</h3>
                            <p style={styles.cardBody}>Hệ thống nhận diện thị giác đọc hiểu các format CV phức tạp. Cơ chế <strong>Human-in-the-loop</strong> cho phép bạn toàn quyền kiểm tra và chỉnh sửa dữ liệu.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── Differentiators Section ─── */}
            <section style={styles.section}>
                <div style={styles.sectionInner}>
                    <p className="caption-uppercase" style={styles.sectionLabel}>KHÁC BIỆT</p>
                    <h2 className="display-lg" style={styles.sectionTitle}>Sự khác biệt của chúng tôi</h2>
                    <div style={styles.diffGrid}>
                        <div style={styles.diffCard}>
                            <div style={styles.diffBadge}>VS</div>
                            <h4 className="title-sm" style={{marginBottom: 'var(--sp-xs)'}}>Khác với TopCV hay Canva</h4>
                            <p style={styles.cardBody}>Chúng tôi không chỉ cung cấp Template đẹp. AI của chúng tôi đánh giá logic sâu bên trong kỹ năng của bạn và cung cấp môi trường luyện nói thực tế.</p>
                        </div>
                        <div style={styles.diffCard}>
                            <div style={styles.diffBadge}>VS</div>
                            <h4 className="title-sm" style={{marginBottom: 'var(--sp-xs)'}}>Khác với ChatGPT thông thường</h4>
                            <p style={styles.cardBody}>ChatGPT đưa ra lời khuyên quá an toàn và dễ bịa đặt thông tin kỹ thuật. Hệ thống của chúng tôi được tinh chỉnh riêng để tạo ra môi trường phỏng vấn dồn ép, bám sát thực tế ngành IT.</p>
                        </div>
                    </div>
                </div>
            </section>

            {/* ─── CTA Band ─── */}
            <section style={styles.ctaBand}>
                <div style={{position: 'relative', zIndex: 1}}>
                    <h2 className="display-lg" style={{textAlign: 'center', marginBottom: 'var(--sp-lg)', color: 'var(--ink)'}}>
                        Sẵn sàng chinh phục nhà tuyển dụng?
                    </h2>
                    <p style={{textAlign: 'center', color: 'var(--body)', marginBottom: 'var(--sp-xl)', maxWidth: '480px', marginLeft: 'auto', marginRight: 'auto'}}>
                        Bắt đầu hành trình nâng cấp CV và luyện phỏng vấn ngay hôm nay.
                    </p>
                    <div style={{display: 'flex', justifyContent: 'center', gap: 'var(--sp-base)'}}>
                        <button className="btn-primary" style={{padding: '12px 28px', height: '44px', fontSize: '16px'}} onClick={() => navigate('/signup')}>
                            Đăng ký miễn phí
                        </button>
                        <button className="btn-outline" style={{padding: '11px 27px', height: '44px', fontSize: '16px'}} onClick={handleViewReport}>
                            Xem báo cáo dự án
                        </button>
                    </div>
                </div>
                {/* Orb decoration */}
                <div className="gradient-orb gradient-orb--sky" style={{width: '300px', height: '300px', top: '-80px', right: '-60px', opacity: 0.3}}></div>
                <div className="gradient-orb gradient-orb--rose" style={{width: '250px', height: '250px', bottom: '-60px', left: '-40px', opacity: 0.3}}></div>
            </section>

            {/* ─── Footer ─── */}
            <footer style={styles.footer}>
                <div style={styles.footerInner}>
                    <div style={styles.footerBrand}>
                        <span style={{...styles.navLogo, fontSize: '14px', letterSpacing: '1.5px'}}>LANCER AI</span>
                        <p className="body-sm" style={{color: 'var(--muted)', marginTop: 'var(--sp-xs)'}}>
                            AI Mentor cho sinh viên IT Việt Nam
                        </p>
                    </div>
                    <p className="caption" style={{color: 'var(--muted)'}}>
                        © 2026 LancerAI. Đồ án tốt nghiệp.
                    </p>
                </div>
            </footer>
        </div>
    );
};

const styles = {
    page: {
        fontFamily: 'var(--font-body)',
        color: 'var(--body)',
        backgroundColor: 'var(--canvas)',
        minHeight: '100vh',
    },
    /* ── Top Nav ── */
    topNav: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '0 var(--sp-xl)',
        height: '64px',
        backgroundColor: 'var(--canvas)',
        borderBottom: '1px solid var(--hairline)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backdropFilter: 'blur(8px)',
    },
    navLogo: {
        fontFamily: 'var(--font-body)',
        fontWeight: 600,
        fontSize: '15px',
        color: 'var(--ink)',
        letterSpacing: '1.5px',
    },
    navActions: {
        display: 'flex',
        gap: 'var(--sp-sm)',
        alignItems: 'center',
    },
    /* ── Hero ── */
    hero: {
        position: 'relative',
        overflow: 'hidden',
        padding: '120px var(--sp-xl) 100px',
        textAlign: 'center',
        backgroundColor: 'var(--canvas)',
    },
    heroContent: {
        position: 'relative',
        zIndex: 1,
        maxWidth: '800px',
        margin: '0 auto',
    },
    heroBadge: {
        display: 'inline-block',
        backgroundColor: 'var(--surface-strong)',
        borderRadius: 'var(--rounded-pill)',
        padding: '6px 16px',
        marginBottom: 'var(--sp-lg)',
    },
    heroTitle: {
        marginBottom: 'var(--sp-lg)',
    },
    heroSub: {
        fontSize: '17px',
        lineHeight: 1.6,
        color: 'var(--body)',
        maxWidth: '600px',
        margin: '0 auto var(--sp-xl)',
        letterSpacing: '0.15px',
    },
    heroButtons: {
        display: 'flex',
        gap: 'var(--sp-base)',
        justifyContent: 'center',
        flexWrap: 'wrap',
    },
    /* ── Sections ── */
    section: {
        padding: '96px var(--sp-xl)',
        backgroundColor: 'var(--canvas)',
        transition: 'background-color var(--transition-base)',
    },
    sectionInner: {
        maxWidth: '1100px',
        margin: '0 auto',
    },
    sectionLabel: {
        textAlign: 'center',
        color: 'var(--muted)',
        marginBottom: 'var(--sp-sm)',
        letterSpacing: '0.96px',
    },
    sectionTitle: {
        textAlign: 'center',
        marginBottom: 'var(--sp-xxl)',
    },
    /* ── Grids ── */
    grid2: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 'var(--sp-lg)',
    },
    grid3: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: 'var(--sp-lg)',
    },
    /* ── Feature Card ── */
    featureCard: {
        padding: 'var(--sp-xl)',
    },
    cardIconWrap: {
        width: '48px',
        height: '48px',
        borderRadius: 'var(--rounded-lg)',
        backgroundColor: 'var(--surface-strong)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '22px',
        marginBottom: 'var(--sp-base)',
    },
    cardBody: {
        color: 'var(--body)',
        fontSize: '15px',
        lineHeight: 1.6,
        letterSpacing: '0.15px',
    },
    /* ── Diff Cards ── */
    diffGrid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: 'var(--sp-lg)',
    },
    diffCard: {
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-xl)',
        padding: 'var(--sp-xl)',
        position: 'relative',
    },
    diffBadge: {
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '32px',
        height: '32px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        color: 'var(--muted)',
        fontSize: '11px',
        fontWeight: 600,
        letterSpacing: '0.5px',
        marginBottom: 'var(--sp-sm)',
    },
    /* ── CTA Band ── */
    ctaBand: {
        position: 'relative',
        overflow: 'hidden',
        padding: '96px var(--sp-xl)',
        backgroundColor: 'var(--canvas-soft)',
    },
    /* ── Footer ── */
    footer: {
        backgroundColor: 'var(--canvas)',
        borderTop: '1px solid var(--hairline)',
        padding: '48px var(--sp-xl)',
    },
    footerInner: {
        maxWidth: '1100px',
        margin: '0 auto',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        flexWrap: 'wrap',
        gap: 'var(--sp-base)',
    },
    footerBrand: {},
};

export default LandingPage;