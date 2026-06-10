import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

/**
 * CVExtractionResultPage — Human-in-the-loop OCR review.
 * Receives extraction data via location.state from CVUploadPage.
 * Supports inline editing of all extracted fields.
 */
const CVExtractionResultPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const extractionData = location.state?.extractionData;
    const rawText = location.state?.rawText || '';

    const [activeSection, setActiveSection] = useState('personal');
    const [showRawText, setShowRawText] = useState(false);
    const [editData, setEditData] = useState(extractionData ? { ...extractionData } : null);

    if (!editData) {
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

    const { cv_id, personal_info, education, experience, projects, skills_matrix, certifications, languages } = editData;

    // ── Helpers for inline editing ──────────────────────────────────────

    const updatePersonal = (field, value) => {
        setEditData(prev => ({
            ...prev,
            personal_info: { ...prev.personal_info, [field]: value },
        }));
    };

    const updateArrayField = (section, index, field, value) => {
        setEditData(prev => {
            const arr = [...prev[section]];
            arr[index] = { ...arr[index], [field]: value };
            return { ...prev, [section]: arr };
        });
    };

    const updateSkillsMatrix = (category, value) => {
        const items = value.split(',').map(s => s.trim()).filter(Boolean);
        setEditData(prev => ({
            ...prev,
            skills_matrix: { ...prev.skills_matrix, [category]: items },
        }));
    };

    const updateListField = (field, value) => {
        const items = value.split(',').map(s => s.trim()).filter(Boolean);
        setEditData(prev => ({
            ...prev,
            [field]: items,
        }));
    };

    const updateExperienceListField = (index, field, value) => {
        const items = value.split('\n').map(s => s.trim()).filter(Boolean);
        setEditData(prev => {
            const arr = [...prev.experience];
            arr[index] = { ...arr[index], [field]: items };
            return { ...prev, experience: arr };
        });
    };

    const updateExperienceCommaField = (index, field, value) => {
        const items = value.split(',').map(s => s.trim()).filter(Boolean);
        setEditData(prev => {
            const arr = [...prev.experience];
            arr[index] = { ...arr[index], [field]: items };
            return { ...prev, experience: arr };
        });
    };

    const updateProjectCommaField = (index, field, value) => {
        const items = value.split(',').map(s => s.trim()).filter(Boolean);
        setEditData(prev => {
            const arr = [...prev.projects];
            arr[index] = { ...arr[index], [field]: items };
            return { ...prev, projects: arr };
        });
    };

    // ── Section tabs ────────────────────────────────────────────────────

    const sections = [
        { key: 'personal', label: 'Thông tin cá nhân' },
        { key: 'education', label: 'Học vấn' },
        { key: 'experience', label: 'Kinh nghiệm' },
        { key: 'projects', label: 'Dự án' },
        { key: 'skills', label: 'Kỹ năng' },
    ];

    // ── Confidence hint ────────────────────────────────────────────────

    const ConfidenceHint = ({ hasContent }) => (
        <span style={{
            display: 'inline-flex', alignItems: 'center', gap: '4px',
            fontSize: '11px', fontWeight: 600, padding: '2px 8px',
            borderRadius: 'var(--rounded-pill)',
            backgroundColor: hasContent ? 'rgba(22,163,74,0.1)' : 'rgba(239,68,68,0.1)',
            color: hasContent ? 'var(--semantic-success)' : 'var(--semantic-error)',
            marginLeft: 'var(--sp-sm)',
        }}>
            {hasContent ? '✓ Trích xuất thành công' : '⚠ Cần xem lại'}
        </span>
    );

    // ── Editable field component ────────────────────────────────────────

    const EditableField = ({ label, value, onChange, multiline = false }) => (
        <div style={styles.field}>
            <span style={styles.fieldLabel}>{label}</span>
            {multiline ? (
                <textarea
                    className="text-input"
                    style={{ minHeight: '60px', fontSize: '14px' }}
                    value={value || ''}
                    onChange={e => onChange(e.target.value)}
                />
            ) : (
                <input
                    className="text-input"
                    style={{ fontSize: '14px', height: '36px', padding: '6px 12px' }}
                    value={value || ''}
                    onChange={e => onChange(e.target.value)}
                />
            )}
        </div>
    );

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
                            <span style={{marginLeft: 'var(--sp-sm)', fontSize: '12px', color: 'var(--muted-soft)'}}>
                                Bấm vào giá trị để chỉnh sửa
                            </span>
                        </p>
                    </div>
                    {/* Raw text toggle */}
                    {rawText && (
                        <button
                            className="btn-outline"
                            onClick={() => setShowRawText(prev => !prev)}
                            style={{ fontSize: '13px', flexShrink: 0 }}
                        >
                            {showRawText ? 'Ẩn văn bản gốc' : '📄 Xem văn bản gốc'}
                        </button>
                    )}
                </div>

                {/* Raw text preview */}
                {showRawText && rawText && (
                    <div style={styles.rawTextBox}>
                        <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>VĂN BẢN GỐC (OCR / TEXT LAYER)</p>
                        <pre style={styles.rawTextPre}>{rawText}</pre>
                    </div>
                )}

                {/* Section Tabs */}
                <div style={styles.tabRow}>
                    {sections.map(s => (
                        <button
                            key={s.key}
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
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>
                            Thông tin cá nhân
                            <ConfidenceHint hasContent={!!personal_info.name} />
                        </h3>
                        <div style={styles.fieldGrid}>
                            <EditableField label="Họ tên" value={personal_info.name} onChange={v => updatePersonal('name', v)} />
                            <EditableField label="Email" value={personal_info.email} onChange={v => updatePersonal('email', v)} />
                            <EditableField label="Số điện thoại" value={personal_info.phone} onChange={v => updatePersonal('phone', v)} />
                            <EditableField label="LinkedIn" value={personal_info.linkedin} onChange={v => updatePersonal('linkedin', v)} />
                            <EditableField label="Địa điểm" value={personal_info.location} onChange={v => updatePersonal('location', v)} />
                        </div>
                    </div>
                )}

                {/* Education */}
                {activeSection === 'education' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>
                            Học vấn
                            <ConfidenceHint hasContent={education?.length > 0} />
                        </h3>
                        {education?.length > 0 ? education.map((edu, i) => (
                            <div key={i} style={styles.entryBlock}>
                                <div style={styles.fieldGrid}>
                                    <EditableField label="Trường" value={edu.school} onChange={v => updateArrayField('education', i, 'school', v)} />
                                    <EditableField label="Bằng cấp" value={edu.degree} onChange={v => updateArrayField('education', i, 'degree', v)} />
                                    <EditableField label="Chuyên ngành" value={edu.major} onChange={v => updateArrayField('education', i, 'major', v)} />
                                    <EditableField label="GPA" value={edu.gpa} onChange={v => updateArrayField('education', i, 'gpa', v)} />
                                    <EditableField label="Thời gian" value={edu.period} onChange={v => updateArrayField('education', i, 'period', v)} />
                                </div>
                            </div>
                        )) : <p style={{color: 'var(--muted)'}}>Không tìm thấy thông tin học vấn.</p>}
                    </div>
                )}

                {/* Experience */}
                {activeSection === 'experience' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>
                            Kinh nghiệm
                            <ConfidenceHint hasContent={experience?.length > 0} />
                        </h3>
                        {experience?.length > 0 ? experience.map((exp, i) => (
                            <div key={i} style={styles.entryBlock}>
                                <div style={styles.fieldGrid}>
                                    <EditableField label="Vị trí" value={exp.title} onChange={v => updateArrayField('experience', i, 'title', v)} />
                                    <EditableField label="Công ty" value={exp.company} onChange={v => updateArrayField('experience', i, 'company', v)} />
                                    <EditableField label="Thời gian" value={exp.period} onChange={v => updateArrayField('experience', i, 'period', v)} />
                                </div>
                                <div style={{ marginTop: 'var(--sp-sm)', display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--sp-sm)' }}>
                                    <EditableField
                                        label="Công nghệ sử dụng (Phân cách bằng dấu phẩy)"
                                        value={(exp.tech_stack || []).join(', ')}
                                        onChange={v => updateExperienceCommaField(i, 'tech_stack', v)}
                                    />
                                    <EditableField
                                        label="Chi tiết công việc (Mỗi dòng một ý)"
                                        value={(exp.descriptions || []).join('\n')}
                                        onChange={v => updateExperienceListField(i, 'descriptions', v)}
                                        multiline
                                    />
                                </div>
                                
                                {/* Live Preview */}
                                <div style={{ marginTop: 'var(--sp-sm)', padding: 'var(--sp-sm)', backgroundColor: 'var(--canvas-soft)', borderRadius: 'var(--rounded-md)', border: '1px dashed var(--hairline)' }}>
                                    <p style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '4px' }}>Xem trước dữ liệu trích xuất:</p>
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
                            </div>
                        )) : <p style={{color: 'var(--muted)'}}>Không tìm thấy kinh nghiệm.</p>}
                    </div>
                )}

                {/* Projects */}
                {activeSection === 'projects' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>
                            Dự án
                            <ConfidenceHint hasContent={projects?.length > 0} />
                        </h3>
                        {projects?.length > 0 ? projects.map((proj, i) => (
                            <div key={i} style={styles.entryBlock}>
                                <div style={styles.fieldGrid}>
                                    <EditableField label="Tên dự án" value={proj.name} onChange={v => updateArrayField('projects', i, 'name', v)} />
                                    <EditableField label="Vai trò" value={proj.role} onChange={v => updateArrayField('projects', i, 'role', v)} />
                                </div>
                                <div style={{ marginTop: 'var(--sp-sm)' }}>
                                    <EditableField label="Mô tả" value={proj.description} onChange={v => updateArrayField('projects', i, 'description', v)} multiline />
                                </div>
                                <div style={{ marginTop: 'var(--sp-sm)' }}>
                                    <EditableField
                                        label="Công nghệ sử dụng (Phân cách bằng dấu phẩy)"
                                        value={(proj.tech_stack || []).join(', ')}
                                        onChange={v => updateProjectCommaField(i, 'tech_stack', v)}
                                    />
                                </div>

                                {/* Live Preview */}
                                <div style={{ marginTop: 'var(--sp-sm)', padding: 'var(--sp-sm)', backgroundColor: 'var(--canvas-soft)', borderRadius: 'var(--rounded-md)', border: '1px dashed var(--hairline)' }}>
                                    <p style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '4px' }}>Xem trước:</p>
                                    {proj.tech_stack?.length > 0 && (
                                        <div style={styles.tagRow}>
                                            {proj.tech_stack.map((t, j) => <span key={j} className="badge-pill" style={{fontSize: '10px'}}>{t}</span>)}
                                        </div>
                                    )}
                                </div>
                            </div>
                        )) : <p style={{color: 'var(--muted)'}}>Không tìm thấy dự án.</p>}
                    </div>
                )}

                {/* Skills */}
                {activeSection === 'skills' && (
                    <div className="card" style={styles.sectionCard}>
                        <h3 className="title-md" style={{marginBottom: 'var(--sp-base)'}}>
                            Kỹ năng & Thông tin khác
                            <ConfidenceHint hasContent={
                                (skills_matrix?.languages?.length > 0) ||
                                (skills_matrix?.frameworks?.length > 0) ||
                                (skills_matrix?.tools?.length > 0) ||
                                (certifications?.length > 0) ||
                                (languages?.length > 0)
                            } />
                        </h3>
                        {[
                            { label: 'Ngôn ngữ lập trình', key: 'languages', items: skills_matrix?.languages },
                            { label: 'Frameworks / Thư viện', key: 'frameworks', items: skills_matrix?.frameworks },
                            { label: 'Công cụ / Hệ điều hành', key: 'tools', items: skills_matrix?.tools },
                            { label: 'Kỹ năng mềm', key: 'soft_skills', items: skills_matrix?.soft_skills },
                        ].map(group => (
                            <div key={group.label} style={{marginBottom: 'var(--sp-base)'}}>
                                <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>{group.label}</p>
                                <input
                                    className="text-input"
                                    style={{ fontSize: '13px', height: '36px', padding: '6px 12px' }}
                                    value={(group.items || []).join(', ')}
                                    onChange={e => updateSkillsMatrix(group.key, e.target.value)}
                                    placeholder={`Nhập ${group.label.toLowerCase()}, phân cách bằng dấu phẩy`}
                                />
                            </div>
                        ))}
                        
                        <div style={{marginBottom: 'var(--sp-base)'}}>
                            <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>Chứng chỉ / Giải thưởng</p>
                            <input
                                className="text-input"
                                style={{ fontSize: '13px', height: '36px', padding: '6px 12px' }}
                                value={(certifications || []).join(', ')}
                                onChange={e => updateListField('certifications', e.target.value)}
                                placeholder="Nhập chứng chỉ, phân cách bằng dấu phẩy"
                            />
                        </div>

                        <div style={{marginBottom: 'var(--sp-base)'}}>
                            <p className="caption-uppercase" style={{color: 'var(--muted)', marginBottom: 'var(--sp-xs)'}}>Ngoại ngữ</p>
                            <input
                                className="text-input"
                                style={{ fontSize: '13px', height: '36px', padding: '6px 12px' }}
                                value={(languages || []).join(', ')}
                                onChange={e => updateListField('languages', e.target.value)}
                                placeholder="Nhập ngoại ngữ, phân cách bằng dấu phẩy"
                            />
                        </div>

                        {/* Live Preview for Certifications & Languages */}
                        <div style={{ marginTop: 'var(--sp-sm)', padding: 'var(--sp-sm)', backgroundColor: 'var(--canvas-soft)', borderRadius: 'var(--rounded-md)', border: '1px dashed var(--hairline)' }}>
                            <p style={{ fontSize: '11px', fontWeight: 600, textTransform: 'uppercase', color: 'var(--muted)', marginBottom: '4px' }}>Xem trước chứng chỉ & ngoại ngữ:</p>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-xs)' }}>
                                {certifications?.length > 0 && (
                                    <div>
                                        <span style={{ fontSize: '12px', fontWeight: 500, marginRight: '8px' }}>Chứng chỉ:</span>
                                        {certifications.map((c, i) => <span key={i} className="badge-pill" style={{ marginRight: '4px' }}>{c}</span>)}
                                    </div>
                                )}
                                {languages?.length > 0 && (
                                    <div>
                                        <span style={{ fontSize: '12px', fontWeight: 500, marginRight: '8px' }}>Ngoại ngữ:</span>
                                        {languages.map((l, i) => <span key={i} className="badge-pill" style={{ marginRight: '4px' }}>{l}</span>)}
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

                {/* Action Buttons */}
                <div style={styles.actions}>
                    <button className="btn-primary" onClick={() => navigate('/cv-optimization', { state: { cvId: cv_id, editedData: editData } })}>
                        Phân tích & Tối ưu CV
                    </button>
                    <button className="btn-outline" onClick={() => navigate('/job-matching', { state: { cvId: cv_id } })}>
                        So khớp với JD
                    </button>
                    <button className="btn-outline" onClick={() => navigate('/cv-upload')}>
                        Upload CV khác
                    </button>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: { maxWidth: '800px', margin: '0 auto', padding: 'var(--sp-xl) var(--sp-lg)' },
    header: {
        marginBottom: 'var(--sp-xl)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 'var(--sp-base)',
    },
    emptyState: { textAlign: 'center', padding: 'var(--sp-section) 0' },
    tabRow: { display: 'flex', gap: 'var(--sp-xs)', marginBottom: 'var(--sp-lg)', flexWrap: 'wrap' },
    tabBtn: {
        padding: '6px 14px', border: 'none', borderRadius: 'var(--rounded-pill)',
        cursor: 'pointer', fontSize: '13px', fontWeight: 500, fontFamily: 'var(--font-body)',
        transition: 'all var(--transition-fast)',
    },
    sectionCard: { padding: 'var(--sp-xl)', marginBottom: 'var(--sp-lg)' },
    fieldGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--sp-sm)' },
    field: { display: 'flex', flexDirection: 'column', gap: 'var(--sp-xxs)' },
    fieldLabel: { fontSize: '12px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.96px', color: 'var(--muted)' },
    entryBlock: { padding: 'var(--sp-base) 0', borderBottom: '1px solid var(--hairline-soft)' },
    tagRow: { display: 'flex', flexWrap: 'wrap', gap: 'var(--sp-xs)', marginTop: 'var(--sp-xs)' },
    bulletList: { marginTop: 'var(--sp-xs)', paddingLeft: 'var(--sp-lg)', color: 'var(--body)', fontSize: '14px', lineHeight: 1.6 },
    actions: { display: 'flex', gap: 'var(--sp-sm)', flexWrap: 'wrap', marginTop: 'var(--sp-lg)' },
    rawTextBox: {
        marginBottom: 'var(--sp-xl)',
        padding: 'var(--sp-base)',
        backgroundColor: 'var(--surface-strong)',
        borderRadius: 'var(--rounded-lg)',
        border: '1px solid var(--hairline)',
    },
    rawTextPre: {
        whiteSpace: 'pre-wrap',
        wordBreak: 'break-word',
        fontFamily: 'monospace',
        fontSize: '12px',
        color: 'var(--body)',
        maxHeight: '300px',
        overflowY: 'auto',
        lineHeight: 1.5,
        margin: 0,
    },
};

export default CVExtractionResultPage;
