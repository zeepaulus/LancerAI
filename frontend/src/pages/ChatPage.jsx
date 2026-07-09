import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import {
    ErrorState,
    StatusBadge,
} from '../components/Common/AppUI';
import { CameraPlaceholder } from '../components/Common/Visuals';
import { createSession, getReport } from '../api/interview';
import { INTERVIEW_WS_PATH } from '../api/paths';
import { API_BASE_URL } from '../config/env';
import * as keys from '../config/storageKeys';

const PHASE_META = {
    connecting: {
        label: 'Đang kết nối',
        title: 'Đang chuẩn bị phòng phỏng vấn',
        description: 'Đang mở kết nối và micro. Camera sẽ hiển thị nếu trình duyệt cho phép.',
        tone: 'ai',
    },
    listening: {
        label: 'Đang nghe',
        title: 'Bạn có thể trả lời',
        description: 'LancerAI đang nghe qua micro. Hãy dừng tự nhiên khi trả lời xong.',
        tone: 'success',
    },
    processing: {
        label: 'Đang phân tích',
        title: 'Đang ghi transcript',
        description: 'Hệ thống đang chuyển câu trả lời thành transcript và chuẩn bị câu hỏi tiếp theo.',
        tone: 'ai',
    },
    speaking: {
        label: 'AI đang hỏi',
        title: 'Hãy nghe câu hỏi',
        description: 'Chờ AI hỏi xong rồi hãy bắt đầu trả lời.',
        tone: 'warning',
    },
    ended: {
        label: 'Đã hoàn tất',
        title: 'Phiên phỏng vấn đã kết thúc',
        description: 'Mở báo cáo để xem transcript, điểm tin cậy và gợi ý cải thiện.',
        tone: 'success',
    },
};

function buildMeetingUrl(sessionId) {
    return `${window.location.origin}/chat?session_id=${encodeURIComponent(sessionId)}`;
}

function isLocalDevelopmentHost() {
    return ['localhost', '127.0.0.1', '[::1]', '::1'].includes(window.location.hostname);
}

function buildInterviewWsUrl() {
    const pageWsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';

    if (!API_BASE_URL) {
        return `${pageWsProtocol}//${window.location.host}${INTERVIEW_WS_PATH}`;
    }

    const base = new URL(API_BASE_URL, window.location.origin);
    const wsProtocol = base.protocol === 'https:' ? 'wss:' : 'ws:';
    const basePath = base.pathname.replace(/\/+$/, '');
    return `${wsProtocol}//${base.host}${basePath}${INTERVIEW_WS_PATH}`;
}

function getAudioContextConstructor() {
    return window.AudioContext || window.webkitAudioContext;
}

function closeSocketQuietly(ws) {
    if (!ws || ![WebSocket.CONNECTING, WebSocket.OPEN].includes(ws.readyState)) return;
    try {
        ws.close(1000, 'media_unavailable');
    } catch {
        // Best-effort close; the UI already shows the actionable media error.
    }
}

function mediaAccessMessage(error, deviceLabel) {
    const name = error?.name || '';
    if (!window.isSecureContext && !isLocalDevelopmentHost()) {
        return 'Camera và micro cần HTTPS. Hãy mở LancerAI bằng tên miền HTTPS an toàn trước khi bắt đầu phỏng vấn.';
    }
    if (!navigator.mediaDevices?.getUserMedia) {
        return 'Trình duyệt này không thể truy cập camera hoặc micro từ trang hiện tại. Hãy dùng Chrome, Edge hoặc Safari trên HTTPS.';
    }
    if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
        return `Quyền truy cập ${deviceLabel} đã bị chặn. Hãy cho phép trong thanh địa chỉ rồi tải lại phòng phỏng vấn.`;
    }
    if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
        return `Không tìm thấy thiết bị ${deviceLabel}. Hãy kết nối thiết bị hoặc kiểm tra quyền riêng tư của hệ điều hành.`;
    }
    if (name === 'NotReadableError' || name === 'TrackStartError') {
        return `${deviceLabel} đang được ứng dụng khác sử dụng hoặc bị hệ điều hành chặn. Hãy đóng ứng dụng họp khác rồi thử lại.`;
    }
    if (name === 'SecurityError') {
        return `Chính sách bảo mật trình duyệt đã chặn ${deviceLabel}. Hãy kiểm tra HTTPS và quyền camera, micro cho bản triển khai này.`;
    }
    if (name === 'OverconstrainedError') {
        return `${deviceLabel} đã chọn không hỗ trợ thiết lập yêu cầu. Hãy thử thiết bị khác.`;
    }
    return `Không thể truy cập ${deviceLabel}. Hãy kiểm tra quyền trình duyệt và thử lại.`;
}

function resampleTo16kInt16(inputBuffer, inputSampleRate) {
    const targetSampleRate = 16000;
    const ratio = inputSampleRate / targetSampleRate;
    const newLength = Math.round(inputBuffer.length / ratio);
    const result = new Int16Array(newLength);
    for (let index = 0; index < newLength; index += 1) {
        const sourceIndex = Math.min(inputBuffer.length - 1, Math.round(index * ratio));
        const value = Math.max(-1, Math.min(1, inputBuffer[sourceIndex]));
        result[index] = value < 0 ? value * 0x8000 : value * 0x7fff;
    }
    return result.buffer;
}

function messageTone(sender) {
    if (sender === 'user') return 'user';
    if (sender === 'ai') return 'ai';
    return 'neutral';
}

function messageTitle(sender) {
    if (sender === 'user') return 'Ứng viên';
    if (sender === 'ai') return 'AI phỏng vấn';
    return 'Hệ thống';
}

function micStatusMeta(status, phase) {
    if (status === 'unavailable') {
        return { label: 'Micro lỗi', tone: 'danger', description: 'Micro chưa sẵn sàng hoặc chưa được cấp quyền.' };
    }
    if (status === 'requesting') {
        return { label: 'Đang xin quyền micro', tone: 'warning', description: 'Trình duyệt đang chờ quyền truy cập micro.' };
    }
    if (status === 'off') {
        return { label: 'Micro đã tắt', tone: 'neutral', description: 'Micro đã dừng cho phiên hiện tại.' };
    }
    if (phase === 'listening' && status === 'recording') {
        return { label: 'Đang thu âm', tone: 'success', description: 'Micro đang gửi âm thanh đến phiên phỏng vấn.' };
    }
    if (phase === 'listening') {
        return { label: 'Micro sẵn sàng', tone: 'success', description: 'Bạn có thể trả lời. Micro sẽ gửi âm thanh khi phát hiện tiếng nói.' };
    }
    if (status === 'ready') {
        return { label: 'Micro tạm dừng', tone: 'warning', description: 'Micro đã sẵn sàng nhưng chưa gửi âm thanh khi AI đang hỏi hoặc hệ thống đang xử lý.' };
    }
    return { label: 'Đang mở micro', tone: 'neutral', description: 'Hệ thống đang chuẩn bị micro.' };
}

const ChatPage = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const [messages, setMessages] = useState([]);
    const [phase, setPhase] = useState('connecting');
    const [error, setError] = useState('');
    const [sessionInfo, setSessionInfo] = useState(null);
    const [cameraStatus, setCameraStatus] = useState('pending');
    const [, setBehaviorEvents] = useState([]);
    const [finalEvaluation, setFinalEvaluation] = useState(null);
    const [loadingReport, setLoadingReport] = useState(false);
    const [micStatus, setMicStatus] = useState('pending');
    const [micLevel, setMicLevel] = useState(0);

    const chatEndRef = useRef(null);
    const videoPreviewRef = useRef(null);
    const wsRef = useRef(null);
    const recordingRef = useRef(null);
    const audioContextPlayerRef = useRef(null);
    const nextStartTimeRef = useRef(0);
    const phaseRef = useRef('connecting');
    const behaviorLastSentRef = useRef({});
    const connectionSeqRef = useRef(0);
    const micLevelUpdateRef = useRef(0);
    const sessionInfoRef = useRef(null);
    const reportRedirectingRef = useRef(false);
    const cameraAnalysisRef = useRef(null); // interval ID for camera anomaly detection
    const prevPixelsRef = useRef(null); // previous frame pixels for motion detection

    useEffect(() => {
        phaseRef.current = phase;
    }, [phase]);

    useEffect(() => {
        sessionInfoRef.current = sessionInfo;
    }, [sessionInfo]);

    useEffect(() => {
        if (phase === 'ended') {
            setMicStatus((current) => (current === 'unavailable' ? current : 'off'));
            setMicLevel(0);
            return;
        }
        if (phase !== 'listening') {
            setMicStatus((current) => (current === 'recording' ? 'ready' : current));
        }
    }, [phase]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        let cancelled = false;

        async function loadSessionAndConnect() {
            const params = new URLSearchParams(location.search);
            let sessionId = location.state?.sessionId || params.get('session_id') || '';
            let cvId = location.state?.cvId || params.get('cv_id') || '';
            const mode = location.state?.mode || 'practice';
            const durationMinutes = Number(location.state?.durationMinutes || 5);

            try {
                if (!sessionId) {
                    if (!cvId) {
                        setError('Vui lòng tải CV trước khi bắt đầu phỏng vấn trực tiếp.');
                        setPhase('ended');
                        return;
                    }

                    const created = await createSession({
                        cv_id: cvId,
                        mode,
                        duration_minutes: durationMinutes,
                        job_title: location.state?.jobTitle || '',
                        jd_text: location.state?.jdText || '',
                        focus_area: location.state?.focusArea || '',
                    });
                    sessionId = created.session_id;
                    navigate(`/chat?session_id=${encodeURIComponent(sessionId)}`, {
                        replace: true,
                        state: {
                            sessionId,
                            cvId,
                            mode,
                            durationMinutes: created.duration_minutes || durationMinutes,
                            meetingUrl: created.meeting_url,
                            jobTitle: created.job_title,
                            interviewPlan: created.interview_plan,
                        },
                    });
                }

                if (cancelled) return;
                const resolvedSession = {
                    sessionId,
                    cvId,
                    mode,
                    durationMinutes,
                    meetingUrl: location.state?.meetingUrl || buildMeetingUrl(sessionId),
                    jobTitle: location.state?.jobTitle || '',
                    interviewPlan: location.state?.interviewPlan || {},
                };
                setSessionInfo(resolvedSession);
                connectWebSocket(resolvedSession);
            } catch (err) {
                setError(err.message || 'Chưa thể tạo phòng phỏng vấn trực tiếp. Vui lòng thử lại.');
                setPhase('ended');
            }
        }

        loadSessionAndConnect();

        return () => {
            cancelled = true;
            cleanupConnections();
        };
    }, []);

    useEffect(() => {
        let disposed = false;
        let awaySince = 0;
        let awayTimer = null;

        const report = (event, minIntervalMs = 8000) => {
            if (disposed || phaseRef.current === 'ended') return;
            sendBehaviorEvent(wsRef.current, event, minIntervalMs);
        };

        const clearAwayTimer = () => {
            if (awayTimer) window.clearTimeout(awayTimer);
            awayTimer = null;
        };

        const comeBack = () => {
            awaySince = 0;
            clearAwayTimer();
        };

        const goAway = (viaBlur = false) => {
            if (awaySince) return;
            awaySince = Date.now();
            const tick = () => {
                if (document.visibilityState === 'visible' && document.hasFocus()) {
                    comeBack();
                    return;
                }
                const awayMs = Date.now() - awaySince;
                report({
                    kind: 'tab_switch',
                    severity: 'high',
                    confidence: 0.85,
                    detail: `Ứng viên rời cửa sổ phỏng vấn trong ${(awayMs / 1000).toFixed(1)} giây.`,
                }, 10000);
                awayTimer = window.setTimeout(tick, 10000);
            };
            awayTimer = window.setTimeout(tick, viaBlur ? 1200 : 600);
        };

        const onVisibility = () => {
            if (document.visibilityState === 'hidden') goAway(false);
            else comeBack();
        };

        const onBlur = () => goAway(true);

        document.addEventListener('visibilitychange', onVisibility);
        window.addEventListener('blur', onBlur);
        window.addEventListener('focus', comeBack);

        if (window.screen?.isExtended === true) {
            report({
                kind: 'secondary_monitor',
                severity: 'high',
                confidence: 0.8,
                detail: 'Phát hiện màn hình mở rộng trong phiên phỏng vấn.',
            }, 15000);
        }

        return () => {
            disposed = true;
            clearAwayTimer();
            document.removeEventListener('visibilitychange', onVisibility);
            window.removeEventListener('blur', onBlur);
            window.removeEventListener('focus', comeBack);
        };
    }, []);

    // ── Camera anomaly detection ──────────────────────────────────────────────
    // Uses the browser-native FaceDetector API (Chrome/Edge) with a canvas
    // brightness fallback for browsers that don't support it.
    // Runs every 4 seconds while camera is active.
    const startCameraAnalysis = (ws) => {
        if (cameraAnalysisRef.current) return; // already running

        const analysisCanvas = document.createElement('canvas');
        analysisCanvas.width = 160;
        analysisCanvas.height = 90;
        const ctx2d = analysisCanvas.getContext('2d');

        const hasFaceDetector = typeof window.FaceDetector !== 'undefined';
        let faceDetector = null;
        if (hasFaceDetector) {
            try {
                faceDetector = new window.FaceDetector({ fastMode: true, maxDetectedFaces: 5 });
            } catch {
                faceDetector = null;
            }
        }

        const analyseFrame = async () => {
            const video = videoPreviewRef.current;
            if (!video || video.readyState < 2 || phaseRef.current === 'ended') return;

            // Draw downscaled frame to canvas for analysis
            try {
                ctx2d.drawImage(video, 0, 0, 160, 90);
            } catch {
                return;
            }

            // ── Brightness check (works in all browsers) ─────────────────────
            const imageData = ctx2d.getImageData(0, 0, 160, 90);
            const pixels = imageData.data;
            let brightnessSum = 0;
            for (let i = 0; i < pixels.length; i += 4) {
                // Luminance approximation: 0.299R + 0.587G + 0.114B
                brightnessSum += pixels[i] * 0.299 + pixels[i + 1] * 0.587 + pixels[i + 2] * 0.114;
            }
            const avgBrightness = brightnessSum / (160 * 90);
            if (avgBrightness < 40) {
                sendBehaviorEvent(ws, {
                    kind: 'poor_lighting',
                    severity: 'medium',
                    confidence: 0.85,
                    detail: `Ánh sáng yếu (độ sáng trung bình ${Math.round(avgBrightness)}/255). Hãy tăng ánh sáng trước mặt.`,
                }, 20000);
            }

            // ── Motion check (works in all browsers via frame difference) ─────
            if (prevPixelsRef.current) {
                let diff = 0;
                for (let i = 0; i < pixels.length; i += 4) {
                    diff += Math.abs(pixels[i] - prevPixelsRef.current[i]) +
                            Math.abs(pixels[i + 1] - prevPixelsRef.current[i + 1]) +
                            Math.abs(pixels[i + 2] - prevPixelsRef.current[i + 2]);
                }
                const avgDiff = diff / (160 * 90 * 3);
                if (avgDiff > 18) {
                    sendBehaviorEvent(ws, {
                        kind: 'restless_motion',
                        severity: 'low',
                        confidence: 0.8,
                        detail: `Ứng viên loay hoay, cử động nhiều (chênh lệch chuyển động ${Math.round(avgDiff)}).`,
                    }, 15000);
                }
            }
            prevPixelsRef.current = new Uint8ClampedArray(pixels);

            // ── Face detection (Chrome/Edge with FaceDetector API) ───────────
            if (!faceDetector) {
                console.warn('[LancerAI Camera] Browser does not support native FaceDetector. Gaze/Face checks skipped. Enable experimental web platform features in chrome://flags to support it.');
                return;
            }
            let faces = [];
            try {
                faces = await faceDetector.detect(video);
            } catch {
                return;
            }

            if (faces.length === 0) {
                sendBehaviorEvent(ws, {
                    kind: 'face_not_visible',
                    severity: 'medium',
                    confidence: 0.9,
                    detail: 'Không phát hiện khuôn mặt trong khung hình. Hãy ngồi lại đúng vị trí camera.',
                }, 12000);
                return;
            }

            if (faces.length > 1) {
                sendBehaviorEvent(ws, {
                    kind: 'multiple_faces',
                    severity: 'high',
                    confidence: 0.95,
                    detail: `Phát hiện ${faces.length} khuôn mặt. Đảm bảo chỉ có ứng viên trong khung hình.`,
                }, 10000);
            }

            // ── Face off-center check ────────────────────────────────────────
            const face = faces[0];
            const box = face.boundingBox;
            const faceCenterX = box.x + box.width / 2;
            const faceCenterY = box.y + box.height / 2;
            const vw = video.videoWidth || 640;
            const vh = video.videoHeight || 480;
            const offsetX = Math.abs(faceCenterX / vw - 0.5);
            const offsetY = Math.abs(faceCenterY / vh - 0.5);
            if (offsetX > 0.30 || offsetY > 0.30) {
                sendBehaviorEvent(ws, {
                    kind: 'face_off_center',
                    severity: 'low',
                    confidence: 0.8,
                    detail: 'Khuôn mặt lệch khỏi trung tâm camera. Hãy ngồi thẳng đối diện camera.',
                }, 15000);
            }
        };

        cameraAnalysisRef.current = window.setInterval(analyseFrame, 4000);
    };

    const stopCameraAnalysis = () => {
        if (cameraAnalysisRef.current) {
            window.clearInterval(cameraAnalysisRef.current);
            cameraAnalysisRef.current = null;
        }
    };

    const appendMessage = (sender, text) => {
        if (!text) return;
        setMessages((prev) => [
            ...prev,
            { id: `${sender}-${Date.now()}-${prev.length}`, sender, text },
        ]);
    };

    const connectWebSocket = (session) => {
        const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
        const wsUrl = buildInterviewWsUrl();
        const connectionId = connectionSeqRef.current + 1;
        connectionSeqRef.current = connectionId;

        if (!token) {
            setError('Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại để vào phòng phỏng vấn.');
            setPhase('ended');
            return;
        }

        if (window.location.protocol === 'https:' && wsUrl.startsWith('ws:')) {
            setError('Trang đang chạy HTTPS nhưng kết nối phỏng vấn chưa an toàn. Hãy cấu hình API bằng HTTPS hoặc proxy WebSocket cùng tên miền.');
            setPhase('ended');
            return;
        }

        let ws;
        try {
            ws = new WebSocket(wsUrl);
        } catch {
            setError('Không mở được kết nối phỏng vấn trực tiếp. Hãy kiểm tra URL API và cấu hình WebSocket bảo mật.');
            setPhase('ended');
            return;
        }
        ws.binaryType = 'arraybuffer';
        wsRef.current = ws;
        const isActiveSocket = () => connectionSeqRef.current === connectionId && wsRef.current === ws;

        ws.onopen = () => {
            if (!isActiveSocket()) return;
            setError('');
            ws.send(JSON.stringify({
                token,
                session_id: session.sessionId,
                duration_minutes: session.durationMinutes || 5,
            }));
            startRecording(ws);
        };

        ws.onmessage = (event) => {
            if (!isActiveSocket()) return;
            if (event.data instanceof ArrayBuffer) {
                playAudioChunk(event.data);
                return;
            }

            try {
                handleSocketEvent(JSON.parse(event.data));
            } catch {
                setError('Máy chủ phỏng vấn trả về dữ liệu không đọc được.');
            }
        };

        ws.onerror = () => {
            if (!isActiveSocket()) return;
            setError('Không kết nối được phòng phỏng vấn. Hãy kiểm tra backend có hỗ trợ WebSocket bảo mật.');
        };

        ws.onclose = (event) => {
            if (!isActiveSocket()) return;
            if (event.code === 1008) {
                setError('Phiên phỏng vấn không hợp lệ hoặc phiên đăng nhập đã hết hạn.');
            } else if (event.code === 1011) {
                setError('Chưa thể chuẩn bị phòng phỏng vấn. Vui lòng thử lại sau ít phút.');
            } else if (![1000, 1001].includes(event.code) && phaseRef.current !== 'ended') {
                setError('Kết nối phỏng vấn bị ngắt. Hãy kiểm tra mạng và cấu hình WebSocket bảo mật.');
            }
            setPhase((current) => (current === 'ended' ? current : 'ended'));
            stopRecording();
        };
    };

    const handleSocketEvent = (payload) => {
        if (payload.event === 'session_started') {
            setSessionInfo((prev) => ({
                ...(prev || {}),
                sessionId: payload.session_id || prev?.sessionId,
                jobTitle: payload.job_title || prev?.jobTitle,
                durationMinutes: payload.duration_minutes || prev?.durationMinutes,
                interviewPlan: payload.interview_plan || prev?.interviewPlan || {},
            }));
            appendMessage('system', 'Phòng phỏng vấn đã sẵn sàng. AI sẽ bắt đầu bằng câu hỏi đầu tiên.');
            return;
        }

        if (payload.event === 'phase_change') {
            const nextPhase = payload.phase;
            if (nextPhase === 'listening') {
                const audioCtx = audioContextPlayerRef.current;
                if (audioCtx && nextStartTimeRef.current > audioCtx.currentTime) {
                    const delayMs = (nextStartTimeRef.current - audioCtx.currentTime) * 1000;
                    window.setTimeout(() => {
                        setPhase((current) => (current === 'speaking' ? 'listening' : current));
                    }, delayMs + 100);
                    return;
                }
            }
            setPhase(nextPhase);
            return;
        }

        if (payload.event === 'transcript') {
            appendMessage('user', payload.text);
            return;
        }

        if (payload.event === 'assistant_text') {
            appendMessage('ai', payload.text);
            return;
        }

        if (payload.event === 'session_ended') {
            const evaluation = payload.evaluation || null;
            const sessionId = evaluation?.session_id || payload.session_id || sessionInfoRef.current?.sessionId;
            setPhase('ended');
            setFinalEvaluation(evaluation);
            setLoadingReport(true);
            cleanupConnections();
            if (sessionId && !reportRedirectingRef.current) {
                reportRedirectingRef.current = true;
                navigate('/interview-report', {
                    replace: true,
                    state: { sessionId, pendingReport: true },
                });
            }
            return;
        }

        if (payload.event === 'behavior_event_ack') {
            setBehaviorEvents((prev) =>
                prev.map((item, index) =>
                    index === 0 && item.kind === payload.kind ? { ...item, acknowledged: true } : item
                )
            );
            return;
        }

        if (payload.event === 'error') {
            setError(payload.message || 'Phiên phỏng vấn gặp lỗi.');
        }
    };

    const playAudioChunk = (arrayBuffer) => {
        if (!audioContextPlayerRef.current) {
            const AudioContextClass = getAudioContextConstructor();
            if (!AudioContextClass) {
                setError('Trình duyệt này không hỗ trợ phát âm thanh thời gian thực. Hãy dùng Chrome, Edge hoặc Safari bản mới.');
                return;
            }
            audioContextPlayerRef.current = new AudioContextClass();
            nextStartTimeRef.current = audioContextPlayerRef.current.currentTime;
        }

        const audioCtx = audioContextPlayerRef.current;
        if (audioCtx.state === 'suspended') audioCtx.resume();

        const int16 = new Int16Array(arrayBuffer);
        const float32 = new Float32Array(int16.length);
        for (let index = 0; index < int16.length; index += 1) {
            float32[index] = int16[index] / 32768.0;
        }

        const audioBuffer = audioCtx.createBuffer(1, float32.length, 24000);
        audioBuffer.getChannelData(0).set(float32);

        const source = audioCtx.createBufferSource();
        source.buffer = audioBuffer;
        source.connect(audioCtx.destination);

        const currentTime = audioCtx.currentTime;
        if (nextStartTimeRef.current < currentTime) nextStartTimeRef.current = currentTime;
        source.start(nextStartTimeRef.current);
        nextStartTimeRef.current += audioBuffer.duration;
    };

    const startRecording = async (ws) => {
        setMicStatus('requesting');
        setMicLevel(0);
        if (!window.isSecureContext && !isLocalDevelopmentHost()) {
            setError(mediaAccessMessage(null, 'camera và micro'));
            setMicStatus('unavailable');
            closeSocketQuietly(ws);
            setPhase('ended');
            return;
        }
        if (!navigator.mediaDevices?.getUserMedia) {
            setError(mediaAccessMessage(null, 'camera và micro'));
            setMicStatus('unavailable');
            closeSocketQuietly(ws);
            setPhase('ended');
            return;
        }

        const AudioContextClass = getAudioContextConstructor();
        if (!AudioContextClass) {
            setError('Trình duyệt này không hỗ trợ xử lý âm thanh thời gian thực. Hãy dùng Chrome, Edge hoặc Safari bản mới.');
            setMicStatus('unavailable');
            closeSocketQuietly(ws);
            setPhase('ended');
            return;
        }

        let stream;
        let videoStream = null;
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            setMicStatus('ready');
        } catch (err) {
            setError(mediaAccessMessage(err, 'micro'));
            setMicStatus('unavailable');
            closeSocketQuietly(ws);
            setPhase('ended');
            return;
        }

        try {
            try {
                videoStream = await navigator.mediaDevices.getUserMedia({
                    video: { width: { ideal: 960 }, height: { ideal: 540 }, frameRate: { ideal: 15 } },
                    audio: false,
                });
                setCameraStatus('active');
                if (videoPreviewRef.current) {
                    videoPreviewRef.current.srcObject = videoStream;
                    videoPreviewRef.current.muted = true;
                    videoPreviewRef.current.playsInline = true;
                    await videoPreviewRef.current.play().catch(() => {});
                }
                sendBehaviorEvent(ws, {
                    kind: 'camera_ready',
                    severity: 'low',
                    confidence: 0.9,
                    detail: 'Camera đang bật để ghi nhận điều kiện phỏng vấn.',
                }, 0);
                // Start real-time camera anomaly analysis
                startCameraAnalysis(ws);
            } catch (err) {
                setCameraStatus('unavailable');
                appendMessage('system', `${mediaAccessMessage(err, 'camera')} Phiên vẫn tiếp tục bằng micro.`);
                sendBehaviorEvent(ws, {
                    kind: 'camera_unavailable',
                    severity: 'info',
                    confidence: 1,
                    detail: 'Camera chưa được cấp quyền hoặc không khả dụng; phiên vẫn tiếp tục bằng micro.',
                }, 0);
            }

            const audioCtx = new AudioContextClass();
            if (audioCtx.state === 'suspended') await audioCtx.resume().catch(() => {});
            const source = audioCtx.createMediaStreamSource(stream);
            const processor = audioCtx.createScriptProcessor(4096, 1, 1);
            const mute = audioCtx.createGain();
            mute.gain.value = 0;
            source.connect(processor);
            processor.connect(mute);
            mute.connect(audioCtx.destination);

            processor.onaudioprocess = (event) => {
                const inputData = event.inputBuffer.getChannelData(0);
                const now = performance.now();
                if (now - micLevelUpdateRef.current > 140) {
                    let sum = 0;
                    for (let index = 0; index < inputData.length; index += 1) {
                        sum += inputData[index] * inputData[index];
                    }
                    const rms = Math.sqrt(sum / inputData.length);
                    setMicLevel(Math.min(1, rms * 14));
                    setMicStatus(phaseRef.current === 'listening' ? 'recording' : 'ready');
                    micLevelUpdateRef.current = now;
                }
                if (phaseRef.current !== 'listening') return;
                const int16Buffer = resampleTo16kInt16(inputData, audioCtx.sampleRate);
                if (ws.readyState === WebSocket.OPEN) ws.send(int16Buffer);
            };

            recordingRef.current = { stream, videoStream, audioCtx, source, processor, mute };
        } catch (err) {
            stream?.getTracks().forEach((track) => track.stop());
            videoStream?.getTracks?.().forEach((track) => track.stop());
            setError(mediaAccessMessage(err, 'micro'));
            setMicStatus('unavailable');
            closeSocketQuietly(ws);
            setPhase('ended');
        }
    };

    const sendBehaviorEvent = (ws, event, minIntervalMs = 6000) => {
        if (!ws || ws.readyState !== WebSocket.OPEN || !event?.kind) return;
        const now = Date.now();
        const lastSent = behaviorLastSentRef.current[event.kind] || 0;
        if (now - lastSent < minIntervalMs) return;
        behaviorLastSentRef.current[event.kind] = now;

        const payload = { ...event, ts: now / 1000 };
        ws.send(JSON.stringify({ action: 'behavior_event', event: payload }));
        setBehaviorEvents((prev) => [payload, ...prev].slice(0, 6));
    };

    const stopRecording = () => {
        stopCameraAnalysis();
        if (!recordingRef.current) return;
        try {
            const { stream, videoStream, audioCtx, source, processor, mute } = recordingRef.current;
            stream.getTracks().forEach((track) => track.stop());
            videoStream?.getTracks?.().forEach((track) => track.stop());
            source?.disconnect?.();
            processor.disconnect();
            mute?.disconnect?.();
            audioCtx.close();
            if (videoPreviewRef.current) videoPreviewRef.current.srcObject = null;
        } catch {
            // Best-effort cleanup.
        }
        recordingRef.current = null;
        setMicLevel(0);
        setMicStatus((current) => (current === 'unavailable' ? current : 'off'));
    };

    const cleanupConnections = () => {
        stopRecording();
        if (wsRef.current) {
            const ws = wsRef.current;
            connectionSeqRef.current += 1;
            ws.onopen = null;
            ws.onmessage = null;
            ws.onerror = null;
            ws.onclose = null;
            ws.close();
            if (wsRef.current === ws) wsRef.current = null;
        }
        if (audioContextPlayerRef.current) {
            audioContextPlayerRef.current.close();
            audioContextPlayerRef.current = null;
        }
    };

    const handleStopInterview = () => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ action: 'stop' }));
        }
    };

    const handleViewReport = async () => {
        const sessionId = finalEvaluation?.session_id || sessionInfo?.sessionId;
        if (!sessionId) return;
        setLoadingReport(true);
        try {
            await new Promise((resolve) => window.setTimeout(resolve, 500));
            const report = await getReport(sessionId);
            navigate('/interview-report', { state: { report } });
        } catch (err) {
            setError(err.message || 'Báo cáo chưa sẵn sàng. Vui lòng thử lại sau vài giây.');
        } finally {
            setLoadingReport(false);
        }
    };

    const phaseMeta = PHASE_META[phase] || PHASE_META.connecting;
    const micMeta = micStatusMeta(micStatus, phase);
    const micLevelWidth = `${Math.round(micLevel * 100)}%`;
    const currentQuestion = [...messages].reverse().find((message) => message.sender === 'ai')?.text;
    const transcriptCount = messages.filter((message) => message.sender === 'user').length;

    return (
        <div className="app-screen">
            <Navbar />
            <main className="interview-room-page" aria-label="Phòng phỏng vấn giọng nói">
                {error && (
                    <div className="interview-room-alert">
                        <ErrorState title="Cần kiểm tra phòng phỏng vấn" description={error} />
                    </div>
                )}

                <section className="interview-room-shell">
                    <div className="interview-room-header">
                        <div>
                            <p className="page-kicker">Phỏng vấn giọng nói</p>
                            <h1>{sessionInfo?.jobTitle || 'Phòng phỏng vấn AI'}</h1>
                        </div>
                        <div className="interview-room-actions">
                            <StatusBadge tone={phaseMeta.tone}>{phaseMeta.label}</StatusBadge>
                            <div className="interview-mic-status" title={micMeta.description} aria-label={micMeta.description}>
                                <StatusBadge tone={micMeta.tone}>{micMeta.label}</StatusBadge>
                                <span className="interview-mic-meter" aria-hidden="true">
                                    <span style={{ width: micLevelWidth }} />
                                </span>
                            </div>
                            {phase !== 'ended' ? (
                                <button className="btn-danger" type="button" onClick={handleStopInterview}>Kết thúc</button>
                            ) : (
                                <button className="btn-primary" type="button" onClick={handleViewReport} disabled={loadingReport}>
                                    {loadingReport ? 'Đang tải...' : 'Mở báo cáo'}
                                </button>
                            )}
                        </div>
                    </div>

                    <div className="interview-room-grid">
                        <section className="interview-camera-panel" aria-label="Camera ứng viên">
                            <video ref={videoPreviewRef} />
                            {cameraStatus !== 'active' && (
                                <CameraPlaceholder
                                    label={cameraStatus === 'unavailable' ? 'Không dùng camera' : 'Đang mở camera'}
                                    name="Ứng viên"
                                    hint={cameraStatus === 'unavailable' ? 'Phiên vẫn tiếp tục bằng micro và transcript.' : undefined}
                                />
                            )}
                            <div className="interview-camera-overlay">
                                <StatusBadge tone={cameraStatus === 'active' ? 'success' : 'warning'}>
                                    {cameraStatus === 'active' ? 'Camera đang bật' : cameraStatus === 'unavailable' ? 'Không dùng camera' : 'Đang chờ camera'}
                                </StatusBadge>
                                <span>{phaseMeta.title}</span>
                            </div>
                        </section>

                        <section className="interview-log-panel" aria-label="Transcript phỏng vấn">
                            <div className="interview-log-head">
                                <div>
                                    <p className="page-kicker">Transcript trực tiếp</p>
                                    <h2>Câu hỏi và câu trả lời</h2>
                                </div>
                                <StatusBadge tone="ai">{transcriptCount} câu trả lời</StatusBadge>
                            </div>

                            {currentQuestion && (
                                <div className="interview-current-question">
                                    <span>Câu hỏi hiện tại</span>
                                    <p>{currentQuestion}</p>
                                </div>
                            )}

                            <div className="interview-log-list" aria-live="polite">
                                {messages.length === 0 ? (
                                    <div className="interview-log-empty">
                                        Câu hỏi đầu tiên của AI và transcript câu trả lời sẽ xuất hiện tại đây.
                                    </div>
                                ) : messages.map((message) => (
                                    <article
                                        key={message.id}
                                        className={`interview-log-item interview-log-item--${messageTone(message.sender)}`}
                                    >
                                        <div className="interview-log-meta">
                                            <strong>{messageTitle(message.sender)}</strong>
                                            <span>{message.sender === 'user' ? 'Câu trả lời' : message.sender === 'ai' ? 'Câu hỏi' : 'Trạng thái'}</span>
                                        </div>
                                        <p>{message.text}</p>
                                    </article>
                                ))}
                                <div ref={chatEndRef} />
                            </div>
                        </section>
                    </div>
                </section>
            </main>
        </div>
    );
};

export default ChatPage;
