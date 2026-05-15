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

    const styles = {
        container: { 
            maxWidth: '600px', 
            margin: '40px auto', 
            padding: '0 20px', 
            fontFamily: 'system-ui' 
        },
        title: { 
            textAlign: 'center', 
            fontSize: '28px', 
            marginBottom: '40px', 
            color: 'var(--text-color)' 
        },
        card: { 
            display: 'flex', 
            alignItems: 'center', 
            padding: '20px', 
            border: '1px solid var(--border-color)', 
            borderRadius: '12px', 
            marginBottom: '20px', 
            boxShadow: '0 2px 4px rgba(0,0,0,0.05)', 
            background: 'var(--nav-bg)' 
        },
        avatar: { 
            width: '70px', 
            height: '70px', 
            borderRadius: '50%', 
            backgroundColor: '#4a5568', 
            color: 'white', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center', 
            fontSize: '24px', 
            marginRight: '20px' 
        },
        infoBox: { 
            display: 'flex', 
            flexDirection: 'column', 
            gap: '5px' 
        },
        name: { 
            fontSize: '18px', 
            fontWeight: 'bold', 
            margin: 0,
            color: 'var(--text-color)'
        },
        text: { 
            fontSize: '14px', 
            color: 'var(--text-color)', 
            margin: 0 
        }
    };

    return (
        <div style={{minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <h1 style={styles.title}>Danh sách thành viên</h1>
                
                {teamMembers.map(member => (
                    <div key={member.id} style={styles.card}>
                        {/* Thay thế khung tròn văn bản bằng thẻ img */}
                        <img src={member.img} alt={member.name} style={styles.avatar} />
                        <div style={styles.infoBox}>
                            <p style={styles.name}>{member.name}</p>
                            <p style={styles.text}><strong>MSSV:</strong> {member.mssv}</p>
                            <p style={styles.text}><strong>Vai trò:</strong> {member.role}</p>
                        </div>
                    </div>
                ))}

            </div>
        </div>
    );
};

export default AboutUsPage;