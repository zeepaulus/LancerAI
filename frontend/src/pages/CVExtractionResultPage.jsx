import React, { useEffect, useMemo, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { CVDocumentGraphic } from '../components/Common/Visuals';
import { getCV, updateCVExtraction } from '../api/extraction';

const emptyExtraction = {
    personal_info: { name: '', email: '', phone: '', linkedin: '', location: '' },
    education: [],
    experience: [],
    projects: [],
    skills_matrix: { languages: [], frameworks: [], tools: [], soft_skills: [] },
    certifications: [],
    languages: [],
};

const educationTemplate = { school: '', degree: '', major: '', gpa: '', period: '' };
const experienceTemplate = {
    company: '',
    title: '',
    period: '',
    descriptions: [],
    key_impacts: [],
    tech_stack: [],
};
const projectTemplate = {
    name: '',
    role: '',
    tech_stack: [],
    description: '',
    key_impacts: [],
};

function normalizeExtraction(data = {}) {
    return {
        ...emptyExtraction,
        ...data,
        personal_info: { ...emptyExtraction.personal_info, ...(data.personal_info || {}) },
        skills_matrix: { ...emptyExtraction.skills_matrix, ...(data.skills_matrix || {}) },
        education: Array.isArray(data.education) ? data.education : [],
        experience: Array.isArray(data.experience) ? data.experience : [],
        projects: Array.isArray(data.projects) ? data.projects : [],
        certifications: Array.isArray(data.certifications) ? data.certifications : [],
        languages: Array.isArray(data.languages) ? data.languages : [],
    };
}

function textToList(value) {
    return String(value || '')
        .split(',')
        .map((item) => item.trim())
        .filter(Boolean);
}

function listToText(value) {
    return Array.isArray(value) ? value.join(', ') : '';
}

const Field = ({ label, value, onChange, placeholder = '', multiline = false, rows = 3 }) => (
    <label className="ui-field">
        <span>{label}</span>
        {multiline ? (
            <textarea
                className="text-input"
                value={value || ''}
                placeholder={placeholder}
                rows={rows}
                onChange={(event) => onChange(event.target.value)}
            />
        ) : (
            <input
                className="text-input"
                value={value || ''}
                placeholder={placeholder}
                onChange={(event) => onChange(event.target.value)}
            />
        )}
    </label>
);

const SectionList = ({ title, items, template, onChange, children }) => {
    const addItem = () => onChange([...(items || []), { ...template }]);
    const updateItem = (index, patch) => {
        onChange(items.map((item, itemIndex) => (itemIndex === index ? { ...item, ...patch } : item)));
    };
    const removeItem = (index) => {
        onChange(items.filter((_, itemIndex) => itemIndex !== index));
    };

    return (
        <div className="ui-stack ui-stack--sm cv-extraction-editor">
            <div className="ui-spread">
                <strong className="ui-row-title">{title}</strong>
                <button className="btn-outline" type="button" onClick={addItem}>Thêm</button>
            </div>
            {(items || []).length === 0 ? (
                <p className="caption">Chưa có dữ liệu. Bạn có thể thêm thủ công nếu OCR bỏ sót.</p>
            ) : (
                items.map((item, index) => (
                    <div className="card ui-stack ui-stack--sm cv-extraction-item" key={`${title}-${index}`}>
                        <div className="ui-spread">
                            <StatusBadge tone="ai">#{index + 1}</StatusBadge>
                            <button className="btn-outline" type="button" onClick={() => removeItem(index)}>Xóa</button>
                        </div>
                        {children(item, (patch) => updateItem(index, patch))}
                    </div>
                ))
            )}
        </div>
    );
};

const CVExtractionResultPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const initialData = location.state?.extractionData || null;
    const cvId = location.state?.cvId || initialData?.cv_id;
    const [formData, setFormData] = useState(() => normalizeExtraction(initialData || {}));
    const [loading, setLoading] = useState(Boolean(cvId && !initialData));
    const [saving, setSaving] = useState(false);
    const [errorMsg, setErrorMsg] = useState('');

    useEffect(() => {
        let ignore = false;
        if (!cvId || initialData) return undefined;

        setLoading(true);
        getCV(cvId)
            .then((data) => {
                if (!ignore) setFormData(normalizeExtraction(data));
            })
            .catch((err) => {
                if (!ignore) setErrorMsg(err?.message || 'Không tải được dữ liệu CV đã bóc tách.');
            })
            .finally(() => {
                if (!ignore) setLoading(false);
            });

        return () => {
            ignore = true;
        };
    }, [cvId, initialData]);

    const extractedCount = useMemo(() => {
        const skills = formData.skills_matrix || {};
        return (
            Object.values(formData.personal_info || {}).filter(Boolean).length
            + (formData.education || []).length
            + (formData.experience || []).length
            + (formData.projects || []).length
            + Object.values(skills).reduce((total, list) => total + (Array.isArray(list) ? list.length : 0), 0)
        );
    }, [formData]);

    const updateRoot = (patch) => setFormData((current) => ({ ...current, ...patch }));
    const updatePersonal = (field, value) => {
        setFormData((current) => ({
            ...current,
            personal_info: { ...current.personal_info, [field]: value },
        }));
    };
    const updateSkills = (field, value) => {
        setFormData((current) => ({
            ...current,
            skills_matrix: { ...current.skills_matrix, [field]: textToList(value) },
        }));
    };

    const handleSaveAndAnalyze = async () => {
        if (!cvId) return;
        setSaving(true);
        setErrorMsg('');
        try {
            const payload = normalizeExtraction(formData);
            delete payload.cv_id;
            await updateCVExtraction(cvId, payload);
            navigate('/cv-optimization', { state: { cvId } });
        } catch (err) {
            setErrorMsg(err?.message || 'Không lưu được dữ liệu đã chỉnh. Vui lòng thử lại.');
        } finally {
            setSaving(false);
        }
    };

    if (!cvId) {
        return (
            <div className="app-screen">
                <Navbar />
                <Page narrow>
                    <EmptyState
                        visual={<CVDocumentGraphic />}
                        title="Chưa có CV để kiểm tra"
                        description="Hãy tải CV lên trước, sau đó LancerAI sẽ hiển thị dữ liệu đã bóc tách để bạn chỉnh lại."
                        action={<button className="btn-primary" onClick={() => navigate('/cv-upload')}>Tải CV</button>}
                    />
                </Page>
            </div>
        );
    }

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Kiểm tra OCR"
                    title="Duyệt thông tin đã bóc tách"
                    description="Bạn có thể sửa dữ liệu OCR/LLM trước khi chạy đánh giá CV để kết quả phân tích bám đúng nội dung thật."
                    visual={<CVDocumentGraphic />}
                    tone="cv"
                    actions={(
                        <>
                            <button className="btn-outline" onClick={() => navigate('/cv-upload')}>Tải CV khác</button>
                            <button className="btn-primary" onClick={handleSaveAndAnalyze} disabled={saving || loading}>
                                {saving ? 'Đang lưu...' : 'Lưu và phân tích'}
                            </button>
                        </>
                    )}
                />

                {errorMsg && <div className="ui-error-box">{errorMsg}</div>}

                <div className="dashboard-grid cv-extraction-grid">
                    <Panel className="span-12" title="Thông tin cá nhân" subtitle={`Đã nhận diện khoảng ${extractedCount} mục dữ liệu. Hãy sửa các mục OCR đọc sai trước khi đánh giá.`}>
                        {loading ? (
                            <p className="caption">Đang tải dữ liệu đã bóc tách...</p>
                        ) : (
                            <div className="form-grid">
                                <Field label="Họ tên" value={formData.personal_info.name} onChange={(value) => updatePersonal('name', value)} />
                                <Field label="Email" value={formData.personal_info.email} onChange={(value) => updatePersonal('email', value)} />
                                <Field label="Số điện thoại" value={formData.personal_info.phone} onChange={(value) => updatePersonal('phone', value)} />
                                <Field label="LinkedIn" value={formData.personal_info.linkedin} onChange={(value) => updatePersonal('linkedin', value)} />
                                <Field label="Địa điểm" value={formData.personal_info.location} onChange={(value) => updatePersonal('location', value)} />
                            </div>
                        )}
                    </Panel>

                    <Panel className="span-6" title="Học vấn">
                        <SectionList
                            title="Education"
                            items={formData.education}
                            template={educationTemplate}
                            onChange={(education) => updateRoot({ education })}
                        >
                            {(item, update) => (
                                <div className="form-grid">
                                    <Field label="Trường" value={item.school} onChange={(value) => update({ school: value })} />
                                    <Field label="Bằng cấp" value={item.degree} onChange={(value) => update({ degree: value })} />
                                    <Field label="Chuyên ngành" value={item.major} onChange={(value) => update({ major: value })} />
                                    <Field label="GPA" value={item.gpa} onChange={(value) => update({ gpa: value })} />
                                    <Field label="Thời gian" value={item.period} onChange={(value) => update({ period: value })} />
                                </div>
                            )}
                        </SectionList>
                    </Panel>

                    <Panel className="span-6" title="Kỹ năng">
                        <div className="ui-stack ui-stack--sm">
                            <Field label="Ngôn ngữ lập trình" placeholder="Python, JavaScript, SQL" value={listToText(formData.skills_matrix.languages)} onChange={(value) => updateSkills('languages', value)} />
                            <Field label="Frameworks" placeholder="React, FastAPI, Django" value={listToText(formData.skills_matrix.frameworks)} onChange={(value) => updateSkills('frameworks', value)} />
                            <Field label="Tools" placeholder="Git, Docker, AWS" value={listToText(formData.skills_matrix.tools)} onChange={(value) => updateSkills('tools', value)} />
                            <Field label="Kỹ năng mềm" placeholder="Teamwork, Communication" value={listToText(formData.skills_matrix.soft_skills)} onChange={(value) => updateSkills('soft_skills', value)} />
                        </div>
                    </Panel>

                    <Panel className="span-12" title="Kinh nghiệm">
                        <SectionList
                            title="Experience"
                            items={formData.experience}
                            template={experienceTemplate}
                            onChange={(experience) => updateRoot({ experience })}
                        >
                            {(item, update) => (
                                <div className="form-grid">
                                    <Field label="Công ty" value={item.company} onChange={(value) => update({ company: value })} />
                                    <Field label="Chức danh" value={item.title} onChange={(value) => update({ title: value })} />
                                    <Field label="Thời gian" value={item.period} onChange={(value) => update({ period: value })} />
                                    <Field label="Mô tả" multiline rows={3} value={listToText(item.descriptions)} onChange={(value) => update({ descriptions: textToList(value) })} />
                                    <Field label="Kết quả/impact" placeholder="Giảm 30% thời gian xử lý, tăng 15% conversion" value={listToText(item.key_impacts)} onChange={(value) => update({ key_impacts: textToList(value) })} />
                                    <Field label="Tech stack" placeholder="React, FastAPI, PostgreSQL" value={listToText(item.tech_stack)} onChange={(value) => update({ tech_stack: textToList(value) })} />
                                </div>
                            )}
                        </SectionList>
                    </Panel>

                    <Panel className="span-12" title="Dự án">
                        <SectionList
                            title="Projects"
                            items={formData.projects}
                            template={projectTemplate}
                            onChange={(projects) => updateRoot({ projects })}
                        >
                            {(item, update) => (
                                <div className="form-grid">
                                    <Field label="Tên dự án" value={item.name} onChange={(value) => update({ name: value })} />
                                    <Field label="Vai trò" value={item.role} onChange={(value) => update({ role: value })} />
                                    <Field label="Mô tả" multiline rows={3} value={item.description} onChange={(value) => update({ description: value })} />
                                    <Field label="Tech stack" placeholder="React, Node.js, MongoDB" value={listToText(item.tech_stack)} onChange={(value) => update({ tech_stack: textToList(value) })} />
                                    <Field label="Kết quả/impact" placeholder="500 users, giảm 20% lỗi nhập liệu" value={listToText(item.key_impacts)} onChange={(value) => update({ key_impacts: textToList(value) })} />
                                </div>
                            )}
                        </SectionList>
                    </Panel>

                    <Panel className="span-6" title="Chứng chỉ">
                        <Field
                            label="Cách nhau bằng dấu phẩy"
                            placeholder="AWS Cloud Practitioner, IELTS 7.0"
                            value={listToText(formData.certifications)}
                            onChange={(value) => updateRoot({ certifications: textToList(value) })}
                        />
                    </Panel>

                    <Panel className="span-6" title="Ngôn ngữ giao tiếp">
                        <Field
                            label="Cách nhau bằng dấu phẩy"
                            placeholder="Tiếng Việt, English"
                            value={listToText(formData.languages)}
                            onChange={(value) => updateRoot({ languages: textToList(value) })}
                        />
                    </Panel>
                </div>
            </Page>
        </div>
    );
};

export default CVExtractionResultPage;
