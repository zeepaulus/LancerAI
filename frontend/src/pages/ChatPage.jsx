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

function formatTimer(seconds) {
    const m = String(Math.floor(seconds / 60)).padStart(2, '0');
    const s = String(seconds % 60).padStart(2, '0');
    return `${m}:${s}`;
}

// ─── CSS injection ────────────────────────────────────────────────────────────

const CHAT_CSS = `
@keyframes chat-wave {
    0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
    30%            { transform: translateY(-6px); opacity: 1; }
}
@keyframes chat-pulse-ring {
    0%   { box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }
    70%  { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
    100% { box-shadow: 0 0 0 0 rgba(239,68,68,0); }
}
@keyframes chat-fade-in {
    from { opacity: 0; transform: translateY(8px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes chat-waveform-bar {
    0%, 100% { height: 4px; }
    50%      { height: 18px; }
}
`;

function injectCss() {
    if (document.getElementById('lancerai-chatpage-css')) return;
    const s = document.createElement('style');
    s.id = 'lancerai-chatpage-css';
    s.textContent = CHAT_CSS;
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
    const [voiceMode, setVoiceMode]           = useState('idle'); // 'idle' | 'recording' | 'paused'
    const [voiceSupported, setVoiceSupported] = useState(false);
    const [recSeconds, setRecSeconds]         = useState(0);

    // ── Session timer ──────────────────────────────────────────────────────
    const [sessionSeconds, setSessionSeconds] = useState(0);

    // ── Refs ───────────────────────────────────────────────────────────────
    const pendingMessagesRef = useRef([]);
    const phaseRef           = useRef(PHASE.GREETING);
    const wsRef              = useRef(null);
    const chatEndRef         = useRef(null);
    const textareaRef        = useRef(null);
    const mediaRecorderRef   = useRef(null);
    const audioChunksRef     = useRef([]);
    const recTimerRef        = useRef(null);
    const streamRef          = useRef(null);
    const sessionTimerRef    = useRef(null);
    const audioCtxRef        = useRef(null);
    const nextPlayTimeRef    = useRef(0);

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

    // ── Audio player ───────────────────────────────────────────────────────

    const initAudioContext = () => {
        if (!audioCtxRef.current) {
            const AudioContextClass = window.AudioContext || window.webkitAudioContext;
            audioCtxRef.current = new AudioContextClass({ sampleRate: 24000 });
            nextPlayTimeRef.current = audioCtxRef.current.currentTime;
        }
        if (audioCtxRef.current.state === 'suspended') {
            audioCtxRef.current.resume();
        }
    };

    const playPcmChunk = async (arrayBuffer) => {
        try {
            initAudioContext();
            const audioCtx = audioCtxRef.current;
            
            const int16Array = new Int16Array(arrayBuffer);
            const float32Array = new Float32Array(int16Array.length);
            for (let i = 0; i < int16Array.length; i++) {
                float32Array[i] = int16Array[i] / 32768.0;
            }

            const buffer = audioCtx.createBuffer(1, float32Array.length, 24000);
            buffer.copyToChannel(float32Array, 0);

            const source = audioCtx.createBufferSource();
            source.buffer = buffer;
            source.connect(audioCtx.destination);

            const now = audioCtx.currentTime;
            let playTime = nextPlayTimeRef.current;
            if (playTime < now) {
                playTime = now;
            }
            source.start(playTime);
            nextPlayTimeRef.current = playTime + buffer.duration;
        } catch (err) {
            console.error('Lỗi phát âm thanh:', err);
        }
    };

    const stopAudio = () => {
        if (audioCtxRef.current) {
            audioCtxRef.current.close().catch(() => {});
            audioCtxRef.current = null;
        }
        nextPlayTimeRef.current = 0;
    };

    // ── Append message ─────────────────────────────────────────────────────

    const appendMessage = useCallback((role, text) => {
        setMessages(prev => [...prev, { id: Date.now() + Math.random(), role, text }]);
    }, []);

    // ── WebSocket ──────────────────────────────────────────────────────────

    const connectWebSocket = useCallback(() => {
        if (!sessionId || !cvId) return;
        const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
        const ws    = new WebSocket(buildWsUrl());
        ws.binaryType = 'arraybuffer';
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
            if (event.data instanceof ArrayBuffer) {
                playPcmChunk(event.data);
                return;
            }
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
                showOrBuffer('user', msg.text);

            } else if (ev === 'session_started') {
                // No action needed

            } else if (ev === 'time_up' || ev === 'session_ended') {
                setAiTyping(false);
                setPhase(PHASE.ENDED);
                stopSessionTimer();
                stopAudio();
                if (msg.evaluation?.final_feedback) {
                    appendMessage('ai', msg.evaluation.final_feedback);
                }

            } else if (ev === 'error') {
                setAiTyping(false);
                stopAudio();
                if (phaseRef.current === PHASE.INTERVIEW) {
                    appendMessage('system', `⚠️ ${msg.message || 'Lỗi từ server.'}`);
                }
            }
        };

        ws.onerror = () => { setAiTyping(false); stopAudio(); };

        ws.onclose = (evt) => {
            setAiTyping(false);
            stopAudio();
            if (phaseRef.current === PHASE.INTERVIEW && evt.code !== 1000 && evt.code !== 1001) {
                setWsError('Kết nối bị gián đoạn. Vui lòng tải lại trang.');
            }
        };
    }, [sessionId, cvId, extractionData, position, level, mode, appendMessage, industry]);

    // ── Session timer ──────────────────────────────────────────────────────

    const startSessionTimer = () => {
        setSessionSeconds(0);
        sessionTimerRef.current = setInterval(() => setSessionSeconds(s => s + 1), 1000);
    };

    const stopSessionTimer = () => {
        if (sessionTimerRef.current) {
            clearInterval(sessionTimerRef.current);
            sessionTimerRef.current = null;
        }
    };

    // ── Bấm "Tôi đã sẵn sàng" ─────────────────────────────────────────────

    const handleReady = () => {
        setPhase(PHASE.INTERVIEW);
        phaseRef.current = PHASE.INTERVIEW;
        connectWebSocket();
        startSessionTimer();
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
            stopRecTimer();
            stopSessionTimer();
            stopAudio();
            streamRef.current?.getTracks().forEach(t => t.stop());
        };
    }, []);

    // ── Gửi text ──────────────────────────────────────────────────────────

    const sendText = useCallback(() => {
        const text = inputText.trim();
        if (!text || aiTyping || phase !== PHASE.INTERVIEW) return;

        stopAudio();
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

    const stopRecTimer = () => {
        if (recTimerRef.current) { clearInterval(recTimerRef.current); recTimerRef.current = null; }
    };

    const startRecTimer = () => {
        setRecSeconds(0);
        recTimerRef.current = setInterval(() => setRecSeconds(s => s + 1), 1000);
    };

    const startVoice = async () => {
        stopAudio();
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
            // Audio blob is assembled in sendVoice
        };

        mr.start();
        setVoiceMode('recording');
        startRecTimer();
    };

    const pauseVoice = () => {
        mediaRecorderRef.current?.pause();
        stopRecTimer();
        setVoiceMode('paused');
    };

    const resumeVoice = () => {
        mediaRecorderRef.current?.resume();
        recTimerRef.current = setInterval(() => setRecSeconds(s => s + 1), 1000);
        setVoiceMode('recording');
    };

    const discardVoice = () => {
        mediaRecorderRef.current?.stop();
        stopRecTimer();
        streamRef.current?.getTracks().forEach(t => t.stop());
        audioChunksRef.current = [];
        setRecSeconds(0);
        setVoiceMode('idle');
    };

    const sendVoice = async () => {
        const wsReady = wsRef.current?.readyState === WebSocket.OPEN;

        // Stop recorder to finalize the recording
        if (mediaRecorderRef.current?.state !== 'inactive') {
            mediaRecorderRef.current?.stop();
        }

        // Wait a tick for onstop to fire, then send
        await new Promise(r => setTimeout(r, 100));

        if (wsReady && audioChunksRef.current.length > 0) {
            const blob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
            const arrayBuffer = await blob.arrayBuffer();
            wsRef.current.send(arrayBuffer);
            setAiTyping(true);
        } else if (!wsReady) {
            setWsError('Mất kết nối. Vui lòng tải lại trang.');
        }

        // Reset voice UI
        stopRecTimer();
        streamRef.current?.getTracks().forEach(t => t.stop());
        audioChunksRef.current = [];
        setRecSeconds(0);
        setVoiceMode('idle');
    };

    // ── Kết thúc / Lưu ────────────────────────────────────────────────────

    const handleEnd = () => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'stop' }));
        }
        setPhase(PHASE.ENDED);
        stopSessionTimer();
    };

    const handleSave = () => {
        navigate('/interview');
    };

    // ─── Render ───────────────────────────────────────────────────────────

    if (!sessionId) return null;

    const positionLabel = `${position}${level ? ' — ' + level : ''}`;
    const isVoiceUI = voiceMode !== 'idle';

    return (
        <div style={{ backgroundColor: 'var(--canvas)', minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
            <Navbar />
            <div style={styles.container}>

                {/* ── Top bar ── */}
                <div style={styles.topBar}>
                    <button className="btn-tertiary" onClick={handleSave} style={{ fontSize: '13px' }}>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="15 18 9 12 15 6" />
                        </svg>
                        Quay lại
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
                    <div style={styles.topBarRight}>
                        {phase === PHASE.INTERVIEW && (
                            <>
                                <span style={styles.timerBadge}>
                                    <span style={styles.timerDot} />
                                    {formatTimer(sessionSeconds)}
                                </span>
                                <button
                                    className="btn-outline"
                                    onClick={handleEnd}
                                    style={{ fontSize: '13px', color: 'var(--semantic-error,#ef4444)', borderColor: 'var(--semantic-error,#ef4444)' }}
                                >
                                    Kết thúc
                                </button>
                            </>
                        )}
                        {phase !== PHASE.INTERVIEW && <div style={{ width: '80px' }} />}
                    </div>
                </div>

                {/* ── Chat box ── */}
                <div style={styles.chatBox}>
                    {/* Lời chào tĩnh */}
                    <div style={{ ...styles.bubbleAI, animation: 'chat-fade-in 0.3s ease' }}>
                        <div style={styles.aiAvatar}>AI</div>
                        <div>
                            Xin chào <strong>{userName}</strong>, hãy bắt đầu với buổi phỏng vấn cho vị trí{' '}
                            <strong>{positionLabel}</strong> ngày <strong>{today()}</strong>.
                            {industry ? ` Ngành: ${industry}.` : ''}
                        </div>
                    </div>

                    {/* Messages */}
                    {messages.map(msg => {
                        const isUser = msg.role === 'user';
                        const isSystem = msg.role === 'system';
                        return (
                            <div
                                key={msg.id}
                                style={{
                                    display: 'flex',
                                    justifyContent: isUser ? 'flex-end' : 'flex-start',
                                    animation: 'chat-fade-in 0.3s ease',
                                }}
                            >
                                <div style={isUser ? styles.bubbleUser : isSystem ? styles.bubbleSystem : styles.bubbleAI}>
                                    {!isUser && !isSystem && <div style={styles.aiAvatar}>AI</div>}
                                    <div style={{ whiteSpace: 'pre-wrap' }}>{msg.text}</div>
                                </div>
                            </div>
                        );
                    })}

                    {/* Typing indicator */}
                    {aiTyping && (
                        <div style={{ display: 'flex', justifyContent: 'flex-start', animation: 'chat-fade-in 0.2s ease' }}>
                            <div style={{ ...styles.bubbleAI, ...styles.typingBubble }}>
                                <div style={styles.aiAvatar}>AI</div>
                                <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                                    {[0, 1, 2].map(i => (
                                        <span key={i} style={{ ...styles.dot, animation: 'chat-wave 1.2s ease-in-out infinite', animationDelay: `${i * 0.18}s` }} />
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* WS error */}
                    {wsError && (
                        <div style={{ textAlign: 'center', padding: 'var(--sp-sm)' }}>
                            <p style={{ color: 'var(--semantic-error,#ef4444)', fontSize: '13px', margin: 0 }}>{wsError}</p>
                            <button
                                className="btn-outline"
                                onClick={() => { setWsError(''); connectWebSocket(); }}
                                style={{ marginTop: 'var(--sp-xs)', fontSize: '12px' }}
                            >
                                Thử kết nối lại
                            </button>
                        </div>
                    )}
                    <div ref={chatEndRef} />
                </div>

                {/* ── Input area ── */}

                {phase === PHASE.GREETING && (
                    <div style={styles.bottomBar}>
                        <div style={styles.greetingContent}>
                            <p style={{ color: 'var(--muted)', fontSize: '14px', margin: '0 0 var(--sp-sm) 0', textAlign: 'center' }}>
                                Khi sẵn sàng, bấm nút bên dưới để bắt đầu phỏng vấn.
                            </p>
                            <button className="btn-primary" onClick={handleReady} style={{ minWidth: '220px', height: '48px', fontSize: '16px' }}>
                                Tôi đã sẵn sàng 🚀
                            </button>
                        </div>
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
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                                    <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                                    <line x1="12" y1="19" x2="12" y2="23" />
                                    <line x1="8" y1="23" x2="16" y2="23" />
                                </svg>
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
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="22" y1="2" x2="11" y2="13" />
                                <polygon points="22 2 15 22 11 13 2 9 22 2" />
                            </svg>
                            Gửi
                        </button>
                    </div>
                )}

                {phase === PHASE.INTERVIEW && isVoiceUI && (
                    /* ── Voice recorder UI ── */
                    <div style={styles.recorderBar}>
                        {/* Nút xoá */}
                        <button
                            onClick={discardVoice}
                            style={{ ...styles.iconBtn, color: 'var(--semantic-error,#ef4444)', fontSize: '20px' }}
                            title="Xoá đoạn ghi âm"
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                            </svg>
                        </button>

                        {/* Dải recorder */}
                        <div style={styles.recorderTrack}>
                            <button
                                onClick={voiceMode === 'recording' ? pauseVoice : resumeVoice}
                                style={styles.recPlayBtn}
                                title={voiceMode === 'recording' ? 'Tạm dừng' : 'Tiếp tục'}
                            >
                                {voiceMode === 'recording' ? (
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
                                        <rect x="6" y="4" width="4" height="16" rx="1" />
                                        <rect x="14" y="4" width="4" height="16" rx="1" />
                                    </svg>
                                ) : (
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="white">
                                        <polygon points="5,3 19,12 5,21" />
                                    </svg>
                                )}
                            </button>

                            {/* Waveform + status */}
                            <div style={styles.recMiddle}>
                                {voiceMode === 'recording' && (
                                    <div style={styles.waveform}>
                                        {Array.from({ length: 24 }).map((_, i) => (
                                            <div
                                                key={i}
                                                style={{
                                                    ...styles.waveBar,
                                                    animation: 'chat-waveform-bar 0.6s ease-in-out infinite',
                                                    animationDelay: `${i * 0.04}s`,
                                                }}
                                            />
                                        ))}
                                    </div>
                                )}
                                {voiceMode === 'paused' && (
                                    <span style={{ color: 'var(--muted)', fontSize: '13px' }}>Đã tạm dừng</span>
                                )}
                            </div>

                            <span style={styles.recTimer}>{formatTimer(recSeconds)}</span>
                        </div>

                        {/* Nút Gửi */}
                        <button
                            className="btn-primary"
                            onClick={sendVoice}
                            disabled={aiTyping}
                            style={{ flexShrink: 0, fontSize: '13px', gap: '6px' }}
                        >
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <line x1="22" y1="2" x2="11" y2="13" />
                                <polygon points="22 2 15 22 11 13 2 9 22 2" />
                            </svg>
                            Gửi
                        </button>
                    </div>
                )}

                {phase === PHASE.ENDED && (
                    <div style={styles.bottomBar}>
                        <div style={styles.endedContent}>
                            <div style={styles.endedIcon}>✓</div>
                            <div>
                                <p style={{ color: 'var(--ink)', fontSize: '15px', fontWeight: 600, margin: '0 0 2px 0' }}>
                                    Buổi phỏng vấn đã kết thúc
                                </p>
                                <p style={{ color: 'var(--muted)', fontSize: '13px', margin: 0 }}>
                                    Thời lượng: {formatTimer(sessionSeconds)} · {messages.filter(m => m.role === 'user').length} câu trả lời
                                </p>
                            </div>
                            <div style={{ marginLeft: 'auto', display: 'flex', gap: 'var(--sp-xs)' }}>
                                <button className="btn-outline" onClick={() => navigate('/interview')}>
                                    Quay lại
                                </button>
                                <button className="btn-primary" onClick={() => navigate('/interview-report', { state: { sessionId } })}>
                                    Xem kết quả →
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = {
    container: {
        maxWidth: '860px', margin: '0 auto',
        padding: 'var(--sp-base) var(--sp-lg)',
        flex: 1, display: 'flex', flexDirection: 'column',
        height: 'calc(100vh - var(--nav-height, 64px))',
    },
    topBar: {
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: 'var(--sp-sm)', gap: 'var(--sp-base)',
    },
    sessionInfo: {
        flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '2px',
    },
    sessionMeta: { fontSize: '12px', color: 'var(--muted)' },
    topBarRight: {
        display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)',
    },
    timerBadge: {
        display: 'inline-flex', alignItems: 'center', gap: '6px',
        backgroundColor: 'var(--surface-strong)', borderRadius: 'var(--rounded-pill)',
        padding: '4px 12px', fontSize: '13px', fontWeight: 600,
        color: 'var(--ink)', fontVariantNumeric: 'tabular-nums',
    },
    timerDot: {
        width: '6px', height: '6px', borderRadius: '50%',
        backgroundColor: 'var(--semantic-error, #ef4444)',
        animation: 'chat-pulse-ring 1.5s ease-out infinite',
    },
    // Chat area
    chatBox: {
        flex: 1, overflowY: 'auto', padding: 'var(--sp-lg)',
        backgroundColor: 'var(--surface-card)', border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-xl) var(--rounded-xl) 0 0',
        display: 'flex', flexDirection: 'column', gap: 'var(--sp-base)',
    },
    aiAvatar: {
        width: '28px', height: '28px', borderRadius: '50%',
        backgroundColor: 'var(--primary)', color: 'var(--on-primary)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '11px', fontWeight: 700, flexShrink: 0,
        letterSpacing: '0.5px',
    },
    bubbleAI: {
        maxWidth: '80%', padding: 'var(--sp-sm) var(--sp-base)',
        borderRadius: 'var(--rounded-xl)',
        backgroundColor: 'var(--surface-strong)', color: 'var(--ink)',
        fontSize: '15px', lineHeight: 1.6,
        border: '1px solid var(--hairline)', alignSelf: 'flex-start',
        display: 'flex', gap: 'var(--sp-sm)', alignItems: 'flex-start',
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
    typingBubble: { padding: '12px 16px', minWidth: '80px' },
    dot: { display: 'inline-block', width: '7px', height: '7px', borderRadius: '50%', backgroundColor: 'var(--muted)' },
    // Bottom bars
    bottomBar: {
        padding: 'var(--sp-base) var(--sp-lg)',
        backgroundColor: 'var(--surface-card)', border: '1px solid var(--hairline)',
        borderTop: 'none', borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
    },
    greetingContent: {
        display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 'var(--sp-xs)',
    },
    endedContent: {
        display: 'flex', alignItems: 'center', gap: 'var(--sp-base)',
    },
    endedIcon: {
        width: '36px', height: '36px', borderRadius: '50%',
        backgroundColor: 'var(--semantic-success, #22c55e)', color: '#fff',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '16px', fontWeight: 700, flexShrink: 0,
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
        borderRadius: 'var(--rounded-full)', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0, transition: 'all var(--transition-base)',
        backgroundColor: 'transparent',
    },
    // Voice recorder bar
    recorderBar: {
        display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)',
        padding: '10px var(--sp-sm)',
        backgroundColor: 'var(--canvas-deep)', borderTop: 'none',
        border: '1px solid var(--hairline)',
        borderRadius: '0 0 var(--rounded-xl) var(--rounded-xl)',
    },
    recorderTrack: {
        flex: 1, display: 'flex', alignItems: 'center', gap: 'var(--sp-sm)',
        backgroundColor: 'var(--surface-dark-elevated)', borderRadius: 'var(--rounded-pill)',
        padding: '6px 14px', minHeight: '44px',
    },
    recPlayBtn: {
        width: '32px', height: '32px', borderRadius: '50%',
        backgroundColor: 'var(--semantic-error, #ef4444)', border: 'none', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        flexShrink: 0,
        animation: 'chat-pulse-ring 1.5s ease-out infinite',
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
        backgroundColor: 'var(--semantic-error, #ef4444)', opacity: 0.8,
        minHeight: '4px',
    },
    recTimer: {
        color: 'var(--on-dark-soft)', fontSize: '13px', fontVariantNumeric: 'tabular-nums',
        flexShrink: 0, minWidth: '40px', textAlign: 'right',
    },
};

export default ChatPage;