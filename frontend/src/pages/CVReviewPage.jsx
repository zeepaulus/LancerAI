import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const CVReviewPage = () => {
    const navigate = useNavigate();

    const history = [
        { id: 1, title: 'CV ứng tuyển vị trí Fullstack Developer (lần 3)', date: '24/10/2024', score: 30 },
        { id: 2, title: 'CV ứng tuyển vị trí Fullstack Developer (lần 2)', date: '20/10/2024', score: 55 },
        { id: 3, title: 'CV ứng tuyển vị trí Fullstack Developer (lần 1)', date: '15/10/2024', score: 77 },
    ];

    const getScoreStyle = (score) => ({
        backgroundColor: score >= 70 ? 'var(--gradient-mint)' : score >= 50 ? 'var(--gradient-peach)' : 'var(--gradient-rose)',
        color: 'var(--ink)',
    });

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <div style={styles.header}>
                    <div>
                        <h2 className="display-sm">Đánh giá CV</h2>
                    </div>
                    <button className="btn-primary" onClick={() => navigate('/chat')}>
                        + Bắt đầu đánh giá CV
                    </button>
                </div>

                <p className="caption-uppercase" style={styles.sectionLabel}>LỊCH SỬ ĐÁNH GIÁ CV</p>
                <div style={styles.cardList}>
                    {history.map(item => (
                        <div 
                            key={item.id} 
                            className="card"
                            style={styles.historyCard}
                            onClick={() => navigate('/chat')}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.borderColor = 'var(--hairline-strong)';
                                e.currentTarget.style.boxShadow = 'var(--shadow-soft)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.borderColor = 'var(--hairline)';
                                e.currentTarget.style.boxShadow = 'none';
                            }}
                        >
                            <div>
                                <h4 className="title-sm" style={{margin: '0 0 var(--sp-xs) 0'}}>{item.title}</h4>
                                <span style={styles.dateBadge}>Ngày: {item.date}</span>
                            </div>
                            <span className="badge-pill" style={getScoreStyle(item.score)}>
                                {item.score} Điểm
                            </span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '800px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg)',
    },
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--sp-xl)',
    },
    sectionLabel: {
        color: 'var(--muted)',
        marginBottom: 'var(--sp-base)',
        letterSpacing: '0.96px',
    },
    cardList: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-sm)',
    },
    historyCard: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        transition: 'all var(--transition-base)',
    },
    dateBadge: {
        fontSize: '13px',
        color: 'var(--muted)',
        letterSpacing: '0.15px',
    },
};

export default CVReviewPage;