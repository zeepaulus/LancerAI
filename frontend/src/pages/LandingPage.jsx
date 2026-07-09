import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FeatureIcon, ProductMockupGraphic } from '../components/Common/Visuals';

const LandingPage = () => {
    const navigate = useNavigate();

    const features = [
        {
            icon: 'cv',
            title: 'CV analysis',
            body: 'Extract skills, experience, education, and project evidence from an uploaded CV.',
        },
        {
            icon: 'voice',
            title: 'Voice interview',
            body: 'Practice with spoken questions, live transcript, and a scored report after the session.',
        },
        {
            icon: 'match',
            title: 'Job matching',
            body: 'Compare a CV with a job description and see missing skills before applying.',
        },
        {
            icon: 'report',
            title: 'Reports',
            body: 'Review scores, transcript evidence, and concrete points to improve before the next interview.',
        },
    ];

    return (
        <div className="landing-page">
            <nav className="landing-nav">
                <button className="landing-brand" onClick={() => navigate('/')}>
                    <span className="landing-brand__mark">L</span>
                    <span>LancerAI</span>
                </button>
                <div className="landing-nav__actions">
                    <button className="btn-outline" onClick={() => navigate('/login')}>Log in</button>
                    <button className="btn-primary" onClick={() => navigate('/signup')}>Start free</button>
                </div>
            </nav>

            <main>
                <section className="landing-hero">
                    <div className="landing-hero__copy">
                        <span className="status-badge status-badge--ai">CV + interview practice</span>
                        <h1>Prepare for IT interviews from your CV.</h1>
                        <p>
                            Upload a CV, match it with job descriptions, practice voice interviews, and review transcript-based reports.
                        </p>
                        <div className="landing-hero__actions">
                            <button className="btn-primary" onClick={() => navigate('/signup')}>Create account</button>
                            <button className="btn-outline" onClick={() => navigate('/login')}>Open dashboard</button>
                        </div>
                        <div className="product-pipeline" aria-label="Quy trình LancerAI">
                            {['Upload CV', 'Match JD', 'Practice interview', 'Review report'].map((step) => (
                                <span key={step}>{step}</span>
                            ))}
                        </div>
                    </div>
                    <div className="landing-hero__visual">
                        <ProductMockupGraphic variant="workspace" />
                    </div>
                </section>

                <section className="landing-section">
                    <div className="landing-section__header">
                        <p className="page-kicker">Workflow</p>
                        <h2 className="title-lg">One flow from CV to interview report</h2>
                        <p className="page-subtitle">Each step keeps the source visible: CV sections, job criteria, spoken answers, and report notes.</p>
                    </div>
                    <div className="landing-feature-grid">
                        {features.map((feature) => (
                            <article className="card landing-feature-card" key={feature.title}>
                                <FeatureIcon type={feature.icon} />
                                <h3 className="title-sm">{feature.title}</h3>
                                <p className="caption">{feature.body}</p>
                            </article>
                        ))}
                    </div>
                </section>

                <section className="landing-showcase">
                    <div className="landing-showcase__copy">
                        <p className="page-kicker">Voice interview</p>
                        <h2 className="title-lg">Practice with transcript while speaking</h2>
                        <p className="page-subtitle">
                            The interview room shows recording state, current question, spoken answers, and the report link when the session ends.
                        </p>
                    </div>
                    <ProductMockupGraphic variant="voice" />
                </section>

                <section className="landing-showcase landing-showcase--alt">
                    <ProductMockupGraphic variant="cv" />
                    <div className="landing-showcase__copy">
                        <p className="page-kicker">CV analysis</p>
                        <h2 className="title-lg">Turn a CV into structured profile data</h2>
                        <p className="page-subtitle">
                            Extract profile, education, experience, projects, and skills before using them for matching or interviews.
                        </p>
                    </div>
                </section>

                <section className="landing-showcase">
                    <div className="landing-showcase__copy">
                        <p className="page-kicker">Reports</p>
                        <h2 className="title-lg">Reports show what to improve</h2>
                        <p className="page-subtitle">
                            Review score, transcript evidence, behavior notes, and suggested fixes from completed interview sessions.
                        </p>
                    </div>
                    <ProductMockupGraphic variant="report" />
                </section>

                <section className="landing-cta">
                    <span className="status-badge status-badge--success">Ready to practice</span>
                    <h2 className="title-lg">Start with a CV, then run a focused interview.</h2>
                    <p className="page-subtitle">
                        Use one uploaded CV for extraction, job matching, question practice, and interview reports.
                    </p>
                    <button className="btn-primary" onClick={() => navigate('/signup')}>Get started</button>
                </section>
            </main>
        </div>
    );
};

export default LandingPage;
