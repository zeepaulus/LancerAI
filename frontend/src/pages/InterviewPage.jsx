import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const InterviewPage = () => {
    const navigate = useNavigate();

    const history = [
        { id: 1, title: 'Phỏng vấn Frontend Developer', date: '24/10/2023', score: 85 },
        { id: 2, title: 'Phỏng vấn Backend Node.js', date: '20/10/2023', score: 72 },
        { id: 3, title: 'Phỏng vấn Hành vi (Behavioral)', date: '15/10/2023', score: 90 },
    ];

    const getScoreStyle = (score) => ({
        backgroundColor: score >= 80 ? 'var(--gradient-mint)' : 'var(--gradient-peach)',
        color: 'var(--ink)',
    });

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <div style={styles.header}>
                    <div>
                        <h2 className="display-sm">Phỏng vấn AI</h2>
                    </div>
                    <button className="btn-primary" onClick={() => navigate('/chat')}>
                        + Bắt đầu phỏng vấn
                    </button>
                </div>

                <p className="caption-uppercase" style={styles.sectionLabel}>LỊCH SỬ PHỎNG VẤN</p>
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

export default InterviewPage;