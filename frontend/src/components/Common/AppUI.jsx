import React from 'react';

export const Page = ({ children, narrow = false, wide = false }) => (
    <main className={`app-page ${narrow ? 'app-page--narrow' : ''} ${wide ? 'app-page--wide' : ''}`}>
        {children}
    </main>
);

export const PageHeader = ({ kicker, title, description, actions }) => (
    <div className="page-header">
        <div>
            {kicker && <p className="page-kicker">{kicker}</p>}
            <h1 className="page-title">{title}</h1>
            {description && <p className="page-subtitle">{description}</p>}
        </div>
        {actions && <div className="page-header__actions">{actions}</div>}
    </div>
);

export const PageHero = ({ kicker, title, description, actions, visual, children, tone = 'brand' }) => (
    <section className={`page-hero page-hero--${tone} ${visual ? '' : 'page-hero--solo'}`}>
        <div className="page-hero__content">
            {kicker && <p className="page-kicker">{kicker}</p>}
            <h1>{title}</h1>
            {description && <p>{description}</p>}
            {actions && <div className="page-hero__actions">{actions}</div>}
            {children}
        </div>
        {visual && <div className="page-hero__visual">{visual}</div>}
    </section>
);

export const IconBadge = ({ children, tone = 'brand', label }) => (
    <span className={`icon-badge icon-badge--${tone}`} aria-label={label} title={label}>
        {children}
    </span>
);

export const QuickActionCard = ({ icon, visual, title, description, meta, action, tone = 'brand', onClick }) => {
    const Tag = onClick ? 'button' : 'article';
    return (
        <Tag type={onClick ? 'button' : undefined} className={`quick-action-card quick-action-card--${tone}`} onClick={onClick}>
            <span className="quick-action-card__accent" aria-hidden="true" />
            <div className="quick-action-card__top">
                {icon && <div className="quick-action-card__icon">{icon}</div>}
                {meta && <StatusBadge tone={meta.tone || tone}>{meta.label || meta}</StatusBadge>}
            </div>
            <div>
                {visual && <div className="quick-action-card__visual">{visual}</div>}
                <strong>{title}</strong>
                {description && <p>{description}</p>}
            </div>
            {action && <div className="quick-action-card__action">{action}</div>}
        </Tag>
    );
};

export const ProgressCard = ({ label, value = 0, detail, tone = 'brand' }) => {
    const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
    return (
        <article className={`progress-card progress-card--${tone}`}>
            <div className="progress-card__header">
                <span>{label}</span>
                <strong>{Math.round(safeValue)}%</strong>
            </div>
            <ScoreBar value={safeValue} tone={tone === 'brand' ? 'brand' : tone} />
            {detail && <p>{detail}</p>}
        </article>
    );
};

export const FilterPill = ({ active = false, children, onClick, tone = 'brand' }) => (
    <button type="button" className={`filter-pill filter-pill--${tone} ${active ? 'is-active' : ''}`} onClick={onClick}>
        {children}
    </button>
);

export const SectionHeader = ({ kicker, title, description, actions }) => (
    <div className="section-header">
        <div>
            {kicker && <p className="page-kicker">{kicker}</p>}
            {title && <h2>{title}</h2>}
            {description && <p>{description}</p>}
        </div>
        {actions && <div className="section-header__actions">{actions}</div>}
    </div>
);

export const AIStatusPanel = ({ state = 'Ready', title, description, actions, tone = 'ai' }) => (
    <section className={`ai-status-panel ai-status-panel--${tone}`} aria-live="polite">
        <div className="ai-status-panel__pulse" />
        <div>
            <StatusBadge tone={tone}>{state}</StatusBadge>
            {title && <h3>{title}</h3>}
            {description && <p>{description}</p>}
        </div>
        {actions && <div className="ai-status-panel__actions">{actions}</div>}
    </section>
);

export const InterviewStateCard = ({ active = false, number, title, description, tone = 'voice' }) => (
    <article className={`interview-state-card interview-state-card--${tone} ${active ? 'is-active' : ''}`}>
        <span>{number}</span>
        <div>
            <strong>{title}</strong>
            {description && <p>{description}</p>}
        </div>
    </article>
);

export const TimelineItem = ({ marker, title, meta, children, tone = 'neutral' }) => (
    <article className={`timeline-item timeline-item--${tone}`}>
        <div className="timeline-item__marker">{marker}</div>
        <div className="timeline-item__body">
            <div className="timeline-item__header">
                {title && <strong>{title}</strong>}
                {meta && <span>{meta}</span>}
            </div>
            {children && <div className="timeline-item__content">{children}</div>}
        </div>
    </article>
);

export const ActionToolbar = ({ children }) => (
    <div className="action-toolbar">
        {children}
    </div>
);

export const SearchFilterBar = ({ children }) => (
    <div className="search-filter-bar">
        {children}
    </div>
);

export const LoadingState = ({ title = 'Đang tải dữ liệu', description }) => (
    <div className="state-panel state-panel--loading" role="status">
        <div className="skeleton" />
        <strong>{title}</strong>
        {description && <p>{description}</p>}
    </div>
);

export const ErrorState = ({ title = 'Không thể hoàn tất thao tác', description, action }) => (
    <div className="state-panel state-panel--error" role="alert">
        <strong>{title}</strong>
        {description && <p>{description}</p>}
        {action}
    </div>
);

export const ReportPanel = ({ title, score, description, children, tone = 'analytics' }) => (
    <section className={`report-panel report-panel--${tone}`}>
        <div className="report-panel__score">
            <strong>{score}</strong>
        </div>
        <div>
            {title && <h3>{title}</h3>}
            {description && <p>{description}</p>}
            {children}
        </div>
    </section>
);

export const MatchScoreCard = ({ score = 0, title = 'Match score', description, actions }) => {
    const safeScore = Math.max(0, Math.min(100, Number(score) || 0));
    return (
        <article className="match-score-card">
            <div className="match-score-card__ring" style={{ '--match-score': `${safeScore}%` }}>
                <strong>{Math.round(safeScore)}</strong>
            </div>
            <div>
                <h3>{title}</h3>
                {description && <p>{description}</p>}
                {actions && <div className="match-score-card__actions">{actions}</div>}
            </div>
        </article>
    );
};

export const MetricCard = ({ label, value, detail, tone = 'neutral' }) => (
    <div className={`metric-card metric-card--${tone}`}>
        <span className="metric-card__beam" aria-hidden="true" />
        <span>{label}</span>
        <strong>{value}</strong>
        {detail && <small>{detail}</small>}
    </div>
);

export const StatusBadge = ({ children, tone = 'neutral', compact = false }) => (
    <span className={`status-badge status-badge--${tone} ${compact ? 'status-badge--compact' : ''}`}>{children}</span>
);

export const InlineMeta = ({ label, value }) => (
    <span className="inline-meta">
        <span>{label}</span>
        <strong>{value}</strong>
    </span>
);

export const Alert = ({ tone = 'warning', title, children, action }) => (
    <div className={`app-alert app-alert--${tone}`} role={tone === 'danger' ? 'alert' : 'status'}>
        <div>
            {title && <strong>{title}</strong>}
            {children && <p>{children}</p>}
        </div>
        {action}
    </div>
);

export const AIResponsePanel = ({ title = 'Gợi ý từ AI', subtitle, children, footer }) => (
    <section className="ai-response-panel">
        <div className="ai-response-panel__header">
            <span className="ai-response-panel__mark">AI</span>
            <div>
                <h3>{title}</h3>
                {subtitle && <p>{subtitle}</p>}
            </div>
        </div>
        <div className="ai-response-panel__body">{children}</div>
        {footer && <div className="ai-response-panel__footer">{footer}</div>}
    </section>
);

export const FeatureActionCard = ({ icon, title, description, status, primaryAction, secondaryAction }) => (
    <article className="feature-action-card">
        <div className="feature-action-card__top">
            {icon && <div className="feature-action-card__icon">{icon}</div>}
            {status && <StatusBadge tone={status.tone || 'neutral'}>{status.label}</StatusBadge>}
        </div>
        <div>
            <h2>{title}</h2>
            {description && <p>{description}</p>}
        </div>
        <div className="feature-action-card__actions">
            {primaryAction}
            {secondaryAction}
        </div>
    </article>
);

export const EmptyState = ({ title, description, action, visual }) => (
    <div className="empty-state">
        {visual && <div className="empty-state__visual">{visual}</div>}
        <strong>{title}</strong>
        {description && <p>{description}</p>}
        {action}
    </div>
);

export const Panel = ({ title, subtitle, actions, children, className = '', style }) => (
    <section className={`panel ${className}`} style={style}>
        {(title || subtitle || actions) && (
            <div className="panel-header">
                <div>
                    {title && <h2 className="title-sm">{title}</h2>}
                    {subtitle && <p className="caption">{subtitle}</p>}
                </div>
                {actions}
            </div>
        )}
        <div className="panel-body">{children}</div>
    </section>
);

export const ScoreBar = ({ value = 0, tone = 'brand' }) => {
    const safeValue = Math.max(0, Math.min(100, Number(value) || 0));
    return (
        <div className={`progress-track progress-track--${tone}`} style={{ '--progress-value': `${safeValue}%`, '--progress-color': scoreColor(tone, safeValue) }}>
            <div className="progress-fill" />
        </div>
    );
};

export const SkeletonRows = ({ rows = 3 }) => (
    <div className="skeleton-row-stack">
        {Array.from({ length: rows }).map((_, index) => (
            <div key={index} className="skeleton skeleton-row" />
        ))}
    </div>
);

function scoreColor(tone, value) {
    if (tone !== 'auto') {
        const colors = {
            brand: 'var(--color-brand-primary)',
            success: 'var(--color-success)',
            warning: 'var(--color-warning)',
            danger: 'var(--color-danger)',
            ai: 'var(--color-processing)',
            voice: 'var(--color-accent-voice)',
            cv: 'var(--color-accent-cv)',
            match: 'var(--color-accent-match)',
            questions: 'var(--color-accent-questions)',
            analytics: 'var(--color-accent-analytics)',
            settings: 'var(--color-accent-settings)',
        };
        return colors[tone] || colors.brand;
    }
    if (value >= 80) return 'var(--color-success)';
    if (value >= 60) return 'var(--color-warning)';
    return 'var(--color-danger)';
}
