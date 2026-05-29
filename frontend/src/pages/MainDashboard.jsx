import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const MainDashboard = () => {
    const navigate = useNavigate();

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
                <h2 className="display-sm" style={styles.mainTitle}>Tổng quan hoạt động</h2>
                
                {/* DAY STREAK */}
                <div className="card" style={{marginBottom: 'var(--sp-lg)'}}>
                    <div style={styles.cardHeader}>
                        <h3 className="title-md">🔥 Day Streak</h3>
                        <span className="badge-pill" style={{backgroundColor: 'var(--gradient-peach)', color: 'var(--ink)'}}>
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

                <div style={styles.flexRow}>
                    {/* KHỐI PHỎNG VẤN AI */}
                    <div className="card" style={styles.flexHalf}>
                        <div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-xs)'}}>🎙️ Phỏng vấn AI</h3>
                            <p style={styles.cardSub}>Điểm trung bình các vòng phỏng vấn gần đây</p>
                            
                            <div style={styles.chartContainer}>
                                <svg viewBox="0 -10 100 120" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                                    {/* Gradient fill area */}
                                    <defs>
                                        <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="var(--gradient-lavender)" stopOpacity="0.3"/>
                                            <stop offset="100%" stopColor="var(--gradient-lavender)" stopOpacity="0"/>
                                        </linearGradient>
                                    </defs>
                                    <polygon
                                        fill="url(#chartGradient)"
                                        points={`0,100 ${createSvgPoints()} 100,100`}
                                    />
                                    <polyline 
                                        fill="none" 
                                        stroke="var(--ink)" 
                                        strokeWidth="2" 
                                        points={createSvgPoints()} 
                                        strokeLinejoin="round"
                                        strokeLinecap="round"
                                    />
                                    {performanceData.map((score, index) => (
                                        <circle 
                                            key={index}
                                            cx={`${(index / (performanceData.length - 1)) * 100}`} 
                                            cy={`${100 - score}`} 
                                            r="3" 
                                            fill="var(--surface-card)" 
                                            stroke="var(--ink)" 
                                            strokeWidth="2" 
                                        />
                                    ))}
                                </svg>
                                <div style={styles.chartLabels}>
                                    {performanceData.map((score, i) => <span key={i}>{score}</span>)}
                                </div>
                            </div>
                        </div>
                        
                        <button className="btn-primary" style={{width: '100%', marginTop: 'var(--sp-lg)', height: '44px'}} onClick={() => navigate('/interview')}>
                            Bắt đầu phỏng vấn
                        </button>
                    </div>

                    {/* KHỐI ĐÁNH GIÁ CV */}
                    <div className="card" style={styles.flexHalf}>
                        <div>
                            <h3 className="title-md" style={{marginBottom: 'var(--sp-xs)'}}>📄 Đánh giá CV</h3>
                            <p style={styles.cardSub}>Độ hoàn thiện của CV theo chuẩn ATS</p>
                            
                            <div style={styles.progressWrapper}>
                                <div style={styles.progressCircle}>
                                    <svg viewBox="0 0 120 120" style={{width: '120px', height: '120px', transform: 'rotate(-90deg)'}}>
                                        <circle cx="60" cy="60" r="52" fill="none" stroke="var(--hairline)" strokeWidth="8" />
                                        <circle cx="60" cy="60" r="52" fill="none" stroke="var(--ink)" strokeWidth="8" 
                                            strokeDasharray={`${2 * Math.PI * 52 * 0.85} ${2 * Math.PI * 52}`}
                                            strokeLinecap="round"
                                        />
                                    </svg>
                                    <div style={styles.progressLabel}>
                                        <span style={{fontSize: '28px', fontWeight: 300, fontFamily: 'var(--font-display)', color: 'var(--ink)'}}>85</span>
                                        <span style={{fontSize: '12px', color: 'var(--muted)', marginTop: '-4px'}}>/100</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button className="btn-primary" style={{width: '100%', marginTop: 'var(--sp-lg)', height: '44px'}} onClick={() => navigate('/cv-upload')}>
                            Bắt đầu Đánh giá CV
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

const styles = {
    container: {
        maxWidth: '1000px',
        margin: '0 auto',
        padding: 'var(--sp-xl) var(--sp-lg)',
    },
    mainTitle: {
        marginBottom: 'var(--sp-lg)',
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
    flexRow: {
        display: 'flex',
        gap: 'var(--sp-lg)',
        flexWrap: 'wrap',
    },
    flexHalf: {
        flex: 1,
        minWidth: '300px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'space-between',
    },
    cardSub: {
        color: 'var(--muted)',
        fontSize: '14px',
        letterSpacing: '0.15px',
    },
    chartContainer: {
        position: 'relative',
        height: '140px',
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
        margin: 'var(--sp-xl) 0',
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
};

export default MainDashboard;