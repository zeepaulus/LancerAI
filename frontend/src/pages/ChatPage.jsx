// import React, { useState, useRef, useEffect, useCallback } from 'react';
// import { useNavigate, useLocation } from 'react-router-dom';
// import Navbar from '../components/Layout/Navbar';
// import { API_BASE_URL } from '../config/env';
// import { INTERVIEW_WS_PATH } from '../api/paths';
// import * as keys from '../config/storageKeys';

// // ─── Constants ────────────────────────────────────────────────────────────────

// const PHASE = {
//     GREETING:  'greeting',   // Chờ user bấm "Tôi đã sẵn sàng"
//     INTERVIEW: 'interview',  // Đang phỏng vấn
//     ENDED:     'ended',      // Kết thúc
// };

// const STORAGE_KEY_HISTORY = 'lancerai_interview_history';

// // ─── Helpers ──────────────────────────────────────────────────────────────────

// function buildWsUrl() {
//     const base = API_BASE_URL.replace(/^http/, 'ws');
//     return `${base}${INTERVIEW_WS_PATH}`;
// }

// function today() {
//     return new Date().toLocaleDateString('vi-VN', {
//         day: '2-digit', month: '2-digit', year: 'numeric',
//     });
// }

// // ─── Wave animation CSS (inject once) ────────────────────────────────────────

// const WAVE_CSS = `
// @keyframes wave {
//     0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
//     30%            { transform: translateY(-6px); opacity: 1; }
// }
// `;

// function injectWaveCss() {
//     if (document.getElementById('lancerai-wave-css')) return;
//     const style = document.createElement('style');
//     style.id = 'lancerai-wave-css';
//     style.textContent = WAVE_CSS;
//     document.head.appendChild(style);
// }

// // ─── Component ────────────────────────────────────────────────────────────────

// const ChatPage = () => {
//     const navigate = useNavigate();
//     const location = useLocation();
//     const state    = location.state || {};

//     const {
//         sessionId,
//         cvId,
//         extractionData = {},
//         sessionName    = 'Buổi phỏng vấn',
//         industry       = '',
//         position       = 'Vị trí không xác định',
//         level          = '',
//         mode           = 'practice',
//         userName       = 'bạn',
//     } = state;

//     // Redirect nếu vào thẳng không có state
//     useEffect(() => {
//         if (!sessionId || !cvId) navigate('/interview', { replace: true });
//     }, [sessionId, cvId, navigate]);

//     // Inject wave CSS một lần
//     useEffect(() => { injectWaveCss(); }, []);

//     // ── State ──────────────────────────────────────────────────────────────

//     const [phase, setPhase]         = useState(PHASE.GREETING);
//     const [messages, setMessages]   = useState([]);
//     const [inputText, setInputText] = useState('');
//     const [aiTyping, setAiTyping]   = useState(false);
//     const [wsError, setWsError]     = useState('');

//     // Voice
//     const [voiceActive, setVoiceActive]       = useState(false);
//     const [voiceSupported, setVoiceSupported] = useState(false);

//     // Buffer messages nhận được trước khi user sẵn sàng
//     const pendingMessagesRef = useRef([]);
//     const phaseRef           = useRef(PHASE.GREETING);

//     // Refs
//     const wsRef          = useRef(null);
//     const chatEndRef     = useRef(null);
//     const inputRef       = useRef(null);
//     const recognitionRef = useRef(null);
//     const mediaStreamRef = useRef(null);

//     // Giữ phaseRef đồng bộ với phase state
//     useEffect(() => { phaseRef.current = phase; }, [phase]);

//     // ── Auto-scroll ────────────────────────────────────────────────────────

//     useEffect(() => {
//         chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//     }, [messages, aiTyping]);

//     // ── Voice support ─────────────────────────────────────────────────────

//     useEffect(() => {
//         const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
//         setVoiceSupported(!!SR);
//     }, []);

//     // ── Append message ─────────────────────────────────────────────────────

//     const appendMessage = useCallback((role, text) => {
//         setMessages(prev => [...prev, { id: Date.now() + Math.random(), role, text }]);
//     }, []);

//     // ── WebSocket ──────────────────────────────────────────────────────────

//     const connectWebSocket = useCallback(() => {
//         if (!sessionId || !cvId) return;

//         const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
//         const ws    = new WebSocket(buildWsUrl());
//         wsRef.current = ws;

//         ws.onopen = () => {
//             ws.send(JSON.stringify({
//                 token,
//                 cv_id:            cvId,
//                 cv_data:          extractionData,
//                 job_title:        `${position}${level ? ' (' + level + ')' : ''}`,
//                 mode,
//                 duration_minutes: 20,
//             }));
//         };

//         ws.onmessage = (event) => {
//             if (typeof event.data !== 'string') return; // bỏ qua binary PCM

//             let msg;
//             try { msg = JSON.parse(event.data); }
//             catch { return; }

//             const ev = msg.event || msg.type;

//             // Helper: hiển thị ngay hoặc buffer lại tuỳ phase
//             const showOrBuffer = (role, text) => {
//                 if (!text) return;
//                 if (phaseRef.current === PHASE.GREETING) {
//                     // Buffer lại, hiển thị sau khi user bấm sẵn sàng
//                     pendingMessagesRef.current.push({ id: Date.now() + Math.random(), role, text });
//                 } else {
//                     appendMessage(role, text);
//                 }
//             };

//             if (ev === 'assistant_text') {
//                 setAiTyping(false);
//                 showOrBuffer('ai', msg.text);

//             } else if (ev === 'phase_change') {
//                 if (msg.phase === 'processing' || msg.phase === 'speaking') {
//                     // Chỉ hiện typing indicator nếu đã qua greeting
//                     if (phaseRef.current !== PHASE.GREETING) setAiTyping(true);
//                 } else if (msg.phase === 'listening') {
//                     setAiTyping(false);
//                 }

//             } else if (ev === 'transcript') {
//                 showOrBuffer('user', msg.text);

//             } else if (ev === 'session_started') {
//                 // Chưa chuyển phase → không hiện typing indicator
//             } else if (ev === 'time_up' || ev === 'session_ended') {
//                 setAiTyping(false);
//                 setPhase(PHASE.ENDED);
//                 if (msg.evaluation?.final_feedback) {
//                     appendMessage('ai', msg.evaluation.final_feedback);
//                 }

//             } else if (ev === 'error') {
//                 setAiTyping(false);
//                 // Chỉ hiện lỗi nếu đã trong interview, không hiện lỗi nội bộ pipeline
//                 if (phaseRef.current === PHASE.INTERVIEW) {
//                     appendMessage('system', `⚠️ ${msg.message || 'Lỗi từ server.'}`);
//                 }
//             }
//         };

//         ws.onerror = () => {
//             // Không tự động hiện lỗi "Mất kết nối" —
//             // ws.onclose sẽ xử lý nếu cần
//             setAiTyping(false);
//         };

//         ws.onclose = (evt) => {
//             setAiTyping(false);
//             // Chỉ báo lỗi nếu đóng bất thường trong lúc phỏng vấn
//             if (phaseRef.current === PHASE.INTERVIEW && evt.code !== 1000 && evt.code !== 1001) {
//                 setWsError('Kết nối bị gián đoạn. Vui lòng tải lại trang.');
//             }
//         };
//     }, [sessionId, cvId, extractionData, position, level, mode, appendMessage]);

//     // ── Bấm "Tôi đã sẵn sàng" ─────────────────────────────────────────────

//     const handleReady = () => {
//         setPhase(PHASE.INTERVIEW);
//         phaseRef.current = PHASE.INTERVIEW;

//         // Kết nối WS — backend sẽ generate câu hỏi đầu tiên
//         connectWebSocket();

//         // Flush các message đã buffer (nếu có từ connect trước đó)
//         if (pendingMessagesRef.current.length > 0) {
//             setMessages(prev => [...prev, ...pendingMessagesRef.current]);
//             pendingMessagesRef.current = [];
//         }

//         // Hiện typing indicator vì LLM đang generate
//         setAiTyping(true);
//     };

//     // ── Cleanup WS khi unmount ─────────────────────────────────────────────

//     useEffect(() => {
//         return () => {
//             if (wsRef.current) wsRef.current.close();
//             if (mediaStreamRef.current) {
//                 mediaStreamRef.current.getTracks().forEach(t => t.stop());
//             }
//             if (recognitionRef.current) recognitionRef.current.stop();
//         };
//     }, []);

//     // ── Gửi text ──────────────────────────────────────────────────────────

//     const sendText = useCallback(() => {
//         const text = inputText.trim();
//         if (!text || aiTyping || phase !== PHASE.INTERVIEW) return;

//         appendMessage('user', text);
//         setInputText('');
//         setAiTyping(true);

//         if (wsRef.current?.readyState === WebSocket.OPEN) {
//             wsRef.current.send(JSON.stringify({ type: 'text_answer', content: text }));
//         } else {
//             setWsError('Mất kết nối. Vui lòng tải lại trang.');
//             setAiTyping(false);
//         }
//     }, [inputText, aiTyping, phase, appendMessage]);

//     const handleKeyDown = (e) => {
//         if (e.key === 'Enter' && !e.shiftKey) {
//             e.preventDefault();
//             sendText();
//         }
//     };

//     // ── Voice ──────────────────────────────────────────────────────────────

//     const toggleVoice = async () => {
//         if (!voiceSupported) return;

//         if (voiceActive) {
//             recognitionRef.current?.stop();
//             setVoiceActive(false);
//             return;
//         }

//         try {
//             const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//             mediaStreamRef.current = stream;
//         } catch {
//             alert('Cho phép LancerAI sử dụng micro để dùng tính năng này.');
//             return;
//         }

//         const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
//         const recognition = new SR();
//         recognitionRef.current = recognition;

//         recognition.lang = 'vi-VN';
//         recognition.continuous = false;
//         recognition.interimResults = true;

//         recognition.onresult = (event) => {
//             const transcript = Array.from(event.results).map(r => r[0].transcript).join('');
//             setInputText(transcript);
//         };

//         recognition.onend = () => {
//             setVoiceActive(false);
//             setInputText(prev => {
//                 if (prev.trim()) setTimeout(() => sendText(), 100);
//                 return prev;
//             });
//         };

//         recognition.onerror = () => setVoiceActive(false);
//         recognition.start();
//         setVoiceActive(true);
//     };

//     // ── Kết thúc phỏng vấn ────────────────────────────────────────────────

//     const handleEnd = () => {
//         if (wsRef.current?.readyState === WebSocket.OPEN) {
//             wsRef.current.send(JSON.stringify({ action: 'stop' }));
//         }
//         setPhase(PHASE.ENDED);
//     };

//     // ── Lưu lại (rời trang, lưu history) ──────────────────────────────────

//     const handleSave = () => {
//         // Lưu session vào localStorage để InterviewPage hiển thị
//         const existing = JSON.parse(localStorage.getItem(STORAGE_KEY_HISTORY) || '[]');
//         const alreadySaved = existing.some(s => s.session_id === sessionId);

//         if (!alreadySaved) {
//             const entry = {
//                 session_id:  sessionId,
//                 title:       sessionName,
//                 position,
//                 level,
//                 industry,
//                 mode,
//                 created_at:  new Date().toISOString(),
//                 status:      'incomplete', // "Chưa hoàn thành"
//             };
//             localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify([entry, ...existing]));
//         }

//         navigate('/interview');
//     };

//     // ─── Render ───────────────────────────────────────────────────────────

//     if (!sessionId) return null;

//     const positionLabel = `${position}${level ? ' — ' + level : ''}`;

//     return (
//         <div style={{ backgroundColor: 'var(--canvas)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
//             <Navbar />

//             <div style={styles.container}>
//                 {/* Top bar */}
//                 <div style={styles.topBar}>
//                     <button
//                         className="btn-tertiary"
//                         onClick={handleSave}
//                         style={{ fontSize: '13px' }}
//                     >
//                         💾 Lưu lại
//                     </button>

//                     <div style={styles.sessionInfo}>
//                         <span style={{ fontWeight: 600, fontSize: '14px' }}>{sessionName}</span>
//                         <span style={styles.sessionMeta}>
//                             {positionLabel}
//                             {industry ? ` · ${industry}` : ''}
//                             {' · '}
//                             <span style={{ color: mode === 'mock' ? 'var(--semantic-error, #ef4444)' : 'var(--semantic-success, #22c55e)' }}>
//                                 {mode === 'mock' ? 'Khắt khe' : 'Chuẩn'}
//                             </span>
//                         </span>
//                     </div>

//                     {phase === PHASE.INTERVIEW ? (
//                         <button
//                             className="btn-outline"
//                             onClick={handleEnd}
//                             style={{ fontSize: '13px', color: 'var(--semantic-error, #ef4444)', borderColor: 'var(--semantic-error, #ef4444)' }}
//                         >
//                             Kết thúc
//                         </button>
//                     ) : (
//                         <div style={{ width: '80px' }} />
//                     )}
//                 </div>

//                 {/* Chat box */}
//                 <div style={styles.chatBox}>

//                     {/* Lời chào tĩnh — luôn đầu tiên */}
//                     <div style={styles.bubbleAI}>
//                         Xin chào <strong>{userName}</strong>, hãy bắt đầu với buổi phỏng vấn cho vị trí{' '}
//                         <strong>{positionLabel}</strong> ngày <strong>{today()}</strong>.
//                         {industry ? ` Ngành: ${industry}.` : ''}
//                     </div>

//                     {/* Messages */}
//                     {messages.map(msg => {
//                         const isUser   = msg.role === 'user';
//                         const isSystem = msg.role === 'system';
//                         return (
//                             <div
//                                 key={msg.id}
//                                 style={{
//                                     display: 'flex',
//                                     justifyContent: isUser ? 'flex-end' : 'flex-start',
//                                 }}
//                             >
//                                 <div style={isUser ? styles.bubbleUser : isSystem ? styles.bubbleSystem : styles.bubbleAI}>
//                                     {msg.text}
//                                 </div>
//                             </div>
//                         );
//                     })}

//                     {/* Typing indicator — 3 chấm lượn sóng */}
//                     {aiTyping && (
//                         <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
//                             <div style={{ ...styles.bubbleAI, ...styles.typingBubble }}>
//                                 {[0, 1, 2].map(i => (
//                                     <span
//                                         key={i}
//                                         style={{
//                                             ...styles.dot,
//                                             animation: `wave 1.2s ease-in-out infinite`,
//                                             animationDelay: `${i * 0.18}s`,
//                                         }}
//                                     />
//                                 ))}
//                             </div>
//                         </div>
//                     )}

//                     {/* WS error — chỉ hiện khi có lỗi thật */}
//                     {wsError && (
//                         <div style={{ textAlign: 'center' }}>
//                             <p style={{ color: 'var(--semantic-error, #ef4444)', fontSize: '13px' }}>{wsError}</p>
//                         </div>
//                     )}

//                     <div ref={chatEndRef} />
//                 </div>

//                 {/* ── Input area ── */}
//                 {phase === PHASE.GREETING && (
//                     <div style={styles.greetingBar}>
//                         <button
//                             className="btn-primary"
//                             onClick={handleReady}
//                             style={{ minWidth: '200px' }}
//                         >
//                             Tôi đã sẵn sàng 🚀
//                         </button>
//                     </div>
//                 )}

//                 {phase === PHASE.INTERVIEW && (
//                     <div style={styles.inputArea}>
//                         {voiceSupported && (
//                             <button
//                                 onClick={toggleVoice}
//                                 style={{
//                                     ...styles.iconBtn,
//                                     color: voiceActive ? 'var(--semantic-error, #ef4444)' : 'var(--muted)',
//                                     backgroundColor: voiceActive ? 'rgba(239,68,68,0.08)' : 'transparent',
//                                 }}
//                                 title={voiceActive ? 'Dừng nói' : 'Nói câu trả lời'}
//                             >
//                                 {voiceActive ? '🔴' : '🎙️'}
//                             </button>
//                         )}

//                         <textarea
//                             ref={inputRef}
//                             className="text-input"
//                             style={styles.textarea}
//                             placeholder={voiceActive ? 'Đang nghe...' : 'Nhập câu trả lời... (Enter để gửi, Shift+Enter xuống dòng)'}
//                             value={inputText}
//                             onChange={e => setInputText(e.target.value)}
//                             onKeyDown={handleKeyDown}
//                             disabled={aiTyping || voiceActive}
//                             rows={1}
//                         />

//                         <button
//                             className="btn-primary"
//                             onClick={sendText}
//                             disabled={!inputText.trim() || aiTyping}
//                             style={{ flexShrink: 0 }}
//                         >
//                             Gửi
//                         </button>
//                     </div>
//                 )}

//                 {phase === PHASE.ENDED && (
//                     <div style={styles.endedBar}>
//                         <p style={{ color: 'var(--muted)', fontSize: '14px', margin: 0 }}>
//                             Buổi phỏng vấn đã kết thúc.
//                         </p>
//                         <button
//                             className="btn-primary"
//                             onClick={() => navigate('/interview-report', { state: { sessionId } })}
//                         >
//                             Xem kết quả →
//                         </button>
//                     </div>
//                 )}
//             </div>
//         </div>
//     );
// };

// // ─── Styles ───────────────────────────────────────────────────────────────────

// const styles = {
//     container: {
//         maxWidth: '800px',
//         margin: '0 auto',
//         padding: 'var(--sp-base) var(--sp-lg)',
//         flex: 1,
//         display: 'flex',
//         flexDirection: 'column',
//         height: 'calc(100vh - var(--nav-height, 60px))',
//     },
//     topBar: {
//         display: 'flex',
//         alignItems: 'center',
//         justifyContent: 'space-between',
//         marginBottom: 'var(--sp-sm)',
//         gap: 'var(--sp-base)',
//     },
//     sessionInfo: {
//         flex: 1,
//         display: 'flex',
//         flexDirection: 'column',
//         alignItems: 'center',
//         gap: '2px',
//     },
//     sessionMeta: {
//         fontSize: '12px',
//         color: 'var(--muted)',
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
//     bubbleAI: {
//         maxWidth: '75%',
//         padding: 'var(--sp-sm) var(--sp-base)',
//         borderRadius: 'var(--rounded-xl)',
//         backgroundColor: 'var(--surface-strong)',
//         color: 'var(--ink)',
//         fontSize: '15px',
//         lineHeight: 1.6,
//         border: '1px solid var(--hairline)',
//         alignSelf: 'flex-start',
//     },
//     bubbleUser: {
//         maxWidth: '75%',
//         padding: 'var(--sp-sm) var(--sp-base)',
//         borderRadius: 'var(--rounded-xl)',
//         backgroundColor: 'var(--primary, var(--ink))',
//         color: 'var(--on-primary, #fff)',
//         fontSize: '15px',
//         lineHeight: 1.6,
//         alignSelf: 'flex-end',
//     },
//     bubbleSystem: {
//         maxWidth: '90%',
//         padding: 'var(--sp-xs) var(--sp-base)',
//         borderRadius: 'var(--rounded-lg)',
//         backgroundColor: 'transparent',
//         color: 'var(--muted)',
//         fontSize: '13px',
//         fontStyle: 'italic',
//     },
//     typingBubble: {
//         display: 'flex',
//         alignItems: 'center',
//         gap: '5px',
//         padding: '12px 16px',
//         minWidth: '60px',
//     },
//     dot: {
//         display: 'inline-block',
//         width: '7px',
//         height: '7px',
//         borderRadius: '50%',
//         backgroundColor: 'var(--muted)',
//     },
//     greetingBar: {
//         padding: 'var(--sp-base)',
//         backgroundColor: 'var(--surface-card)',
//         border: '1px solid var(--hairline)',
//         borderTop: 'none',
//         borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
//         display: 'flex',
//         justifyContent: 'center',
//     },
//     inputArea: {
//         display: 'flex',
//         padding: 'var(--sp-sm)',
//         backgroundColor: 'var(--surface-card)',
//         border: '1px solid var(--hairline)',
//         borderTop: 'none',
//         borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
//         gap: 'var(--sp-xs)',
//         alignItems: 'flex-end',
//     },
//     textarea: {
//         flex: 1,
//         resize: 'none',
//         borderRadius: 'var(--rounded-lg)',
//         minHeight: '40px',
//         maxHeight: '120px',
//         overflowY: 'auto',
//         lineHeight: 1.5,
//         padding: 'var(--sp-sm) var(--sp-base)',
//     },
//     iconBtn: {
//         width: '40px', height: '40px',
//         border: 'none', borderRadius: 'var(--rounded-full)',
//         cursor: 'pointer', fontSize: '18px',
//         display: 'flex', alignItems: 'center', justifyContent: 'center',
//         flexShrink: 0, transition: 'all var(--transition-base)',
//     },
//     endedBar: {
//         padding: 'var(--sp-base) var(--sp-lg)',
//         backgroundColor: 'var(--surface-card)',
//         border: '1px solid var(--hairline)',
//         borderTop: 'none',
//         borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
//         display: 'flex',
//         justifyContent: 'space-between',
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
    GREETING:  'greeting',
    INTERVIEW: 'interview',
    ENDED:     'ended',
};

const STORAGE_KEY_HISTORY = 'lancerai_interview_history';

// ─── Helpers ──────────────────────────────────────────────────────────────────

function buildWsUrl() {
    const base = API_BASE_URL.replace(/^http/, 'ws');
    return `${base}${INTERVIEW_WS_PATH}`;
}

function today() {
    return new Date().toLocaleDateString('vi-VN', {
        day: '2-digit', month: '2-digit', year: 'numeric',
    });
}

function formatDuration(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${m}:${s}`;
}

// ─── CSS injection ────────────────────────────────────────────────────────────

const EXTRA_CSS = `
@keyframes wave {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30%            { transform: translateY(-6px); opacity: 1; }
}
@keyframes pulse-ring {
    0%   { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    70%  { box-shadow: 0 0 0 8px rgba(239,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}
`;

function injectCss() {
    if (document.getElementById('lancerai-chat-css')) return;
    const s = document.createElement('style');
    s.id = 'lancerai-chat-css';
    s.textContent = EXTRA_CSS;
    document.head.appendChild(s);
}

// ─── Component ────────────────────────────────────────────────────────────────

const ChatPage = () => {
    const navigate = useNavigate();
    const location = useLocation();
    const state    = location.state || {};

    const {
        sessionId, cvId, extractionData = {},
        sessionName = 'Buổi phỏng vấn', industry = '',
        position = 'Vị trí không xác định', level = '',
        mode = 'practice', userName = 'bạn',
    } = state;

    useEffect(() => {
        if (!sessionId || !cvId) navigate('/interview', { replace: true });
    }, [sessionId, cvId, navigate]);

    useEffect(() => { injectCss(); }, []);

    // ── Core state ─────────────────────────────────────────────────────────

    const [phase, setPhase]         = useState(PHASE.GREETING);
    const [messages, setMessages]   = useState([]);
    const [inputText, setInputText] = useState('');
    const [aiTyping, setAiTyping]   = useState(false);
    const [wsError, setWsError]     = useState('');

    // ── Voice recorder state ───────────────────────────────────────────────
    // voiceMode: 'idle' | 'recording' | 'paused'
    const [voiceMode, setVoiceMode]       = useState('idle');
    const [voiceSupported, setVoiceSupported] = useState(false);
    const [recSeconds, setRecSeconds]     = useState(0);   // thời lượng đếm
    const [audioBlob, setAudioBlob]       = useState(null);// blob khi kết thúc

    // ── Refs ───────────────────────────────────────────────────────────────
    const pendingMessagesRef = useRef([]);
    const phaseRef           = useRef(PHASE.GREETING);
    const wsRef              = useRef(null);
    const chatEndRef         = useRef(null);
    const textareaRef        = useRef(null);
    const mediaRecorderRef   = useRef(null);
    const audioChunksRef     = useRef([]);
    const timerRef           = useRef(null);
    const streamRef          = useRef(null);

    useEffect(() => { phaseRef.current = phase; }, [phase]);

    // ── Auto-scroll ────────────────────────────────────────────────────────

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages, aiTyping]);

    // ── Textarea auto-resize ───────────────────────────────────────────────

    const resizeTextarea = () => {
        const el = textareaRef.current;
        if (!el) return;
        el.style.height = 'auto';
        el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    };

    useEffect(() => { resizeTextarea(); }, [inputText]);

    // ── Check voice support ────────────────────────────────────────────────

    useEffect(() => {
        setVoiceSupported(!!(navigator.mediaDevices && window.MediaRecorder));
    }, []);

    // ── Append message ─────────────────────────────────────────────────────

    const appendMessage = useCallback((role, text) => {
        setMessages(prev => [...prev, { id: Date.now() + Math.random(), role, text }]);
    }, []);

    // ── WebSocket ──────────────────────────────────────────────────────────

    const connectWebSocket = useCallback(() => {
        if (!sessionId || !cvId) return;
        const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
        const ws    = new WebSocket(buildWsUrl());
        wsRef.current = ws;

        ws.onopen = () => {
            ws.send(JSON.stringify({
                token, cv_id: cvId, cv_data: extractionData,
                job_title: `${position}${level ? ' (' + level + ')' : ''}`,
                focus_area: `${industry} — ${position} — ${level}`,
                session_id: sessionId,
                mode, duration_minutes: 20,
            }));
        };

        ws.onmessage = (event) => {
            if (typeof event.data !== 'string') return;
            let msg;
            try { msg = JSON.parse(event.data); } catch { return; }

            const ev = msg.event || msg.type;

            const showOrBuffer = (role, text) => {
                if (!text) return;
                if (phaseRef.current === PHASE.GREETING) {
                    pendingMessagesRef.current.push({ id: Date.now() + Math.random(), role, text });
                } else {
                    appendMessage(role, text);
                }
            };

            if (ev === 'assistant_text') {
                setAiTyping(false);
                showOrBuffer('ai', msg.text);

            } else if (ev === 'phase_change') {
                if (msg.phase === 'processing' || msg.phase === 'speaking') {
                    if (phaseRef.current !== PHASE.GREETING) setAiTyping(true);
                } else if (msg.phase === 'listening') {
                    setAiTyping(false);
                }

            } else if (ev === 'transcript') {
                // Backend xác nhận transcript — đây là nguồn duy nhất append message user
                showOrBuffer('user', msg.text);

            } else if (ev === 'session_started') {
                // không làm gì

            } else if (ev === 'time_up' || ev === 'session_ended') {
                setAiTyping(false);
                setPhase(PHASE.ENDED);
                if (msg.evaluation?.final_feedback) {
                    appendMessage('ai', msg.evaluation.final_feedback);
                }

            } else if (ev === 'error') {
                setAiTyping(false);
                if (phaseRef.current === PHASE.INTERVIEW) {
                    appendMessage('system', `⚠️ ${msg.message || 'Lỗi từ server.'}`);
                }
            }
        };

        ws.onerror = () => { setAiTyping(false); };

        ws.onclose = (evt) => {
            setAiTyping(false);
            if (phaseRef.current === PHASE.INTERVIEW && evt.code !== 1000 && evt.code !== 1001) {
                setWsError('Kết nối bị gián đoạn. Vui lòng tải lại trang.');
            }
        };
    }, [sessionId, cvId, extractionData, position, level, mode, appendMessage]);

    // ── Bấm "Tôi đã sẵn sàng" ─────────────────────────────────────────────

    const handleReady = () => {
        setPhase(PHASE.INTERVIEW);
        phaseRef.current = PHASE.INTERVIEW;
        connectWebSocket();
        if (pendingMessagesRef.current.length > 0) {
            setMessages(prev => [...prev, ...pendingMessagesRef.current]);
            pendingMessagesRef.current = [];
        }
        setAiTyping(true);
    };

    // ── Cleanup ────────────────────────────────────────────────────────────

    useEffect(() => {
        return () => {
            wsRef.current?.close();
            stopTimer();
            streamRef.current?.getTracks().forEach(t => t.stop());
        };
    }, []);

    // ── Gửi text ──────────────────────────────────────────────────────────
    // Không append message ở đây — backend sẽ confirm qua event 'transcript'

    const sendText = useCallback(() => {
        const text = inputText.trim();
        if (!text || aiTyping || phase !== PHASE.INTERVIEW) return;

        setInputText('');
        setAiTyping(true);

        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'text_answer', content: text }));
        } else {
            setWsError('Mất kết nối. Vui lòng tải lại trang.');
            setAiTyping(false);
        }
    }, [inputText, aiTyping, phase]);

    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendText();
        }
    };

    // ── Voice recorder ─────────────────────────────────────────────────────

    const stopTimer = () => {
        if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    };

    const startTimer = () => {
        setRecSeconds(0);
        timerRef.current = setInterval(() => setRecSeconds(s => s + 1), 1000);
    };

    // Bắt đầu ghi âm lần đầu
    const startVoice = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;
        } catch {
            alert('Cho phép LancerAI sử dụng micro để dùng tính năng này.');
            return;
        }

        audioChunksRef.current = [];
        const mr = new MediaRecorder(streamRef.current);
        mediaRecorderRef.current = mr;

        mr.ondataavailable = (e) => { if (e.data.size > 0) audioChunksRef.current.push(e.data); };
        mr.onstop = () => {
            const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            setAudioBlob(blob);
        };

        mr.start();
        setVoiceMode('recording');
        startTimer();
    };

    // Tạm dừng ghi
    const pauseVoice = () => {
        mediaRecorderRef.current?.pause();
        stopTimer();
        setVoiceMode('paused');
    };

    // Tiếp tục ghi
    const resumeVoice = () => {
        mediaRecorderRef.current?.resume();
        timerRef.current = setInterval(() => setRecSeconds(s => s + 1), 1000);
        setVoiceMode('recording');
    };

    // Xoá recording, quay về text input
    const discardVoice = () => {
        mediaRecorderRef.current?.stop();
        stopTimer();
        streamRef.current?.getTracks().forEach(t => t.stop());
        audioChunksRef.current = [];
        setAudioBlob(null);
        setRecSeconds(0);
        setVoiceMode('idle');
    };

    // Gửi audio — hiện tại dùng WebSpeech API để transcribe rồi gửi text
    // (vì backend text_answer đã hoạt động; khi STT backend sẵn sàng thì gửi raw bytes)
    const sendVoice = async () => {
        if (!audioBlob) return;

        // Dùng WebSpeech để lấy transcript từ blob
        // Cách đơn giản nhất hiện tại: đọc blob qua AudioContext + SpeechRecognition
        // Tạm thời: gửi thông báo cho user biết đang xử lý rồi dùng SpeechRecognition live
        // vì Web Speech API không nhận blob — plan B: gửi bytes thẳng lên WS (khi backend STT sẵn)
        const wsReady = wsRef.current?.readyState === WebSocket.OPEN;

        if (wsReady) {
            // Gửi raw audio bytes để backend STT xử lý
            const arrayBuffer = await audioBlob.arrayBuffer();
            wsRef.current.send(arrayBuffer);
            setAiTyping(true);
        } else {
            setWsError('Mất kết nối. Vui lòng tải lại trang.');
        }

        // Reset voice UI
        stopTimer();
        streamRef.current?.getTracks().forEach(t => t.stop());
        setAudioBlob(null);
        setRecSeconds(0);
        setVoiceMode('idle');
    };

    // ── Kết thúc / Lưu ────────────────────────────────────────────────────

    const handleEnd = () => {
        wsRef.current?.readyState === WebSocket.OPEN &&
            wsRef.current.send(JSON.stringify({ action: 'stop' }));
        setPhase(PHASE.ENDED);
    };

    const handleSave = () => {
        const existing = JSON.parse(localStorage.getItem(STORAGE_KEY_HISTORY) || '[]');
        if (!existing.some(s => s.session_id === sessionId)) {
            localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify([{
                session_id: sessionId, title: sessionName,
                position, level, industry, mode,
                created_at: new Date().toISOString(),
                status: 'incomplete',
            }, ...existing]));
        }
        navigate('/interview');
    };

    // ─── Render ───────────────────────────────────────────────────────────

    if (!sessionId) return null;

    const positionLabel = `${position}${level ? ' — ' + level : ''}`;
    const isVoiceUI = voiceMode !== 'idle'; // đang trong chế độ ghi âm

    return (
        <div style={{ backgroundColor: 'var(--canvas)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Navbar />
            <div style={styles.container}>

                {/* Top bar */}
                <div style={styles.topBar}>
                    <button className="btn-tertiary" onClick={handleSave} style={{ fontSize: '13px' }}>
                        💾 Lưu lại
                    </button>
                    <div style={styles.sessionInfo}>
                        <span style={{ fontWeight: 600, fontSize: '14px' }}>{sessionName}</span>
                        <span style={styles.sessionMeta}>
                            {positionLabel}{industry ? ` · ${industry}` : ''} ·{' '}
                            <span style={{ color: mode === 'mock' ? 'var(--semantic-error,#ef4444)' : 'var(--semantic-success,#22c55e)' }}>
                                {mode === 'mock' ? 'Khắt khe' : 'Chuẩn'}
                            </span>
                        </span>
                    </div>
                    {phase === PHASE.INTERVIEW ? (
                        <button
                            className="btn-outline"
                            onClick={handleEnd}
                            style={{ fontSize: '13px', color: 'var(--semantic-error,#ef4444)', borderColor: 'var(--semantic-error,#ef4444)' }}
                        >
                            Kết thúc
                        </button>
                    ) : <div style={{ width: '80px' }} />}
                </div>

                {/* Chat box */}
                <div style={styles.chatBox}>
                    {/* Lời chào tĩnh */}
                    <div style={styles.bubbleAI}>
                        Xin chào <strong>{userName}</strong>, hãy bắt đầu với buổi phỏng vấn cho vị trí{' '}
                        <strong>{positionLabel}</strong> ngày <strong>{today()}</strong>.
                        {industry ? ` Ngành: ${industry}.` : ''}
                    </div>

                    {/* Messages */}
                    {messages.map(msg => {
                        const isUser = msg.role === 'user';
                        const isSystem = msg.role === 'system';
                        return (
                            <div key={msg.id} style={{ display: 'flex', justifyContent: isUser ? 'flex-end' : 'flex-start' }}>
                                <div style={isUser ? styles.bubbleUser : isSystem ? styles.bubbleSystem : styles.bubbleAI}>
                                    {msg.text}
                                </div>
                            </div>
                        );
                    })}

                    {/* Typing indicator */}
                    {aiTyping && (
                        <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                            <div style={{ ...styles.bubbleAI, ...styles.typingBubble }}>
                                {[0, 1, 2].map(i => (
                                    <span key={i} style={{ ...styles.dot, animation: 'wave 1.2s ease-in-out infinite', animationDelay: `${i * 0.18}s` }} />
                                ))}
                            </div>
                        </div>
                    )}

                    {wsError && (
                        <div style={{ textAlign: 'center' }}>
                            <p style={{ color: 'var(--semantic-error,#ef4444)', fontSize: '13px' }}>{wsError}</p>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                {/* ── Input area ── */}

                {phase === PHASE.GREETING && (
                    <div style={styles.bottomBar}>
                        <button className="btn-primary" onClick={handleReady} style={{ minWidth: '200px' }}>
                            Tôi đã sẵn sàng 🚀
                        </button>
                    </div>
                )}

                {phase === PHASE.INTERVIEW && !isVoiceUI && (
                    /* ── Text mode ── */
                    <div style={styles.inputArea}>
                        {voiceSupported && (
                            <button
                                onClick={startVoice}
                                style={{ ...styles.iconBtn, color: 'var(--muted)' }}
                                title="Ghi âm câu trả lời"
                                disabled={aiTyping}
                            >
                                🎙️
                            </button>
                        )}
                        <textarea
                            ref={textareaRef}
                            className="text-input"
                            style={styles.textarea}
                            placeholder="Nhập câu trả lời... (Enter để gửi, Shift+Enter xuống dòng)"
                            value={inputText}
                            onChange={e => { setInputText(e.target.value); resizeTextarea(); }}
                            onKeyDown={handleKeyDown}
                            disabled={aiTyping}
                            rows={1}
                        />
                        <button
                            className="btn-primary"
                            onClick={sendText}
                            disabled={!inputText.trim() || aiTyping}
                            style={{ flexShrink: 0, alignSelf: 'flex-end' }}
                        >
                            Gửi
                        </button>
                    </div>
                )}

                {phase === PHASE.INTERVIEW && isVoiceUI && (
                    /* ── Voice recorder UI ── */
                    <div style={styles.recorderBar}>
                        {/* Nút thùng rác — xoá recording */}
                        <button
                            onClick={discardVoice}
                            style={{ ...styles.iconBtn, color: 'var(--semantic-error,#ef4444)', fontSize: '20px' }}
                            title="Xoá đoạn ghi âm"
                        >
                            🗑️
                        </button>

                        {/* Dải recorder */}
                        <div style={styles.recorderTrack}>
                            {/* Nút Play/Pause */}
                            <button
                                onClick={voiceMode === 'recording' ? pauseVoice : resumeVoice}
                                style={styles.recPlayBtn}
                                title={voiceMode === 'recording' ? 'Tạm dừng' : 'Tiếp tục'}
                            >
                                {voiceMode === 'recording' ? (
                                    /* Pause icon */
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                                        <rect x="6" y="4" width="4" height="16" rx="1" />
                                        <rect x="14" y="4" width="4" height="16" rx="1" />
                                    </svg>
                                ) : (
                                    /* Play icon */
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
                                        <polygon points="5,3 19,12 5,21" />
                                    </svg>
                                )}
                            </button>

                            {/* Waveform giả + timer */}
                            <div style={styles.recMiddle}>
                                {voiceMode === 'recording' && (
                                    <div style={styles.waveform}>
                                        {Array.from({ length: 20 }).map((_, i) => (
                                            <div
                                                key={i}
                                                style={{
                                                    ...styles.waveBar,
                                                    height: `${8 + Math.sin(i * 0.8) * 6}px`,
                                                    animationDelay: `${i * 0.06}s`,
                                                    animation: 'wave 0.8s ease-in-out infinite',
                                                }}
                                            />
                                        ))}
                                    </div>
                                )}
                                {voiceMode === 'paused' && (
                                    <span style={{ color: '#aaa', fontSize: '13px' }}>Đã tạm dừng</span>
                                )}
                            </div>

                            <span style={styles.recTimer}>{formatDuration(recSeconds)}</span>
                        </div>

                        {/* Nút Gửi */}
                        <button
                            className="btn-primary"
                            onClick={sendVoice}
                            disabled={aiTyping}
                            style={{ flexShrink: 0, fontSize: '13px' }}
                        >
                            Gửi
                        </button>
                    </div>
                )}

                {phase === PHASE.ENDED && (
                    <div style={styles.bottomBar}>
                        <p style={{ color: 'var(--muted)', fontSize: '14px', margin: 0 }}>
                            Buổi phỏng vấn đã kết thúc.
                        </p>
                        <button className="btn-primary" onClick={() => navigate('/interview-report', { state: { sessionId } })}>
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
        maxWidth: '800px', margin: '0 auto',
        padding: 'var(--sp-base) var(--sp-lg)',
        flex: 1, display: 'flex', flexDirection: 'column',
        height: 'calc(100vh - var(--nav-height, 60px))',
    },
    topBar: {
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 'var(--sp-sm)', gap: 'var(--sp-base)',
    },
    sessionInfo: {
        flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
    },
    sessionMeta: { fontSize: '12px', color: 'var(--muted)' },
    chatBox: {
        flex: 1, overflowY: 'auto', padding: 'var(--sp-lg)',
        backgroundColor: 'var(--surface-card)', border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) 0 0',
        display: 'flex', flexDirection: 'column', gap: 'var(--sp-base)',
    },
    bubbleAI: {
        maxWidth: '75%', padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl)',
        backgroundColor: 'var(--surface-strong)', color: 'var(--ink)',
        fontSize: '15px', lineHeight: 1.6,
        border: '1px solid var(--hairline)', alignSelf: 'flex-start',
    },
    bubbleUser: {
        maxWidth: '75%', padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl)',
        backgroundColor: 'var(--primary, var(--ink))', color: 'var(--on-primary, #fff)',
        fontSize: '15px', lineHeight: 1.6, alignSelf: 'flex-end',
    },
    bubbleSystem: {
        maxWidth: '90%', padding: 'var(--sp-xs) var(--sp-base)',
        borderRadius: 'var(--rounded-lg)', backgroundColor: 'transparent',
        color: 'var(--muted)', fontSize: '13px', fontStyle: 'italic',
    },
    typingBubble: { display: 'flex', alignItems: 'center', gap: '5px', padding: '12px 16px', minWidth: '60px' },
    dot: { display: 'inline-block', width: '7px', height: '7px', borderRadius: '50%', backgroundColor: 'var(--muted)' },
    // Bottom bar shared style
    bottomBar: {
        padding: 'var(--sp-base)',
        backgroundColor: 'var(--surface-card)', border: '1px solid var(--hairline)',
        borderTop: 'none', borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 'var(--sp-base)',
    },
    // Text input area
    inputArea: {
        display: 'flex', padding: 'var(--sp-sm)',
        backgroundColor: 'var(--surface-card)', border: '1px solid var(--hairline)',
        borderTop: 'none', borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        gap: 'var(--sp-xs)', alignItems: 'flex-end',
    },
    textarea: {
        flex: 1, resize: 'none', borderRadius: 'var(--rounded-lg)',
        minHeight: '40px', maxHeight: '200px',
        overflowY: 'auto', lineHeight: 1.5,
        padding: 'var(--sp-sm) var(--sp-base)',
        transition: 'height 0.1s ease',
    },
    iconBtn: {
        width: '40px', height: '40px', border: 'none',
        borderRadius: 'var(--rounded-full)', cursor: 'pointer', fontSize: '18px',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0, transition: 'all var(--transition-base)',
        backgroundColor: 'transparent',
    },
    // Voice recorder bar
    recorderBar: {
        display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)',
        padding: '10px var(--sp-sm)',
        backgroundColor: '#111', borderTop: 'none',
        border: '1px solid #333',
        borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
    },
    recorderTrack: {
        flex: 1, display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)',
        backgroundColor: '#1a1a1a', borderRadius: 'var(--rounded-pill)',
        padding: '6px 12px', minHeight: '44px',
    },
    recPlayBtn: {
        width: '32px', height: '32px', borderRadius: '50%',
        backgroundColor: '#ef4444', border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
        animation: 'pulse-ring 1.5s ease-out infinite',
    },
    recMiddle: {
        flex: 1, display: 'flex', alignItems: 'center',
        overflow: 'hidden', minHeight: '28px',
    },
    waveform: {
        display: 'flex', alignItems: 'center', gap: '2px', height: '28px',
    },
    waveBar: {
        width: '3px', borderRadius: '2px',
        backgroundColor: '#ef4444', opacity: 0.8,
        transition: 'height 0.1s ease',
    },
    recTimer: {
        color: '#ccc', fontSize: '13px', fontVariantNumeric: 'tabular-nums',
        flexShrink: 0, minWidth: '40px', textAlign: 'right',
    },
    endedBar: {
        padding: 'var(--sp-base) var(--sp-lg)',
        backgroundColor: 'var(--surface-card)', border: '1px solid var(--hairline)',
        borderTop: 'none', borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
    },
};

export default ChatPage;