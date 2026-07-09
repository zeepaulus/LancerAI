import React, { useMemo, useState } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { EmptyState, Page, PageHero, Panel, StatusBadge } from '../components/Common/AppUI';
import { FeatureIcon, ProductMockupGraphic } from '../components/Common/Visuals';
import {
    DIFFICULTIES,
    IT_LEVELS,
    IT_ROLES,
    QUESTION_BANK,
    QUESTION_CATEGORIES,
    allQuestionTags,
} from '../data/questionBank';

const ALL = 'All';

function optionLabel(value) {
    return value === ALL ? 'Tất cả' : value;
}

function includesText(value, query) {
    return String(value || '').toLowerCase().includes(query.toLowerCase());
}

function difficultyTone(value) {
    if (value === 'Hard') return 'danger';
    if (value === 'Medium') return 'warning';
    return 'success';
}

const QuestionBankPage = () => {
    const location = useLocation();
    const preset = location.state?.preset || location.state?.jobPreset || {};

    const [query, setQuery] = useState('');
    const [role, setRole] = useState(preset.role || ALL);
    const [level, setLevel] = useState(preset.level || ALL);
    const [category, setCategory] = useState(preset.category || ALL);
    const [difficulty, setDifficulty] = useState(ALL);
    const [activeTag, setActiveTag] = useState(preset.tag || ALL);
    const [activeQuestion, setActiveQuestion] = useState(null);

    const tags = useMemo(() => allQuestionTags(), []);

    const filteredQuestions = useMemo(() => {
        const normalizedQuery = query.trim();
        return QUESTION_BANK.filter((item) => {
            const matchesQuery = !normalizedQuery
                || includesText(item.question_vi || item.question, normalizedQuery)
                || includesText(item.category, normalizedQuery)
                || includesText(item.role, normalizedQuery)
                || includesText(item.interviewer_expectation_vi, normalizedQuery)
                || item.tags.some((tag) => includesText(tag, normalizedQuery));
            const matchesRole = role === ALL || item.role === role;
            const matchesLevel = level === ALL || item.level === level;
            const matchesCategory = category === ALL || item.category === category;
            const matchesDifficulty = difficulty === ALL || item.difficulty === difficulty;
            const matchesTag = activeTag === ALL || item.tags.includes(activeTag);
            return matchesQuery && matchesRole && matchesLevel && matchesCategory && matchesDifficulty && matchesTag;
        });
    }, [activeTag, category, difficulty, level, query, role]);

    const resetFilters = () => {
        setQuery('');
        setRole(ALL);
        setLevel(ALL);
        setCategory(ALL);
        setDifficulty(ALL);
        setActiveTag(ALL);
    };

    return (
        <div className="app-screen">
            <Navbar />
            <Page wide>
                <PageHero
                    kicker="Ngân hàng câu hỏi"
                    title="Thư viện câu hỏi phỏng vấn IT"
                    description="Tra cứu các câu hỏi tuyển dụng phổ biến theo vai trò, cấp độ, chủ đề và kỹ năng. Đây là thư viện tham khảo, không phải trình tạo mock interview."
                    visual={<ProductMockupGraphic variant="questions" />}
                    tone="questions"
                />

                <section className="qbank-filter-bar" aria-label="Bộ lọc ngân hàng câu hỏi">
                    <label htmlFor="question-search" className="qbank-filter qbank-filter--search">
                        <span>Tìm kiếm</span>
                        <input
                            id="question-search"
                            className="text-input"
                            placeholder="Tìm theo React, SQL, debug, system design..."
                            value={query}
                            onChange={(event) => setQuery(event.target.value)}
                        />
                    </label>

                    <FilterSelect id="question-role" label="Vai trò" value={role} onChange={setRole} options={[ALL, ...IT_ROLES]} />
                    <FilterSelect id="question-level" label="Cấp độ" value={level} onChange={setLevel} options={[ALL, ...IT_LEVELS]} />
                    <FilterSelect id="question-category" label="Chủ đề" value={category} onChange={setCategory} options={[ALL, ...QUESTION_CATEGORIES]} />
                    <FilterSelect id="question-difficulty" label="Độ khó" value={difficulty} onChange={setDifficulty} options={[ALL, ...DIFFICULTIES]} />
                    <FilterSelect id="question-tag" label="Kỹ năng" value={activeTag} onChange={setActiveTag} options={[ALL, ...tags]} />

                    <button className="btn-outline qbank-reset" type="button" onClick={resetFilters}>Xóa lọc</button>
                </section>

                <Panel title="Danh sách câu hỏi" subtitle="Bấm vào một câu hỏi để đọc mục đích phỏng vấn, gợi ý trả lời và lỗi thường gặp.">
                    {filteredQuestions.length === 0 ? (
                        <EmptyState
                            visual={<ProductMockupGraphic variant="questions" />}
                            title="Không có câu hỏi phù hợp"
                            description="Hãy giảm bớt bộ lọc hoặc thử từ khóa khác."
                            action={<button className="btn-outline" onClick={resetFilters}>Xóa bộ lọc</button>}
                        />
                    ) : (
                        <div className="qbank-library-grid">
                            {filteredQuestions.map((question) => (
                                <button
                                    key={question.id}
                                    type="button"
                                    className="card qbank-library-card"
                                    onClick={() => setActiveQuestion(question)}
                                >
                                    <div className="qbank-library-card__meta">
                                        <StatusBadge tone={difficultyTone(question.difficulty)}>{question.difficulty}</StatusBadge>
                                        <StatusBadge>{question.category}</StatusBadge>
                                    </div>
                                    <strong>{question.question_vi || question.question}</strong>
                                    <p className="caption">{question.role} - {question.level}</p>
                                    <div className="qbank-tag-row">
                                        {question.tags.slice(0, 4).map((tag) => <span key={tag}>{tag}</span>)}
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </Panel>
            </Page>

            {activeQuestion && (
                <QuestionDetailModal question={activeQuestion} onClose={() => setActiveQuestion(null)} />
            )}
        </div>
    );
};

const FilterSelect = ({ id, label, value, onChange, options }) => (
    <label htmlFor={id} className="qbank-filter">
        <span>{label}</span>
        <select id={id} className="text-input" value={value} onChange={(event) => onChange(event.target.value)}>
            {options.map((item) => <option key={item} value={item}>{optionLabel(item)}</option>)}
        </select>
    </label>
);

const QuestionDetailModal = ({ question, onClose }) => (
    <div className="ui-modal-overlay" onClick={(event) => event.target === event.currentTarget && onClose()}>
        <div className="ui-modal-card qbank-detail-modal" role="dialog" aria-modal="true" aria-labelledby="question-detail-title">
            <div className="panel-header">
                <div className="qbank-detail-heading">
                    <FeatureIcon type="questions" />
                    <div>
                        <p className="page-kicker">Chi tiết câu hỏi</p>
                        <h2 className="title-md" id="question-detail-title">Câu hỏi</h2>
                    </div>
                </div>
                <button className="btn-ghost" type="button" onClick={onClose}>Đóng</button>
            </div>

            <div className="ui-modal-body qbank-detail">
                <section className="qbank-detail-hero">
                    <div>
                        <div className="ui-cluster">
                            <StatusBadge tone={difficultyTone(question.difficulty)}>{question.difficulty}</StatusBadge>
                            <StatusBadge tone="ai">{question.role}</StatusBadge>
                            <StatusBadge>{question.level}</StatusBadge>
                        </div>
                        <h2>{question.question_vi || question.question}</h2>
                    </div>
                </section>

                <div className="qbank-tag-row">
                    {question.tags.map((tag) => <span key={tag}>{tag}</span>)}
                </div>

                <DetailBlock title="Mục đích nhà tuyển dụng muốn kiểm tra" icon="match">
                    <p>{question.interviewer_expectation_vi || question.expectations}</p>
                </DetailBlock>

                <DetailBlock title="Gợi ý cách trả lời" icon="ai">
                    <p>{question.answer_guidance_vi || question.starHint}</p>
                </DetailBlock>

                <DetailBlock title="Cấu trúc trả lời đề xuất" icon="structure">
                    <ol className="qbank-step-list">
                        {(question.suggested_answer_structure_vi || question.answerStructure || []).map((item, index) => (
                            <li key={item}>
                                <span>{index + 1}</span>
                                <p>{item}</p>
                            </li>
                        ))}
                    </ol>
                </DetailBlock>

                <DetailBlock title="Lỗi thường gặp" icon="report">
                    <div className="qbank-mistake-list">
                        {(question.common_mistakes_vi || question.commonMistakes || []).map((item) => <span key={item}>{item}</span>)}
                    </div>
                </DetailBlock>

                <DetailBlock title="Gợi ý câu trả lời mẫu nếu phù hợp" icon="questions">
                    <p>{question.sample_answer_vi || question.sampleAnswer || 'Không có câu trả lời mẫu cho câu hỏi này.'}</p>
                </DetailBlock>
            </div>
        </div>
    </div>
);

const DetailBlock = ({ title, icon = 'questions', children }) => (
    <section className="qbank-detail-block">
        <div className="qbank-detail-block__heading">
            <FeatureIcon type={icon} />
            <p className="page-kicker">{title}</p>
        </div>
        {children}
    </section>
);

export default QuestionBankPage;
