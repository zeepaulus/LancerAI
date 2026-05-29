import React from 'react';
import Navbar from '../components/Layout/Navbar';

const ProfilePage = () => {
    const interviewHistory = [
        { id: 'INT-001', name: 'Phỏng vấn Frontend Dev', date: '05/05/2026', note: 'Kỹ năng React tốt' },
        { id: 'INT-002', name: 'Phỏng vấn Backend Nodejs', date: '01/05/2026', note: 'Cần ôn lại SQL' }
    ];
    const cvHistory = [];

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                {/* Profile header */}
                <div style={styles.header}>
                    <div style={styles.avatar}>A</div>
                    <div>
                        <h2 className="display-sm">Nguyễn Văn A</h2>
                        <p style={{color: 'var(--muted)', fontSize: '14px', marginTop: 'var(--sp-xxs)'}}>Sinh viên IT</p>
                    </div>
                </div>

                {/* Interview History */}
                <div style={styles.sectionHeader}>
                    <p className="caption-uppercase" style={{color: 'var(--muted)'}}>LỊCH SỬ PHỎNG VẤN</p>
                </div>
                {interviewHistory.length > 0 ? (
                    <div className="card" style={{overflow: 'hidden', padding: 0, marginBottom: 'var(--sp-xl)'}}>
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
                                        <td style={styles.td}><span className="caption" style={{color: 'var(--muted)'}}>{item.id}</span></td>
                                        <td style={styles.td}><span style={{color: 'var(--ink)', fontWeight: 500, cursor: 'pointer'}}>{item.name}</span></td>
                                        <td style={styles.td}><span className="caption" style={{color: 'var(--muted)'}}>{item.date}</span></td>
                                        <td style={styles.td}><span className="caption">{item.note}</span></td>
                                        <td style={styles.td}>
                                            <button style={styles.btnIcon} title="Xóa">🗑️</button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div style={styles.emptyMsg}>Bạn chưa thực hiện cuộc phỏng vấn nào!</div>
                )}

                {/* CV History */}
                <div style={styles.sectionHeader}>
                    <p className="caption-uppercase" style={{color: 'var(--muted)'}}>LỊCH SỬ ĐÁNH GIÁ CV</p>
                </div>
                {cvHistory.length > 0 ? (
                    <div className="card" style={{overflow: 'hidden', padding: 0}}>
                        <table style={styles.table}>...</table>
                    </div>
                ) : (
                    <div style={styles.emptyMsg}>Chưa thực hiện đánh giá CV!</div>
                )}
            </div>
        </div>
    );
};

const styles = {
    container: {
        padding: 'var(--sp-xl) var(--sp-lg)',
        maxWidth: '1000px',
        margin: '0 auto',
    },
    header: {
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--sp-lg)',
        marginBottom: 'var(--sp-xxl)',
    },
    avatar: {
        width: '72px',
        height: '72px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        color: 'var(--ink)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        fontSize: '28px',
        fontFamily: 'var(--font-display)',
        fontWeight: 300,
        border: '2px solid var(--hairline)',
    },
    sectionHeader: {
        marginBottom: 'var(--sp-base)',
        paddingBottom: 'var(--sp-xs)',
    },
    table: {
        width: '100%',
        borderCollapse: 'collapse',
        textAlign: 'left',
    },
    th: {
        padding: 'var(--sp-sm) var(--sp-base)',
        backgroundColor: 'var(--surface-strong)',
        fontFamily: 'var(--font-body)',
        fontSize: '12px',
        fontWeight: 600,
        letterSpacing: '0.96px',
        textTransform: 'uppercase',
        color: 'var(--muted)',
        borderBottom: '1px solid var(--hairline)',
    },
    td: {
        padding: 'var(--sp-sm) var(--sp-base)',
        borderBottom: '1px solid var(--hairline-soft)',
        fontSize: '14px',
        color: 'var(--body)',
    },
    btnIcon: {
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        fontSize: '14px',
        padding: 'var(--sp-xxs)',
        borderRadius: 'var(--rounded-sm)',
        transition: 'background-color var(--transition-fast)',
    },
    emptyMsg: {
        padding: 'var(--sp-lg)',
        backgroundColor: 'var(--surface-strong)',
        color: 'var(--muted)',
        borderRadius: 'var(--rounded-xl)',
        textAlign: 'center',
        fontSize: '14px',
        marginBottom: 'var(--sp-xl)',
    },
};

export default ProfilePage;