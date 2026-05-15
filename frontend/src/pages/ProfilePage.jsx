import React from 'react';
import Navbar from '../components/Layout/Navbar';

const ProfilePage = () => {
    // Dữ liệu giả (Mock Data) - Tương lai lấy từ API
    const interviewHistory = [
        { id: 'INT-001', name: 'Phỏng vấn Frontend Dev', date: '05/05/2026', note: 'Kỹ năng React tốt' },
        { id: 'INT-002', name: 'Phỏng vấn Backend Nodejs', date: '01/05/2026', note: 'Cần ôn lại SQL' }
    ];
    const cvHistory = []; // Mảng rỗng để test tính năng hiển thị thông báo

    const styles = {
        container: { padding: '40px', maxWidth: '1000px', margin: '0 auto', fontFamily: 'system-ui' },
        header: { display: 'flex', alignItems: 'center', gap: '20px', marginBottom: '40px' },
        avatar: { width: '80px', height: '80px', borderRadius: '50%', backgroundColor: '#3182ce', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '30px' },
        sectionTitle: { 
            fontSize: '20px', 
            borderBottom: '2px solid var(--border-color)', 
            paddingBottom: '10px', 
            marginBottom: '20px', 
            marginTop: '40px' 
        },
        table: { 
            width: '100%', 
            borderCollapse: 'collapse', 
            textAlign: 'left' 
        },
        th: { 
            padding: '12px', 
            borderBottom: '2px solid var(--border-color)', 
            background: 'var(--border-color)' 
        },
        td: { padding: '12px', borderBottom: '1px solid #e2e8f0' },
        link: { color: '#3182ce', textDecoration: 'none', fontWeight: 'bold' },
        emptyMsg: { padding: '20px', background: '#fefcbf', color: '#975a16', borderRadius: '8px', textAlign: 'center' },
        btnDelete: { background: 'none', border: 'none', cursor: 'pointer', fontSize: '16px' }
    };

    return (
        <div>
            <Navbar />
            <div style={styles.container}>
                <div style={styles.header}>
                    <div style={styles.avatar}>A</div>
                    <h2>Nguyễn Văn A</h2>
                </div>

                <h3 style={styles.sectionTitle}>Lịch sử phỏng vấn</h3>
                {interviewHistory.length > 0 ? (
                    <table style={styles.table}>
                        <thead>
                            <tr>
                                <th style={styles.th}>ID</th>
                                <th style={styles.th}>Tên cuộc phỏng vấn</th>
                                <th style={styles.th}>Thời gian</th>
                                <th style={styles.th}>Ghi chú</th>
                                <th style={styles.th}>Xóa</th>
                            </tr>
                        </thead>
                        <tbody>
                            {interviewHistory.map(item => (
                                <tr key={item.id}>
                                    <td style={styles.td}>{item.id}</td>
                                    <td style={styles.td}><a href="#" style={styles.link}>{item.name}</a></td>
                                    <td style={styles.td}>{item.date}</td>
                                    <td style={styles.td}>{item.note}</td>
                                    <td style={styles.td}><button style={styles.btnDelete} title="Xóa">🗑️</button></td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                ) : (
                    <div style={styles.emptyMsg}>Bạn chưa thực hiện cuộc phỏng vấn nào!</div>
                )}

                <h3 style={styles.sectionTitle}>Lịch sử đánh giá CV</h3>
                {cvHistory.length > 0 ? (
                    <table style={styles.table}>...</table>
                ) : (
                    <div style={styles.emptyMsg}>Chưa thực hiện đánh giá CV!</div>
                )}
            </div>
        </div>
    );
};

export default ProfilePage;