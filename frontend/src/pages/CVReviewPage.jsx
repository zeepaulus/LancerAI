import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const InterviewPage = () => {
    const navigate = useNavigate();

    // Dữ liệu giả lập
    const history = [
        { id: 1, title: 'CV ứng tuyển vị trí Fullstack Developer (lần 3)', date: '24/10/2024', score: 30 },
        { id: 2, title: 'CV ứng tuyển vị trí Fullstack Developer (lần 2)', date: '20/10/2024', score: 55 },
        { id: 3, title: 'CV ứng tuyển vị trí Fullstack Developer (lần 1)', date: '15/10/2024', score: 77 },
    ];

    const styles = {
        secondTitle: { margin: '0 0 24px 0', fontSize: '18px' }, 
        container: { maxWidth: '800px', margin: '40px auto', padding: '0 20px', fontFamily: 'system-ui', color: 'var(--text-color)' },
        header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '30px' },
        btnStart: { background: '#3182ce', color: 'white', padding: '12px 24px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '16px' },
        cardList: { display: 'flex', flexDirection: 'column', gap: '15px' },
        historyCard: { background: 'var(--bg-color)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer', transition: 'all 0.2s' },
        scoreBadge: (score) => ({ background: score >= 80 ? '#48bb78' : '#ecc94b', color: score >= 80 ? 'white' : 'black', padding: '5px 12px', borderRadius: '20px', fontWeight: 'bold', fontSize: '14px' })
    };

    return (
        <div>
            <Navbar />
            <div style={styles.container}>
                <div style={styles.header}>
                    <h2>Đánh giá CV</h2>
                    <button style={styles.btnStart} onClick={() => navigate('/chat')}>+ Bắt đầu đánh giá CV</button>
                </div>

                <h3 style={styles.secondTitle}> Lịch sử đánh giá CV</h3>
                <div style={styles.cardList}>
                    {history.map(item => (
                        <div 
                            key={item.id} 
                            style={styles.historyCard} 
                            onClick={() => navigate('/chat')} // Nhấn vào lịch sử cũng mở giao diện Chat
                            onMouseOver={(e) => e.currentTarget.style.borderColor = '#3182ce'}
                            onMouseOut={(e) => e.currentTarget.style.borderColor = 'var(--border-color)'}
                        >
                            <div>
                                <h4 style={{ margin: '0 0 8px 0' }}>{item.title}</h4>
                                <span style={{ fontSize: '14px', color: 'var(--text-color)', opacity: 0.7 }}>Ngày: {item.date}</span>
                            </div>
                            <div style={styles.scoreBadge(item.score)}>{item.score} Điểm</div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default InterviewPage;