import React from 'react';
import Navbar from '../components/Layout/Navbar';

import member1 from '../assets/Members/nd.jpg';
import member2 from '../assets/Members/hd.jpg';
import member3 from '../assets/Members/cd.jpg';
import member4 from '../assets/Members/db.jpg';
import member5 from '../assets/Members/vh.jpg';

const AboutUsPage = () => {
    const teamMembers = [
        { id: 1, name: 'Phạm Ngọc Duy', mssv: '23122025', role: 'Project Manager (PM) & System Architect', img: member1 },
        { id: 2, name: 'Lê Hải Đăng', mssv: '23122005', role: 'Frontend Developer', img: member2 },
        { id: 3, name: 'Chung Tín Đạt', mssv: '23122024', role: 'Backend Developer', img: member3 },
        { id: 4, name: 'Bùi Duy Bảo', mssv: '23122021', role: 'AI Engineer (Local LLM, Speech-to-Text & Text-to-Speech)', img: member4 },
        { id: 5, name: 'Nguyễn Việt Hùng', mssv: '23122032', role: 'AI Engineer (RAG, CoT & prompt engineering)', img: member5 }
    ];

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <p className="caption-uppercase" style={{textAlign: 'center', color: 'var(--muted)', marginBottom: 'var(--sp-sm)'}}>
                    ĐỘI NGŨ PHÁT TRIỂN
                </p>
                <h1 className="display-lg" style={styles.title}>Danh sách thành viên</h1>
                
                <div style={styles.grid}>
                    {teamMembers.map(member => (
                        <div key={member.id} className="card" style={styles.memberCard}>
                            <img src={member.img} alt={member.name} style={styles.avatar} />
                            <div style={styles.infoBox}>
                                <h3 className="title-sm" style={{marginBottom: 'var(--sp-xxs)'}}>{member.name}</h3>
                                <span className="badge-pill" style={{marginBottom: 'var(--sp-xs)', fontSize: '10px'}}>
                                    MSSV: {member.mssv}
                                </span>
                                <p style={styles.role}>{member.role}</p>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '700px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg) var(--sp-section)',
    },
    title: {
        textAlign: 'center',
        marginBottom: 'var(--sp-xxl)',
    },
    grid: {
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-base)',
    },
    memberCard: {
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--sp-lg)',
        padding: 'var(--sp-lg)',
    },
    avatar: {
        width: '64px',
        height: '64px',
        borderRadius: 'var(--rounded-full)',
        objectFit: 'cover',
        border: '2px solid var(--hairline)',
        flexShrink: 0,
    },
    infoBox: {
        display: 'flex',
        flexDirection: 'column',
    },
    role: {
        fontSize: '13px',
        color: 'var(--muted)',
        lineHeight: 1.5,
        letterSpacing: '0.15px',
    },
};

export default AboutUsPage;