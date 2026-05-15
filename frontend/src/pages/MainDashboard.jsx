import React from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';

const MainDashboard = () => {
    const navigate = useNavigate();

    // Sinh dữ liệu giả cho Day Streak (Heatmap)
    const generateHeatmap = () => {
        const days = [];
        for (let i = 0; i < 90; i++) { // 90 ngày
            const level = Math.random() > 0.6 ? Math.floor(Math.random() * 4) : 0;
            let bgColor = 'var(--nav-bg)'; // Ngày chưa hoạt động
            if (level === 1) bgColor = '#90cdf4'; // Hoạt động ít
            if (level === 2) bgColor = '#4299e1'; // Hoạt động vừa
            if (level === 3) bgColor = '#3182ce'; // Hoạt động nhiều
            
            days.push(
                <div 
                    key={i} 
                    style={{ width: '14px', height: '14px', backgroundColor: bgColor, borderRadius: '3px' }} 
                    title={`Hoạt động mức ${level}`}
                ></div>
            );
        }
        return days;
    };

    // Dữ liệu giả cho biểu đồ hiệu suất (Từ 0 - 100)
    const performanceData = [40, 60, 55, 80, 75, 90, 85];
    
    // Hàm tạo chuỗi toạ độ cho SVG Line Chart
    const createSvgPoints = () => {
        return performanceData.map((score, index) => {
            const x = (index / (performanceData.length - 1)) * 100; // Tọa độ X (0 - 100%)
            const y = 100 - score; // Tọa độ Y (Đảo ngược vì SVG tính từ trên xuống)
            return `${x},${y}`;
        }).join(' ');
    };

    const styles = {
        container: { maxWidth: '1000px', margin: '30px auto', padding: '0 20px', fontFamily: 'system-ui', color: 'var(--text-color)' },
        // Thêm margin-bottom để dãn cách tiêu đề
        mainTitle: { margin: '0 0 24px 0', fontSize: '28px' }, 
        card: { background: 'var(--bg-color)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '24px', marginBottom: '24px', boxShadow: '0 2px 4px rgba(0,0,0,0.05)' },
        
        // CSS Grid cho Heatmap: 7 hàng dọc (tương đương 7 ngày/tuần), chảy theo cột
        heatmapWrapper: { display: 'flex', gap: '10px', alignItems: 'flex-start', marginTop: '20px' },
        dayLabels: { display: 'flex', flexDirection: 'column', justifyContent: 'space-between', height: '122px', fontSize: '12px', color: 'var(--text-color)', opacity: 0.7, paddingTop: '5px' },
        heatmapGrid: { display: 'grid', gridTemplateRows: 'repeat(7, 14px)', gridAutoFlow: 'column', gap: '4px', overflowX: 'auto', paddingBottom: '10px' },
        
        sectionTitle: { margin: '0 0 10px 0', fontSize: '20px' },
        flexRow: { display: 'flex', gap: '24px', flexWrap: 'wrap' },
        // Chỉnh flexHalf thành flex column để đẩy nút xuống đáy
        flexHalf: { flex: 1, minWidth: '300px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' },
        
        btnAction: { background: '#3182ce', color: 'white', padding: '12px 24px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '16px', marginTop: '20px', width: '100%', transition: 'opacity 0.2s' },
        
        // Style cho Line Chart SVG
        chartContainer: { position: 'relative', height: '140px', width: '100%', marginTop: '30px' }
    };

    return (
        <div>
            <Navbar />
            <div style={styles.container}>
                <h2 style={styles.mainTitle}>Tổng quan hoạt động</h2>
                
                {/* DAY STREAK */}
                <div style={styles.card}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h3 style={styles.sectionTitle}>🔥 Day Streak</h3>
                        <span style={{ fontSize: '14px', fontWeight: 'bold', color: '#e53e3e', background: 'var(--nav-bg)', padding: '5px 12px', borderRadius: '20px' }}>
                            Đang giữ chuỗi: 5 ngày liên tiếp
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
                    <div style={{...styles.card, ...styles.flexHalf}}>
                        <div>
                            <h3 style={styles.sectionTitle}>🎙️ Phỏng vấn AI</h3>
                            <p style={{color: 'var(--text-color)', opacity: 0.8, fontSize: '14px', margin: 0}}>Điểm trung bình các vòng phỏng vấn gần đây</p>
                            
                            {/* SVG Line Chart */}
                            <div style={styles.chartContainer}>
                                <svg viewBox="0 -10 100 120" preserveAspectRatio="none" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                                    {/* Vẽ đường line màu xanh */}
                                    <polyline 
                                        fill="none" 
                                        stroke="#3182ce" 
                                        strokeWidth="2.5" 
                                        points={createSvgPoints()} 
                                        strokeLinejoin="round"
                                        strokeLinecap="round"
                                    />
                                    {/* Vẽ các điểm chấm tròn (Dots) */}
                                    {performanceData.map((score, index) => (
                                        <circle 
                                            key={index}
                                            cx={`${(index / (performanceData.length - 1)) * 100}`} 
                                            cy={`${100 - score}`} 
                                            r="3" 
                                            fill="var(--bg-color)" 
                                            stroke="#3182ce" 
                                            strokeWidth="2" 
                                        />
                                    ))}
                                </svg>
                                {/* Trục X hiển thị điểm số giả lập */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', fontSize: '12px', color: 'var(--text-color)', opacity: 0.6 }}>
                                    {performanceData.map((score, i) => <span key={i}>{score}</span>)}
                                </div>
                            </div>
                        </div>
                        
                        <button style={styles.btnAction} onClick={() => navigate('/interview')}>Bắt đầu phỏng vấn</button>
                    </div>

                    {/* KHỐI ĐÁNH GIÁ CV */}
                    <div style={{...styles.card, ...styles.flexHalf}}>
                        <div>
                            <h3 style={styles.sectionTitle}>📄 Đánh giá CV</h3>
                            <p style={{color: 'var(--text-color)', opacity: 0.8, fontSize: '14px', margin: 0}}>Độ hoàn thiện của CV theo chuẩn ATS</p>
                            
                            <div style={{ display: 'flex', justifyContent: 'center', margin: '30px 0' }}>
                                <div style={{ width: '120px', height: '120px', borderRadius: '50%', background: `conic-gradient(#3182ce 85%, var(--border-color) 85%)`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                    <div style={{ width: '100px', height: '100px', borderRadius: '50%', background: 'var(--bg-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '24px', fontWeight: 'bold' }}>
                                        85/100
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <button style={styles.btnAction} onClick={() => navigate('/cv-upload')}>Bắt đầu Đánh giá CV</button>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MainDashboard;