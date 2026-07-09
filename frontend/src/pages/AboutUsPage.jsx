import React from 'react';
import Navbar from '../components/Layout/Navbar';
import { Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { ProductMockupGraphic } from '../components/Common/Visuals';

import member1 from '../assets/Members/nd.jpg';
import member2 from '../assets/Members/hd.jpg';
import member3 from '../assets/Members/cd.jpg';
import member4 from '../assets/Members/db.jpg';
import member5 from '../assets/Members/vh.jpg';

const teamMembers = [
    { id: 1, name: 'Pham Ngoc Duy', mssv: '23122025', role: 'Quản lý dự án và kiến trúc hệ thống', img: member1 },
    { id: 2, name: 'Le Hai Dang', mssv: '23122005', role: 'Frontend Developer', img: member2 },
    { id: 3, name: 'Chung Tin Dat', mssv: '23122024', role: 'Backend Developer', img: member3 },
    { id: 4, name: 'Bui Duy Bao', mssv: '23122021', role: 'AI Engineer: giọng nói và Local LLM', img: member4 },
    { id: 5, name: 'Nguyen Viet Hung', mssv: '23122032', role: 'AI Engineer: RAG và Prompt Engineering', img: member5 },
];

const AboutUsPage = () => (
    <div className="app-screen">
        <Navbar />
        <Page wide>
            <PageHero
                kicker="Giới thiệu LancerAI"
                title="Ứng dụng luyện CV và phỏng vấn cho ứng viên IT"
                description="LancerAI giúp trích xuất CV, so khớp mô tả công việc, luyện phỏng vấn giọng nói và xem báo cáo có điểm."
                visual={<ProductMockupGraphic variant="workspace" />}
                tone="ai"
                actions={<StatusBadge tone="ai">Đồ án sinh viên</StatusBadge>}
            />

            <div className="about-value-grid">
                {[
                    ['Luyện phỏng vấn giọng nói', 'Ứng viên trả lời bằng giọng nói và xem lại transcript sau phiên.'],
                    ['Đánh giá dựa trên CV', 'Báo cáo và so khớp dùng dữ liệu CV đã trích xuất thay vì chỉ nhập tay.'],
                    ['Ngân hàng câu hỏi IT', 'Câu hỏi được nhóm theo vai trò, cấp độ, chủ đề và độ khó.'],
                ].map(([title, description]) => (
                    <Panel key={title} title={title}>
                        <p className="caption">{description}</p>
                    </Panel>
                ))}
            </div>

            <Panel title="Nhóm phát triển" subtitle="Thành viên và vai trò trong dự án.">
                <div className="about-team-grid">
                    {teamMembers.map((member) => (
                        <article key={member.id} className="team-card">
                            <img src={member.img} alt={member.name} />
                            <div className="team-card__body">
                                <h3 className="title-sm">{member.name}</h3>
                                <p className="caption">MSSV: {member.mssv}</p>
                                <div className="chip-row ui-section-gap">
                                    <span>{member.role}</span>
                                </div>
                            </div>
                        </article>
                    ))}
                </div>
            </Panel>
        </Page>
    </div>
);

export default AboutUsPage;
