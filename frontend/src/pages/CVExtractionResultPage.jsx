import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

/**
 * CVExtractionResultPage — Human-in-the-loop OCR review.
 * Receives extraction data via location.state from CVUploadPage.
 */
const CVExtractionResultPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const extractionData = location.state?.extractionData;

    const [activeSection, setActiveSection] = useState('personal');

    if (!extractionData) {
        return (
            <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
                <Navbar />
                <div style={styles.container}>
                    <div style={styles.emptyState}>
                        <p className="title-md">Không có dữ liệu CV</p>
                        <p style={{color: 'var(--muted)', marginBottom: 'var(--sp-lg)'}}>Vui lòng upload CV trước.</p>
                        <button className="btn-primary" onClick={() => navigate('/cv-upload')}>Upload CV</button>
                    </div>
                </div>
            </div>
        );
    }

    const { cv_id, personal_info, education, experience, projects, skills_matrix, certifications, languages } = extractionData;

    const sections = [
        { key: 'personal', label: 'Thông tin cá nhân' },
        { key: 'education', label: 'Học vấn' },
        { key: 'experience', label: 'Kinh nghiệm' },
        { key: 'projects', label: 'Dự án' },
        { key: 'skills', label: 'Kỹ năng' },
    ];

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <div style={styles.header}>
                    <div>
                        <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>KẾT QUẢ TRÍCH XUẤT CV</p>
                        <h1 className="display-sm">Xem lại thông tin CV</h1>
                        <p style={{color: 'var(--muted)', marginTop: 'var(--sp-xs)', fontSize: '14px'}}>
                            CV ID: <code style={{backgroundColor: 'var(--surface-strong)', padding: '2px 6px', borderRadius: 'var(--rounded-xs)', fontSize: '12px'}}>{cv_id}</code>
                        </p>
                    </div>
                </div>

                {/* Section Tabs */}
                <div style={styles.tabRow}>
                    {sections.map(s => (
                        <button
                            key={s.key}
                            className={activeSection === s.key ? 'badge-pill' : ''}
                            style={{
                                ...styles.tabBtn,
                                backgroundColor: activeSection === s.key ? 'var(--primary)' : 'transparent',
                                color: activeSection === s.key ? 'var(--on-primary)' : 'var(--muted)',
                            }}
                            onClick={() => setActiveSection(s.key)}
                        >
                            {s.label}
                        </button>
                    ))}
                </div>

                {/* Personal Info */}
                {activeSection === 'personal' && personal_info && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>Thông tin cá nhân</h3>
                        <div style={styles.fieldGrid}>
                            {[
                                { label: 'Họ tên', value: personal_info.name },
                                { label: 'Email', value: personal_info.email },
                                { label: 'Số điện thoại', value: personal_info.phone },
                                { label: 'LinkedIn', value: personal_info.linkedin },
                                { label: 'Địa điểm', value: personal_info.location },
                            ].map(f => (
                                <div key={f.label} style={styles.field}>
                                    <span style={styles.fieldLabel}>{f.label}</span>
                                    <span style={styles.fieldValue}>{f.value || '—'}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Education */}
                {activeSection === 'education' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>Học vấn</h3>
                        {education?.length > 0 ? education.map((edu, i) => (
                            <div key={i} style={styles.entryBlock}>
                                <div style={styles.entryHeader}>
                                    <strong>{edu.school}</strong>
                                    <span className="caption" style={{color: 'var(--muted)'}}>{edu.period}</span>
                                </div>
                                <p style={{color: 'var(--body)', fontSize: '14px'}}>{edu.degree} — {edu.major}</p>
                                {edu.gpa && <p style={{color: 'var(--muted)', fontSize: '13px'}}>GPA: {edu.gpa}</p>}
                            </div>
                        )) : <p style={{color: 'var(--muted)'}}>Không tìm thấy thông tin học vấn.</p>}
                    </div>
                )}

                {/* Experience */}
                {activeSection === 'experience' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>Kinh nghiệm</h3>
                        {experience?.length > 0 ? experience.map((exp, i) => (
                            <div key={i} style={styles.entryBlock}>
                                <div style={styles.entryHeader}>
                                    <strong>{exp.title}</strong>
                                    <span className="caption" style={{color: 'var(--muted)'}}>{exp.period}</span>
                                </div>
                                <p style={{color: 'var(--body)', fontSize: '14px', marginBottom: 'var(--sp-xs)'}}>{exp.company}</p>
                                {exp.tech_stack?.length > 0 && (
                                    <div style={styles.tagRow}>
                                        {exp.tech_stack.map((t, j) => <span key={j} className="badge-pill" style={{fontSize: '10px'}}>{t}</span>)}
                                    </div>
                                )}
                                {exp.descriptions?.length > 0 && (
                                    <ul style={styles.bulletList}>
                                        {exp.descriptions.map((d, j) => <li key={j}>{d}</li>)}
                                    </ul>
                                )}
                            </div>
                        )) : <p style={{color: 'var(--muted)'}}>Không tìm thấy kinh nghiệm.</p>}
                    </div>
                )}

                {/* Projects */}
                {activeSection === 'projects' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>Dự án</h3>
                        {projects?.length > 0 ? projects.map((proj, i) => (
                            <div key={i} style={styles.entryBlock}>
                                <strong>{proj.name}</strong>
                                {proj.role && <p style={{color: 'var(--muted)', fontSize: '13px'}}>Vai trò: {proj.role}</p>}
                                <p style={{color: 'var(--body)', fontSize: '14px', marginTop: 'var(--sp-xxs)'}}>{proj.description}</p>
                                {proj.tech_stack?.length > 0 && (
                                    <div style={styles.tagRow}>
                                        {proj.tech_stack.map((t, j) => <span key={j} className="badge-pill" style={{fontSize: '10px'}}>{t}</span>)}
                                    </div>
                                )}
                            </div>
                        )) : <p style={{color: 'var(--muted)'}}>Không tìm thấy dự án.</p>}
                    </div>
                )}

                {/* Skills */}
                {activeSection === 'skills' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>Kỹ năng</h3>
                        {[
                            { label: 'Ngôn ngữ lập trình', items: skills_matrix?.languages },
                            { label: 'Frameworks', items: skills_matrix?.frameworks },
                            { label: 'Công cụ', items: skills_matrix?.tools },
                            { label: 'Kỹ năng mềm', items: skills_matrix?.soft_skills },
                        ].map(group => (
                            <div key={group.label} style={{marginBottom: 'var(--sp-base)'}}>
                                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>{group.label}</p>
                                <div style={styles.tagRow}>
                                    {group.items?.length > 0
                                        ? group.items.map((s, i) => <span key={i} className="badge-pill">{s}</span>)
                                        : <span style={{color: 'var(--muted-soft)', fontSize: '13px'}}>—</span>
                                    }
                                </div>
                            </div>
                        ))}
                        {certifications?.length > 0 && (
                            <div style={{marginBottom: 'var(--sp-base)'}}>
                                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>CHỨNG CHỈ</p>
                                <div style={styles.tagRow}>
                                    {certifications.map((c, i) => <span key={i} className="badge-pill">{c}</span>)}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* Action Buttons */}
                <div style={styles.actions}>
                    <button className="btn-primary" onClick={() => navigate('/cv-optimization', { state: { cvId: cv_id } })}>
                        Phân tích & Tối ưu CV
                    </button>
                    <button className="btn-outline" onClick={() => navigate('/job-matching', { state: { cvId: cv_id } })}>
                        So khớp với JD
                    </button>
                    <button className="btn-outline" style={{ marginLeft: 'auto' }} onClick={() => navigate('/cv-upload')}>
                        Upload CV khác
                    </button>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: 'var(--sp-xl) var(--sp-lg)' },
    header: { marginBottom: 'var(--sp-xl)' },
    emptyState: { textAlign: 'center', padding: 'var(--sp-section) 0' },
    tabRow: { display: 'flex', gap: 'var(--sp-xs)', marginBottom: 'var(--sp-lg)', flexWrap: 'wrap' },
    tabBtn: {
        padding: '6px 14px', border: 'none', borderRadius: 'var(--rounded-pill)',
        cursor: 'pointer', fontSize: '13px', fontWeight: 500, fontFamily: 'var(--font-body)',
        transition: 'all var(--transition-fast)',
    },
    sectionCard: { padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)' },
    fieldGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 'var(--sp-xl)' },
    field: { display: 'flex', flexDirection: 'column', gap: 'var(--sp-xxs)' },
    fieldLabel: { fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.96px', color: 'var(--muted)' },
    fieldValue: { fontSize: '15px', color: 'var(--ink)' },
    entryBlock: { padding: 'var(--sp-base) 0', borderBottom: '1px solid var(--hairline-soft)' },
    entryHeader: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--sp-xxs)' },
    tagRow: { display: 'flex', flexWrap: 'wrap', gap: 'var(--sp-xs)', marginTop: 'var(--sp-xs)' },
    bulletList: { marginTop: 'var(--sp-xs)', paddingLeft: 'var(--sp-lg)', color: 'var(--body)', fontSize: '14px', lineHeight: 1.6 },
    actions: { display: 'flex', gap: 'var(--sp-sm)', flexWrap: 'wrap', marginTop: 'var(--sp-lg)' },
};

export default CVExtractionResultPage;
