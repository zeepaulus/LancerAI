import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { getSessions } from '../api/interview';
import * as keys from '../config/storageKeys';

function formatDate(isoString) {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleDateString('vi-VN', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

function scoreColor(score) {
    if (score >= 80) return 'var(--semantic-success, #22c55e)';
    if (score >= 60) return 'var(--semantic-warning, #f59e0b)';
    return 'var(--semantic-error, #ef4444)';
}

const MainDashboard = () => {
    const navigate = useNavigate();
    const profile = JSON.parse(localStorage.getItem(keys.LANCERAI_USER_PROFILE) || '{}');

    const [history, setHistory] = useState([]);
    const [historyLoading, setHistoryLoading] = useState(false);

    useEffect(() => {
        let active = true;
        setHistoryLoading(true);
        getSessions()
            .then(data => {
                if (active) setHistory(data);
            })
            .catch(err => {
                console.error("Lỗi khi tải lịch sử phỏng vấn:", err);
            })
            .finally(() => {
                if (active) setHistoryLoading(false);
            });
        return () => { active = false; };
    }, []);

    // Sinh dữ liệu giả cho Day Streak (Heatmap)
    const generateHeatmap = () => {
        const days = [];
        const colors = ['var(--surface-strong)', 'var(--gradient-mint)', 'var(--gradient-lavender)', 'var(--gradient-peach)'];
        for (let i = 0; i < 90; i++) {
            const level = Math.random() > 0.6 ? Math.floor(Math.random() * 4) : 0;
            days.push(
                <div 
                    key={i} 
                    style={{
                        width: '14px',
                        height: '14px',
                        backgroundColor: colors[level],
                        borderRadius: 'var(--rounded-xs)',
                        transition: 'background-color var(--transition-fast)',
                    }} 
                    title={`Hoạt động mức ${level}`}
                ></div>
            );
        }
        return days;
    };

    // Dữ liệu giả cho biểu đồ hiệu suất
    const performanceData = [40, 60, 55, 80, 75, 90, 85];
    
    const createSvgPoints = () => {
        return performanceData.map((score, index) => {
            const x = (index / (performanceData.length - 1)) * 100;
            const y = 100 - score;
            return `${x},${y}`;
        }).join(' ');
    };

    return (
        <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh'}}>
            <Navbar />
            <div style={styles.container}>
                <div style={styles.welcomeSection}>
                    <h2 className="display-sm" style={styles.welcomeText}>
                        Chào mừng trở lại, {profile.display_name || 'User'}!
                    </h2>
                </div>

                <div style={styles.layoutWrapper}>
                    {/* Main Content (70%) */}
                    <div style={styles.mainContent}>
                        <div style={styles.topCardsRow}>
                            {/* Card 1: Day Streak */}
                            <div className="card" style={styles.flexHalf}>
                                <div style={styles.cardHeader}>
                                    <h3 className="title-md">🔥 Chuỗi hoạt động</h3>
                                    <span className="badge-pill" style={{backgroundColor: 'var(--gradient-peach)', color: 'var(--ink)', fontSize: '10px'}}>
                                        5 ngày liên tiếp
                                    </span>
                                </div>
                                
                                <div style={styles.heatmapWrapper}>
                                    <div style={styles.dayLabels}>
                                        <span>T2</span>
                                        <span>T4</span>
                                        <span>T6</span>
                                    </div>
                                    <div style={styles.heatmapGrid}>
                                        {generateHeatmap()}
                                    </div>
                                </div>
                            </div>

                            {/* Card 2: Best CV Score */}
                            <div className="card" style={styles.flexHalf}>
                                <div style={styles.cardHeader}>
                                    <h3 className="title-md">📄 Điểm CV tốt nhất</h3>
                                    {/* <span className="badge-pill" style={{backgroundColor: 'var(--gradient-mint)', color: 'var(--ink)'}}>
                                        Top 5%
                                    </span> */}
                                </div>
                                <div style={styles.progressWrapper}>
                                    <div style={styles.progressCircle}>
                                        <svg viewBox="0 0 120 120" style={{width: '100px', height: '100px', transform: 'rotate(-90deg)'}}>
                                            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--hairline)" strokeWidth="8" />
                                            <circle cx="60" cy="60" r="52" fill="none" stroke="var(--ink)" strokeWidth="8" 
                                                strokeDasharray={`${2 * Math.PI * 52 * 0.92} ${2 * Math.PI * 52}`}
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                        <div style={styles.progressLabel}>
                                            <span style={{fontSize: '28px', fontWeight: 300, color: 'var(--ink)', fontFamily: 'var(--font-display)'}}>92</span>
                                            <span style={{fontSize: '12px', color: 'var(--muted)', marginTop: '-4px', fontFamily: 'var(--font-display)'}}>/100</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Card 3: Performance Trend */}
                        <div className="card" style={{marginTop: 'var(--sp-lg)', flex: 1, display: 'flex', flexDirection: 'column'}}>
                            <div style={styles.cardHeader}>
                                <h3 className="title-md">🎙️ Xu hướng điểm phỏng vấn</h3>
                            </div>
                            <p style={styles.cardSub}>Điểm trung bình các vòng phỏng vấn gần đây</p>
                            
                            <div style={{ display: 'flex', flex: 1, marginTop: 'var(--sp-xl)', marginBottom: 'var(--sp-sm)' }}>
                                {/* Y-Axis */}
                                <div style={{ 
                                    position: 'relative', 
                                    width: '36px', 
                                    color: 'var(--muted)', 
                                    fontSize: '11px',
                                    fontFamily: 'var(--font-sans)',
                                }}>
                                    {[100, 80, 60, 40].map(score => (
                                        <span key={score} style={{ position: 'absolute', top: `${100 - score}%`, right: '8px', transform: 'translateY(-50%)' }}>
                                            {score}
                                        </span>
                                    ))}
                                </div>
                                
                                {/* Chart Area */}
                                <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
                                    <div style={{ ...styles.chartContainer, marginTop: 0 }}>
                                        <svg viewBox="0 0 100 100" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible', position: 'absolute', top: 0, left: 0 }}>
                                            <defs>
                                                <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stopColor="var(--gradient-lavender)" stopOpacity="0.3"/>
                                                    <stop offset="100%" stopColor="var(--gradient-lavender)" stopOpacity="0"/>
                                                </linearGradient>
                                            </defs>
                                            {/* Horizontal grid lines */}
                                            {[100, 80, 60, 40].map(score => (
                                                <line key={score} x1="0" y1={100 - score} x2="100" y2={100 - score} stroke="var(--hairline)" strokeWidth="1" vectorEffect="non-scaling-stroke" strokeDasharray="3 4" />
                                            ))}
                                            <polygon
                                                fill="url(#chartGradient)"
                                                points={`0,100 ${createSvgPoints()} 100,100`}
                                            />
                                            <polyline 
                                                fill="none" 
                                                stroke="var(--ink)" 
                                                strokeWidth="2" 
                                                vectorEffect="non-scaling-stroke"
                                                points={createSvgPoints()} 
                                                strokeLinejoin="round"
                                                strokeLinecap="round"
                                            />
                                        </svg>
                                        {performanceData.map((score, index) => (
                                            <div 
                                                key={index}
                                                style={{
                                                    position: 'absolute',
                                                    left: `${(index / (performanceData.length - 1)) * 100}%`,
                                                    top: `${100 - score}%`,
                                                    width: '8px',
                                                    height: '8px',
                                                    backgroundColor: 'var(--surface-card)',
                                                    border: '2px solid var(--ink)',
                                                    borderRadius: '50%',
                                                    transform: 'translate(-50%, -50%)',
                                                    zIndex: 2,
                                                }}
                                            />
                                        ))}
                                    </div>
                                    <div style={{ ...styles.chartLabels, marginTop: '12px' }}>
                                        {performanceData.map((_, i) => <span key={i}>Lần {i+1}</span>)}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Sidebar (30%) */}
                    <div style={styles.sidebar}>
                        <div className="card" style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                            <h3 className="title-md" style={{ marginBottom: 'var(--sp-base)' }}>🕒 Phiên phỏng vấn gần đây</h3>
                            
                            <div style={{ flex: 1 }}>
                                {historyLoading ? (
                                    <div style={styles.spinnerWrapper}>
                                        <div style={styles.spinner} />
                                    </div>
                                ) : history.length === 0 ? (
                                    <p style={{ color: 'var(--muted)', fontSize: '14px', textAlign: 'center', marginTop: 'var(--sp-xl)' }}>
                                        Chưa có phiên phỏng vấn nào.
                                    </p>
                                ) : (
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--sp-sm)' }}>
                                        {history.slice(0, 5).map(item => (
                                            <div 
                                                key={item.session_id}
                                                style={styles.historyItem}
                                                onClick={() => navigate('/interview-report', { state: { sessionId: item.session_id } })}
                                                onMouseEnter={e => {
                                                    e.currentTarget.style.backgroundColor = 'var(--canvas-soft)';
                                                }}
                                                onMouseLeave={e => {
                                                    e.currentTarget.style.backgroundColor = 'transparent';
                                                }}
                                            >
                                                <div style={{ display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                                                    <span style={{ fontSize: '14px', fontWeight: 600, color: 'var(--ink)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                                                        {item.title || 'Buổi phỏng vấn'}
                                                    </span>
                                                    <span style={{ fontSize: '12px', color: 'var(--muted)' }}>{formatDate(item.created_at)}</span>
                                                </div>
                                                {item.status === 'incomplete' ? (
                                                    <span className="badge-pill" style={{ fontSize: '11px', backgroundColor: 'var(--surface-strong)', color: 'var(--muted)', whiteSpace: 'nowrap' }}>
                                                        Chưa HT
                                                    </span>
                                                ) : (
                                                    <span className="badge-pill" style={{ fontSize: '11px', backgroundColor: scoreColor(item.overall_confidence), color: '#fff', whiteSpace: 'nowrap' }}>
                                                        {Math.round(item.overall_confidence)} đ
                                                    </span>
                                                )}
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </div>

                            <button className="btn-outline" style={{width: '100%', marginTop: 'var(--sp-lg)'}} onClick={() => navigate('/interview')}>
                                Xem tất cả →
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '1200px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg)',
    },
    welcomeSection: {
        marginBottom: 'var(--sp-xl)',
    },
    welcomeText: {
        color: 'var(--ink)',
        fontSize: '36px',
    },
    layoutWrapper: {
        display: 'flex',
        gap: 'var(--sp-xl)',
        alignItems: 'stretch',
        flexWrap: 'wrap',
    },
    mainContent: {
        flex: '1 1 65%',
        display: 'flex',
        flexDirection: 'column',
    },
    sidebar: {
        flex: '1 1 30%',
        minWidth: '300px',
        display: 'flex',
        flexDirection: 'column',
    },
    topCardsRow: {
        display: 'flex',
        gap: 'var(--sp-lg)',
        flexWrap: 'wrap',
    },
    flexHalf: {
        flex: 1,
        minWidth: '280px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
    },
    cardHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: 'var(--sp-base)',
    },
    heatmapWrapper: {
        display: 'flex',
        gap: 'var(--sp-sm)',
        alignItems: 'flex-start',
    },
    dayLabels: {
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
        height: '122px',
        fontSize: '12px',
        color: 'var(--muted)',
        paddingTop: '5px',
    },
    heatmapGrid: {
        display: 'grid',
        gridTemplateRows: 'repeat(7, 14px)',
        gridAutoFlow: 'column',
        gap: '4px',
        overflowX: 'auto',
        paddingBottom: 'var(--sp-sm)',
    },
    cardSub: {
        color: 'var(--muted)',
        fontSize: '14px',
        letterSpacing: '0.15px',
    },
    chartContainer: {
        position: 'relative',
        flex: 1,
        minHeight: '160px',
        width: '100%',
        marginTop: 'var(--sp-xl)',
    },
    chartLabels: {
        display: 'flex',
        justifyContent: 'space-between',
        marginTop: 'var(--sp-sm)',
        fontSize: '12px',
        color: 'var(--muted)',
    },
    progressWrapper: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        flex: 1,
        minHeight: '120px',
    },
    progressCircle: {
        position: 'relative',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
    },
    progressLabel: {
        position: 'absolute',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
    },
    spinnerWrapper: {
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        height: '100px',
    },
    spinner: {
        width: '28px', height: '28px',
        border: '3px solid var(--hairline)',
        borderTop: '3px solid var(--ink)',
        borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
    },
    historyItem: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: 'var(--sp-sm) var(--sp-sm)',
        borderRadius: 'var(--rounded-md)',
        cursor: 'pointer',
        transition: 'background-color var(--transition-fast)',
        border: '1px solid transparent',
        gap: 'var(--sp-sm)',
    },
};

export default MainDashboard;