// import React, { useState, useRef, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
// import Navbar from '../components/Layout/Navbar';

// const ChatPage = () => {
//     const navigate = useNavigate();
//     const [input, setInput] = useState('');
//     const chatEndRef = useRef(null);

//     const [messages, setMessages] = useState([
//         { id: 1, sender: 'ai', text: 'Chào bạn! Tôi là Lancer AI. Hôm nay chúng ta sẽ phỏng vấn cho vị trí Frontend Developer. Bạn đã sẵn sàng chưa?' },
//         { id: 2, sender: 'user', text: 'Chào bạn, tôi đã sẵn sàng!' },
//         { id: 3, sender: 'ai', text: 'Tuyệt vời. Câu hỏi đầu tiên: Bạn có thể giải thích sự khác biệt giữa state và props trong React không?' }
//     ]);

//     // Auto-scroll to bottom
//     useEffect(() => {
//         chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//     }, [messages]);

//     const handleSend = () => {
//         if (!input.trim()) return;
//         setMessages([...messages, { id: Date.now(), sender: 'user', text: input }]);
//         setInput('');
        
//         setTimeout(() => {
//             setMessages(prev => [...prev, { id: Date.now(), sender: 'ai', text: 'Cảm ơn câu trả lời của bạn. Chúng ta tiếp tục nhé...' }]);
//         }, 1000);
//     };

//     return (
//         <div style={{backgroundColor: 'var(--canvas)', minHeight: '100vh', display: 'flex', flexDirection: 'column'}}>
//             <Navbar />
//             <div style={styles.container}>
//                 <button className="btn-tertiary" style={{marginBottom: 'var(--sp-sm)'}} onClick={() => navigate(-1)}>
//                     ← Quay lại
//                 </button>
                
//                 <div style={styles.chatBox}>
//                     {messages.map(msg => {
//                         const isUser = msg.sender === 'user';
//                         return (
//                             <div key={msg.id} style={{display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start'}}>
//                                 {!isUser && <div style={styles.aiAvatar}>AI</div>}
//                                 <div style={isUser ? styles.bubbleUser : styles.bubbleAI}>
//                                     {msg.text}
//                                 </div>
//                             </div>
//                         );
//                     })}
//                     <div ref={chatEndRef} />
//                 </div>

//                 <div style={styles.inputArea}>
//                     <input 
//                         className="text-input"
//                         style={{flex: 1, borderRadius: 'var(--rounded-pill)', paddingLeft: 'var(--sp-md)'}}
//                         placeholder="Nhập câu trả lời của bạn..." 
//                         value={input}
//                         onChange={(e) => setInput(e.target.value)}
//                         onKeyDown={(e) => e.key === 'Enter' && handleSend()}
//                     />
//                     <button className="btn-primary" onClick={handleSend}>
//                         Gửi
//                     </button>
//                 </div>
//             </div>
//         </div>
//     );
// };

// const styles = {
//     container: {
//         maxWidth: '800px',
//         margin: '0 auto',
//         padding: 'var(--sp-base) var(--sp-lg)',
//         flex: 1,
//         display: 'flex',
//         flexDirection: 'column',
//         height: 'calc(100vh - var(--nav-height))',
//     },
//     chatBox: {
//         flex: 1,
//         overflowY: 'auto',
//         padding: 'var(--sp-lg)',
//         backgroundColor: 'var(--surface-card)',
//         border: '1px solid var(--hairline)',
//         borderRadius: 'var(--rounded-xl) var(--rounded-xl) 0 0',
//         display: 'flex',
//         flexDirection: 'column',
//         gap: 'var(--sp-base)',
//     },
//     aiAvatar: {
//         width: '32px',
//         height: '32px',
//         borderRadius: 'var(--rounded-full)',
//         backgroundColor: 'var(--surface-strong)',
//         display: 'flex',
//         alignItems: 'center',
//         justifyContent: 'center',
//         fontSize: '11px',
//         fontWeight: 600,
//         color: 'var(--muted)',
//         flexShrink: 0,
//         marginRight: 'var(--sp-xs)',
//         marginTop: '2px',
//     },
//     bubbleUser: {
//         maxWidth: '70%',
//         padding: 'var(--sp-sm) var(--sp-base)',
//         borderRadius: 'var(--rounded-xl) var(--rounded-xl) var(--rounded-xs) var(--rounded-xl)',
//         backgroundColor: 'var(--primary)',
//         color: 'var(--on-primary)',
//         fontSize: '15px',
//         lineHeight: 1.5,
//         letterSpacing: '0.15px',
//     },
//     bubbleAI: {
//         maxWidth: '70%',
//         padding: 'var(--sp-sm) var(--sp-base)',
//         borderRadius: 'var(--rounded-xl) var(--rounded-xl) var(--rounded-xl) var(--rounded-xs)',
//         backgroundColor: 'var(--surface-strong)',
//         color: 'var(--body-strong, var(--ink))',
//         fontSize: '15px',
//         lineHeight: 1.5,
//         letterSpacing: '0.15px',
//         border: '1px solid var(--hairline)',
//     },
//     inputArea: {
//         display: 'flex',
//         padding: 'var(--sp-sm)',
//         backgroundColor: 'var(--surface-card)',
//         border: '1px solid var(--hairline)',
//         borderTop: 'none',
//         borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
//         gap: 'var(--sp-xs)',
//         alignItems: 'center',
//     },
// };

// export default ChatPage;

import React, { useState, useRef, useEffect, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { API_BASE_URL } from '../config/env';
import { INTERVIEW_WS_PATH } from '../api/paths';
import * as keys from '../config/storageKeys';

// ─── Constants ────────────────────────────────────────────────────────────────

const PHASE = {
    GREETING:  'greeting',   // Hiển thị lời chào, chờ user bấm "Tôi đã sẵn sàng"
    INTERVIEW: 'interview',  // Đang phỏng vấn
    ENDED:     'ended',      // Kết thúc
};

// ─── Helpers ──────────────────────────────────────────────────────────────────

// Chuyển API_BASE_URL (http/https) sang WS URL (ws/wss)
function buildWsUrl() {
    const base = API_BASE_URL.replace(/^http/, 'ws');
    return `${base}${INTERVIEW_WS_PATH}`;
}

function today() {
    return new Date().toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric',
    });
}

// ─── Component ────────────────────────────────────────────────────────────────

const ChatPage = () => {
    const navigate  = useNavigate();
    const location  = useLocation();
    const state     = location.state || {};

    // Context nhận từ InterviewPage
    const {
        sessionId,
        cvId,
        extractionData = {},
        sessionName    = 'Buổi phỏng vấn',
        industry       = '',
        position       = 'Vị trí không xác định',
        level          = '',
        mode           = 'practice',
        userName       = 'bạn',
    } = state;

    // Nếu vào thẳng /chat mà không có state → redirect về interview
    useEffect(() => {
        if (!sessionId || !cvId) {
            navigate('/interview', { replace: true });
        }
    }, [sessionId, cvId, navigate]);

    // ── State ──────────────────────────────────────────────────────────────

    const [phase, setPhase]       = useState(PHASE.GREETING);
    const [messages, setMessages] = useState([]);
    const [inputText, setInputText] = useState('');
    const [aiTyping, setAiTyping] = useState(false);
    const [wsError, setWsError]   = useState('');

    // Voice
    const [voiceActive, setVoiceActive]     = useState(false);
    const [voiceSupported, setVoiceSupported] = useState(false);

    // Refs
    const wsRef          = useRef(null);
    const chatEndRef     = useRef(null);
    const inputRef       = useRef(null);
    const recognitionRef = useRef(null);
    const mediaStreamRef = useRef(null);

    // ── Auto-scroll ────────────────────────────────────────────────────────

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, aiTyping]);

    // ── Check voice support ────────────────────────────────────────────────

    useEffect(() => {
        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;
        setVoiceSupported(!!SpeechRecognition);
    }, []);

    // ── WebSocket setup ────────────────────────────────────────────────────

    const appendMessage = useCallback((role, text) => {
        setMessages(prev => [...prev, { id: Date.now() + Math.random(), role, text }]);
    }, []);

    const connectWebSocket = useCallback(() => {
        if (!sessionId || !cvId) return;

        const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
        const ws    = new WebSocket(buildWsUrl());
        wsRef.current = ws;

        ws.onopen = () => {
            // Frame đầu tiên: auth + context
            ws.send(JSON.stringify({
                token,
                cv_id:            cvId,
                cv_data:          extractionData,
                job_title:        `${position}${level ? ' (' + level + ')' : ''}`,
                mode,
                duration_minutes: 20,
            }));
        };

        ws.onmessage = (event) => {
            // Backend gửi JSON events
            try {
                const msg = JSON.parse(event.data);

                if (msg.type === 'question' || msg.type === 'message') {
                    setAiTyping(false);
                    appendMessage('ai', msg.content || msg.text || '');
                } else if (msg.type === 'typing') {
                    setAiTyping(true);
                } else if (msg.type === 'end' || msg.type === 'session_ended') {
                    setAiTyping(false);
                    setPhase(PHASE.ENDED);
                    if (msg.content) appendMessage('ai', msg.content);
                } else if (msg.type === 'error') {
                    setAiTyping(false);
                    appendMessage('system', `⚠️ ${msg.content || 'Lỗi từ server.'}`);
                }
            } catch {
                // binary frame (TTS audio) — bỏ qua nếu chưa implement audio playback
            }
        };

        ws.onerror = () => {
            setWsError('Mất kết nối đến server. Vui lòng thử lại.');
            setAiTyping(false);
        };

        ws.onclose = () => {
            if (phase !== PHASE.ENDED) {
                setAiTyping(false);
            }
        };
    }, [sessionId, cvId, extractionData, position, level, mode, appendMessage, phase]);

    // ── Bắt đầu phỏng vấn khi user bấm "Tôi đã sẵn sàng" ─────────────────

    const handleReady = () => {
        setPhase(PHASE.INTERVIEW);
        setAiTyping(true);
        connectWebSocket();
    };

    // ── Cleanup WS khi unmount ─────────────────────────────────────────────

    useEffect(() => {
        return () => {
            if (wsRef.current) wsRef.current.close();
            if (mediaStreamRef.current) {
                mediaStreamRef.current.getTracks().forEach(t => t.stop());
            }
            if (recognitionRef.current) recognitionRef.current.stop();
        };
    }, []);

    // ── Gửi tin nhắn text ─────────────────────────────────────────────────

    const sendText = () => {
        const text = inputText.trim();
        if (!text || aiTyping || phase !== PHASE.INTERVIEW) return;

        appendMessage('user', text);
        setInputText('');
        setAiTyping(true);

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'text_answer', content: text }));
        } else {
            setWsError('Mất kết nối. Vui lòng tải lại trang.');
            setAiTyping(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendText();
        }
    };

    // ── Voice input ────────────────────────────────────────────────────────

    const toggleVoice = async () => {
        if (!voiceSupported) return;

        if (voiceActive) {
            // Dừng recognition
            recognitionRef.current?.stop();
            setVoiceActive(false);
            return;
        }

        // Xin quyền micro
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaStreamRef.current = stream;
        } catch {
            alert('Cho phép LancerAI sử dụng micro để dùng tính năng này.');
            return;
        }

        const SpeechRecognition =
            window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();
        recognitionRef.current = recognition;

        recognition.lang = 'vi-VN';
        recognition.continuous = false;
        recognition.interimResults = true;

        recognition.onresult = (event) => {
            const transcript = Array.from(event.results)
                .map(r => r[0].transcript)
                .join('');
            setInputText(transcript);
        };

        recognition.onend = () => {
            setVoiceActive(false);
            // Tự động gửi nếu có nội dung
            setInputText(prev => {
                if (prev.trim()) {
                    setTimeout(() => sendText(), 100);
                }
                return prev;
            });
        };

        recognition.onerror = () => {
            setVoiceActive(false);
        };

        recognition.start();
        setVoiceActive(true);
    };

    // ── Kết thúc phỏng vấn ────────────────────────────────────────────────

    const handleEnd = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'stop' }));
        }
        setPhase(PHASE.ENDED);
    };

    // ─── Render ───────────────────────────────────────────────────────────

    if (!sessionId) return null; // đang redirect

    const positionLabel = `${position}${level ? ' — ' + level : ''}`;

    return (
        <div style={{ backgroundColor: 'var(--canvas)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Navbar />

            <div style={styles.container}>
                {/* Top bar */}
                <div style={styles.topBar}>
                    <button
                        className="btn-tertiary"
                        onClick={() => navigate('/interview')}
                        style={{ fontSize: '13px' }}
                    >
                        ← Quay lại
                    </button>

                    <div style={styles.sessionInfo}>
                        <span style={{ fontWeight: 600, fontSize: '14px' }}>{sessionName}</span>
                        <span style={styles.sessionMeta}>
                            {positionLabel}
                            {industry ? ` · ${industry}` : ''}
                            {' · '}
                            <span style={{ color: mode === 'mock' ? 'var(--semantic-error, #ef4444)' : 'var(--semantic-success, #22c55e)' }}>
                                {mode === 'mock' ? 'Khắt khe' : 'Chuẩn'}
                            </span>
                        </span>
                    </div>

                    {phase === PHASE.INTERVIEW && (
                        <button
                            className="btn-outline"
                            onClick={handleEnd}
                            style={{ fontSize: '13px', color: 'var(--semantic-error, #ef4444)', borderColor: 'var(--semantic-error, #ef4444)' }}
                        >
                            Kết thúc
                        </button>
                    )}
                    {phase !== PHASE.INTERVIEW && <div style={{ width: '80px' }} />}
                </div>

                {/* Chat box */}
                <div style={styles.chatBox}>

                    {/* Tin nhắn chào mừng — luôn hiển thị đầu tiên */}
                    <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                        <div style={styles.aiAvatar}>AI</div>
                        <div style={styles.bubbleAI}>
                            Xin chào <strong>{userName}</strong>, hãy bắt đầu với buổi phỏng vấn cho vị trí{' '}
                            <strong>{positionLabel}</strong> ngày <strong>{today()}</strong>.
                            {industry ? ` Ngành: ${industry}.` : ''}
                        </div>
                    </div>

                    {/* Messages */}
                    {messages.map(msg => {
                        const isUser   = msg.role === 'user';
                        const isSystem = msg.role === 'system';
                        return (
                            <div
                                key={msg.id}
                                style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }}
                            >
                                {!isUser && !isSystem && <div style={styles.aiAvatar}>AI</div>}
                                <div style={isUser ? styles.bubbleUser : isSystem ? styles.bubbleSystem : styles.bubbleAI}>
                                    {msg.text}
                                </div>
                            </div>
                        );
                    })}

                    {/* AI typing indicator */}
                    {aiTyping && (
                        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                            <div style={styles.aiAvatar}>AI</div>
                            <div style={{ ...styles.bubbleAI, ...styles.typingBubble }}>
                                <span style={styles.dot} />
                                <span style={{ ...styles.dot, animationDelay: '0.2s' }} />
                                <span style={{ ...styles.dot, animationDelay: '0.4s' }} />
                            </div>
                        </div>
                    )}

                    {/* WS error */}
                    {wsError && (
                        <div style={{ textAlign: 'center' }}>
                            <p style={{ color: 'var(--semantic-error, #ef4444)', fontSize: '13px' }}>{wsError}</p>
                        </div>
                    )}

                    <div ref={chatEndRef} />
                </div>

                {/* ── Input area ── */}
                {phase === PHASE.GREETING && (
                    <div style={styles.greetingBar}>
                        <button className="btn-primary" onClick={handleReady} style={{ minWidth: '200px' }}>
                            Tôi đã sẵn sàng 🚀
                        </button>
                    </div>
                )}

                {phase === PHASE.INTERVIEW && (
                    <div style={styles.inputArea}>
                        {/* Voice toggle */}
                        {voiceSupported && (
                            <button
                                onClick={toggleVoice}
                                style={{
                                    ...styles.iconBtn,
                                    color: voiceActive ? 'var(--semantic-error, #ef4444)' : 'var(--muted)',
                                    backgroundColor: voiceActive ? 'rgba(239,68,68,0.08)' : 'transparent',
                                }}
                                title={voiceActive ? 'Dừng nói' : 'Nói câu trả lời'}
                            >
                                {voiceActive ? '🔴' : '🎙️'}
                            </button>
                        )}

                        <textarea
                            ref={inputRef}
                            className="text-input"
                            style={styles.textarea}
                            placeholder={voiceActive ? 'Đang nghe...' : 'Nhập câu trả lời... (Enter để gửi, Shift+Enter xuống dòng)'}
                            value={inputText}
                            onChange={e => setInputText(e.target.value)}
                            onKeyDown={handleKeyDown}
                            disabled={aiTyping || voiceActive}
                            rows={1}
                        />

                        <button
                            className="btn-primary"
                            onClick={sendText}
                            disabled={!inputText.trim() || aiTyping}
                            style={{ flexShrink: 0 }}
                        >
                            Gửi
                        </button>
                    </div>
                )}

                {phase === PHASE.ENDED && (
                    <div style={styles.endedBar}>
                        <p style={{ color: 'var(--muted)', fontSize: '14px', margin: 0 }}>
                            Buổi phỏng vấn đã kết thúc.
                        </p>
                        <button
                            className="btn-primary"
                            onClick={() => navigate('/interview-report', { state: { sessionId } })}
                        >
                            Xem kết quả →
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
};

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = {
    container: {
        maxWidth: '800px',
        margin: '0 auto',
        padding: 'var(--sp-base) var(--sp-lg)',
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        height: 'calc(100vh - var(--nav-height, 60px))',
    },
    topBar: {
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 'var(--sp-sm)',
        gap: 'var(--sp-base)',
    },
    sessionInfo: {
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: '2px',
    },
    sessionMeta: {
        fontSize: '12px',
        color: 'var(--muted)',
    },
    chatBox: {
        flex: 1,
        overflowY: 'auto',
        padding: 'var(--sp-lg)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) 0 0',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-base)',
    },
    aiAvatar: {
        width: '28px', height: '28px',
        borderRadius: 'var(--rounded-full)',
        backgroundColor: 'var(--surface-strong)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '10px', fontWeight: 700,
        color: 'var(--muted)',
        flexShrink: 0,
        marginRight: 'var(--sp-xs)',
        marginTop: '4px',
    },
    bubbleAI: {
        maxWidth: '75%',
        padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) var(--rounded-xl) var(--rounded-xs)',
        backgroundColor: 'var(--surface-strong)',
        color: 'var(--ink)',
        fontSize: '15px',
        lineHeight: 1.6,
        border: '1px solid var(--hairline)',
    },
    bubbleUser: {
        maxWidth: '75%',
        padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) var(--rounded-xs) var(--rounded-xl)',
        backgroundColor: 'var(--primary, var(--ink))',
        color: 'var(--on-primary, #fff)',
        fontSize: '15px',
        lineHeight: 1.6,
    },
    bubbleSystem: {
        maxWidth: '90%',
        padding: 'var(--sp-xs) var(--sp-base)',
        borderRadius: 'var(--rounded-lg)',
        backgroundColor: 'transparent',
        color: 'var(--muted)',
        fontSize: '13px',
        fontStyle: 'italic',
    },
    typingBubble: {
        display: 'flex', alignItems: 'center', gap: '4px',
        padding: 'var(--sp-sm) var(--sp-base)',
        minWidth: '56px',
    },
    dot: {
        display: 'inline-block',
        width: '7px', height: '7px',
        borderRadius: '50%',
        backgroundColor: 'var(--muted)',
        animation: 'bounce 1s ease-in-out infinite',
    },
    greetingBar: {
        padding: 'var(--sp-base)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderTop: 'none',
        borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        display: 'flex',
        justifyContent: 'center',
    },
    inputArea: {
        display: 'flex',
        padding: 'var(--sp-sm)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderTop: 'none',
        borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        gap: 'var(--sp-xs)',
        alignItems: 'flex-end',
    },
    textarea: {
        flex: 1,
        resize: 'none',
        borderRadius: 'var(--rounded-lg)',
        minHeight: '40px',
        maxHeight: '120px',
        overflowY: 'auto',
        lineHeight: 1.5,
        padding: 'var(--sp-sm) var(--sp-base)',
    },
    iconBtn: {
        width: '40px', height: '40px',
        border: 'none', borderRadius: 'var(--rounded-full)',
        cursor: 'pointer', fontSize: '18px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0, transition: 'all var(--transition-base)',
    },
    endedBar: {
        padding: 'var(--sp-base) var(--sp-lg)',
        backgroundColor: 'var(--surface-card)',
        border: '1px solid var(--hairline)',
        borderTop: 'none',
        borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
    },
};

export default ChatPage;
