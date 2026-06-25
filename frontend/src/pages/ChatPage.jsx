import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Navbar from '../components/Layout/Navbar';
import { createSession, getReport } from '../api/interview';
import { API_BASE_URL } from '../config/env';
import * as keys from '../config/storageKeys';

const ChatPage = () => {
    const navigate = useNavigate();
    const location = useLocation();

    const [messages, setMessages] = useState([]);
    const [phase, setPhase] = useState('connecting');
    const [error, setError] = useState('');
    const [sessionInfo, setSessionInfo] = useState(null);
    const [cameraStatus, setCameraStatus] = useState('pending');
    const [behaviorEvents, setBehaviorEvents] = useState([]);
    const [typedAnswer, setTypedAnswer] = useState('');
    const [finalEvaluation, setFinalEvaluation] = useState(null);
    const [loadingReport, setLoadingReport] = useState(false);

    const chatEndRef = useRef(null);
    const videoPreviewRef = useRef(null);
    const wsRef = useRef(null);
    const recordingRef = useRef(null);
    const audioContextPlayerRef = useRef(null);
    const nextStartTimeRef = useRef(0);
    const phaseRef = useRef('connecting');
    const behaviorLastSentRef = useRef({});
    const connectionSeqRef = useRef(0);

    useEffect(() => {
        phaseRef.current = phase;
    }, [phase]);

    useEffect(() => {
        chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    useEffect(() => {
        let cancelled = false;

        const loadSessionAndConnect = async () => {
            const params = new URLSearchParams(location.search);
            let sessionId = location.state?.sessionId || params.get('session_id') || '';
            let cvId = location.state?.cvId || params.get('cv_id') || '';
            const mode = location.state?.mode || 'practice';
            const durationMinutes = Number(location.state?.durationMinutes || 5);

            try {
                if (!sessionId) {
                    cvId = cvId || getLatestCvId();
                    if (!cvId) {
                        setError('Vui lòng upload hoặc tối ưu CV trước khi phỏng vấn.');
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
                setError(err.message || 'Không thể khởi tạo phòng phỏng vấn.');
                setPhase('ended');
            }
        };

        loadSessionAndConnect();

        return () => {
            cancelled = true;
            cleanupConnections();
        };
    }, []);

    const buildMeetingUrl = (sessionId) =>
        `${window.location.origin}/chat?session_id=${encodeURIComponent(sessionId)}`;

    const getLatestCvId = () => {
        const storedCvHistory = localStorage.getItem('lancerai_cv_history');
        if (!storedCvHistory) return '';
        try {
            const cvs = JSON.parse(storedCvHistory);
            return cvs.length > 0 ? cvs[0].cvId : '';
        } catch {
            return '';
        }
    };

    const connectWebSocket = (session) => {
        const token = localStorage.getItem(keys.LANCERAI_ACCESS_TOKEN);
        const wsUrl = `${API_BASE_URL.replace(/^http/, 'ws')}/api/v1/interview/ws`;
        const connectionId = connectionSeqRef.current + 1;
        connectionSeqRef.current = connectionId;
        if (!token) {
            setError('Vui lòng đăng nhập lại để tham gia phòng phỏng vấn.');
            setPhase('ended');
            return;
        }

        const ws = new WebSocket(wsUrl);
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
                const payload = JSON.parse(event.data);
                handleSocketEvent(payload);
            } catch (err) {
                console.error('Failed to parse WS JSON message:', err);
            }
        };

        ws.onerror = (event) => {
            if (!isActiveSocket()) return;
            console.error('Interview WebSocket error:', event, wsUrl);
            setError('Không kết nối được WebSocket tới server.');
        };

        ws.onclose = (event) => {
            if (!isActiveSocket()) return;
            if (event.code === 1008) {
                setError('Phiên phỏng vấn không hợp lệ hoặc phiên đăng nhập đã hết hạn.');
            } else if (event.code === 1011) {
                setError('Server gặp lỗi khi khởi tạo pipeline phỏng vấn. Kiểm tra log backend để xem chi tiết.');
            } else if (![1000, 1001].includes(event.code) && phaseRef.current !== 'ended') {
                setError(`WebSocket đã đóng bất thường (code ${event.code || 'unknown'}).`);
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
            setMessages((prev) => [
                ...prev,
                {
                    id: `system-${Date.now()}`,
                    sender: 'system',
                    text: 'Phòng phỏng vấn đã sẵn sàng. AI sẽ bắt đầu bằng câu chào và câu hỏi đầu tiên.',
                },
            ]);
            return;
        }

        if (payload.event === 'phase_change') {
            setPhase(payload.phase);
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
            setPhase('ended');
            setFinalEvaluation(payload.evaluation || null);
            saveSessionToHistory(payload.evaluation);
            return;
        }

        if (payload.event === 'behavior_event_ack') {
            setBehaviorEvents((prev) =>
                prev.map((item, idx) =>
                    idx === 0 && item.kind === payload.kind ? { ...item, acknowledged: true } : item
                )
            );
            return;
        }

        if (payload.event === 'error') {
            setError(payload.message || 'Lỗi phiên phỏng vấn.');
        }
    };

    const appendMessage = (sender, text) => {
        if (!text) return;
        setMessages((prev) => [
            ...prev,
            { id: `${sender}-${Date.now()}-${prev.length}`, sender, text },
        ]);
    };

    const resampleAndConvertTo16kInt16 = (inputBuffer, inputSampleRate) => {
        const targetSampleRate = 16000;
        const ratio = inputSampleRate / targetSampleRate;
        const newLength = Math.round(inputBuffer.length / ratio);
        const result = new Int16Array(newLength);
        for (let i = 0; i < newLength; i += 1) {
            const index = Math.min(inputBuffer.length - 1, Math.round(i * ratio));
            const val = Math.max(-1, Math.min(1, inputBuffer[index]));
            result[i] = val < 0 ? val * 0x8000 : val * 0x7fff;
        }
        return result.buffer;
    };

    const playAudioChunk = (arrayBuffer) => {
        if (!audioContextPlayerRef.current) {
            audioContextPlayerRef.current = new (window.AudioContext || window.webkitAudioContext)();
            nextStartTimeRef.current = audioContextPlayerRef.current.currentTime;
        }

        const audioCtx = audioContextPlayerRef.current;
        if (audioCtx.state === 'suspended') audioCtx.resume();

        const int16 = new Int16Array(arrayBuffer);
        const float32 = new Float32Array(int16.length);
        for (let i = 0; i < int16.length; i += 1) {
            float32[i] = int16[i] / 32768.0;
        }

        const audioBuffer = audioCtx.createBuffer(1, float32.length, 16000);
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
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            let videoStream = null;
            let behaviorCleanup = () => {};

            try {
                videoStream = await navigator.mediaDevices.getUserMedia({
                    video: {
                        width: { ideal: 960 },
                        height: { ideal: 540 },
                        frameRate: { ideal: 15 },
                    },
                    audio: false,
                });
                behaviorCleanup = await startBehaviorMonitoring(videoStream, ws);
            } catch (cameraErr) {
                console.warn('Camera setup failed:', cameraErr);
                setCameraStatus('unavailable');
                sendBehaviorEvent(ws, {
                    kind: 'camera_unavailable',
                    severity: 'medium',
                    confidence: 1,
                    detail: 'Candidate did not grant camera access or no camera was available.',
                }, 0);
            }

            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const source = audioCtx.createMediaStreamSource(stream);
            const processor = audioCtx.createScriptProcessor(4096, 1, 1);
            source.connect(processor);
            processor.connect(audioCtx.destination);

            processor.onaudioprocess = (e) => {
                if (phaseRef.current !== 'listening') return;
                const inputData = e.inputBuffer.getChannelData(0);
                const int16Buffer = resampleAndConvertTo16kInt16(inputData, audioCtx.sampleRate);
                if (ws.readyState === WebSocket.OPEN) ws.send(int16Buffer);
            };

            recordingRef.current = { stream, videoStream, audioCtx, processor, behaviorCleanup };
        } catch (err) {
            console.error('Mic setup failed:', err);
            setError('Không thể truy cập microphone. Vui lòng cấp quyền ghi âm.');
        }
    };

    const startBehaviorMonitoring = async (videoStream, ws) => {
        const videoTracks = videoStream?.getVideoTracks?.() || [];
        if (videoTracks.length === 0) {
            setCameraStatus('unavailable');
            sendBehaviorEvent(ws, {
                kind: 'camera_unavailable',
                severity: 'medium',
                confidence: 1,
                detail: 'Camera stream was not available.',
            }, 0);
            return () => {};
        }

        setCameraStatus('active');
        sendBehaviorEvent(ws, {
            kind: 'camera_ready',
            severity: 'low',
            confidence: 0.9,
            detail: 'Camera is active for behavioral observations.',
        }, 0);

        const video = videoPreviewRef.current;
        if (video) {
            video.srcObject = videoStream;
            video.muted = true;
            video.playsInline = true;
            await video.play().catch(() => {});
        }

        const canvas = document.createElement('canvas');
        canvas.width = 160;
        canvas.height = 120;
        const ctx = canvas.getContext('2d', { willReadFrequently: true });
        const FaceDetectorCtor = window.FaceDetector;
        const faceDetector = FaceDetectorCtor
            ? new FaceDetectorCtor({ fastMode: true, maxDetectedFaces: 2 })
            : null;

        if (!faceDetector) {
            sendBehaviorEvent(ws, {
                kind: 'camera_analysis_limited',
                severity: 'info',
                confidence: 1,
                detail: 'Native FaceDetector is not supported in this browser.',
            }, 0);
        }

        let previousPixels = null;
        let lastFaceCenter = null;
        let noFaceSince = 0;
        let offCenterSince = 0;
        let centeredSince = 0;
        let restlessTicks = 0;
        let lowLightTicks = 0;
        let running = false;

        const analyseFrame = async () => {
            if (running || !ctx || !video || video.readyState < 2) return;
            running = true;
            try {
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                const frame = ctx.getImageData(0, 0, canvas.width, canvas.height);
                let brightness = 0;
                let diff = 0;
                const sampleCount = Math.max(1, Math.floor(frame.data.length / 16));

                for (let i = 0; i < frame.data.length; i += 16) {
                    const gray = (frame.data[i] + frame.data[i + 1] + frame.data[i + 2]) / 3;
                    brightness += gray;
                    if (previousPixels) diff += Math.abs(gray - previousPixels[i / 16]);
                }

                brightness /= sampleCount;
                diff = previousPixels ? diff / sampleCount : 0;
                previousPixels = Array.from({ length: sampleCount }, (_, idx) => {
                    const p = idx * 16;
                    return (frame.data[p] + frame.data[p + 1] + frame.data[p + 2]) / 3;
                });

                if (brightness < 42) lowLightTicks += 1;
                else lowLightTicks = 0;
                if (lowLightTicks >= 4) {
                    sendBehaviorEvent(ws, {
                        kind: 'poor_lighting',
                        severity: 'medium',
                        confidence: 0.65,
                        detail: 'Camera image is too dark for reliable behavioral observations.',
                    });
                }

                if (diff > 38) restlessTicks += 1;
                else restlessTicks = Math.max(0, restlessTicks - 1);
                if (restlessTicks >= 4) {
                    sendBehaviorEvent(ws, {
                        kind: 'restless_motion',
                        severity: 'medium',
                        confidence: 0.55,
                        detail: 'Camera frame changed rapidly several times in a short period.',
                    });
                    restlessTicks = 0;
                }

                if (faceDetector) {
                    const faces = await faceDetector.detect(video);
                    const now = Date.now();
                    if (faces.length === 0) {
                        if (!noFaceSince) noFaceSince = now;
                        centeredSince = 0;
                        if (now - noFaceSince > 3000) {
                            sendBehaviorEvent(ws, {
                                kind: 'face_not_visible',
                                severity: 'high',
                                confidence: 0.8,
                                detail: 'No face was visible for more than 3 seconds.',
                            });
                        }
                    } else {
                        noFaceSince = 0;
                        if (faces.length > 1) {
                            sendBehaviorEvent(ws, {
                                kind: 'multiple_faces',
                                severity: 'high',
                                confidence: 0.8,
                                detail: `${faces.length} faces were visible in the camera frame.`,
                            });
                        }

                        const face = faces[0].boundingBox;
                        const videoWidth = video.videoWidth || 1;
                        const videoHeight = video.videoHeight || 1;
                        const center = {
                            x: (face.x + face.width / 2) / videoWidth,
                            y: (face.y + face.height / 2) / videoHeight,
                        };
                        const centered =
                            center.x >= 0.34 && center.x <= 0.66 && center.y >= 0.22 && center.y <= 0.78;

                        if (centered) {
                            offCenterSince = 0;
                            if (!centeredSince) centeredSince = now;
                            if (now - centeredSince > 10000) {
                                sendBehaviorEvent(ws, {
                                    kind: 'eye_contact_stable',
                                    severity: 'low',
                                    confidence: 0.6,
                                    detail: 'Face stayed centered for a sustained period.',
                                }, 12000);
                                centeredSince = now;
                            }
                        } else {
                            centeredSince = 0;
                            if (!offCenterSince) offCenterSince = now;
                            if (now - offCenterSince > 3500) {
                                sendBehaviorEvent(ws, {
                                    kind: 'face_off_center',
                                    severity: 'medium',
                                    confidence: 0.65,
                                    detail: 'Face was off-center for more than 3 seconds.',
                                });
                            }
                        }

                        if (lastFaceCenter) {
                            const jump = Math.abs(center.x - lastFaceCenter.x) + Math.abs(center.y - lastFaceCenter.y);
                            if (jump > 0.22) {
                                sendBehaviorEvent(ws, {
                                    kind: 'restless_motion',
                                    severity: 'medium',
                                    confidence: 0.65,
                                    detail: 'Face position moved abruptly in the camera frame.',
                                });
                            }
                        }
                        lastFaceCenter = center;
                    }
                }
            } finally {
                running = false;
            }
        };

        const timer = window.setInterval(analyseFrame, 1000);
        return () => {
            window.clearInterval(timer);
            if (videoPreviewRef.current) videoPreviewRef.current.srcObject = null;
        };
    };

    const sendBehaviorEvent = (ws, event, minIntervalMs = 6000) => {
        if (!ws || ws.readyState !== WebSocket.OPEN || !event?.kind) return;
        const now = Date.now();
        const lastSent = behaviorLastSentRef.current[event.kind] || 0;
        if (now - lastSent < minIntervalMs) return;
        behaviorLastSentRef.current[event.kind] = now;

        const payload = { ...event, ts: now / 1000 };
        ws.send(JSON.stringify({ action: 'behavior_event', event: payload }));
        setBehaviorEvents((prev) => [payload, ...prev].slice(0, 5));
    };

    useEffect(() => {
        let disposed = false;
        let awaySince = 0;
        let awayTimer = null;
        let monitorTimer = null;
        let screenDetails = null;

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
                    detail: `Candidate left the interview window for ${(awayMs / 1000).toFixed(1)}s.`,
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

        const evaluateMonitor = () => {
            const extended = window.screen?.isExtended === true;
            const count = screenDetails?.screens?.length || (extended ? 2 : 1);
            if (extended || count > 1) {
                report({
                    kind: 'secondary_monitor',
                    severity: 'high',
                    confidence: 0.8,
                    detail: `${count} display(s) detected during the interview.`,
                }, 15000);
            }
        };

        const monitorSupported =
            typeof window.screen?.isExtended === 'boolean' ||
            typeof window.getScreenDetails === 'function';

        if (typeof window.getScreenDetails === 'function') {
            window.getScreenDetails()
                .then((details) => {
                    if (disposed) return;
                    screenDetails = details;
                    evaluateMonitor();
                    details.addEventListener?.('screenschange', evaluateMonitor);
                })
                .catch((err) => {
                    if (typeof window.screen?.isExtended !== 'boolean') {
                        report({
                            kind: 'detection_unsupported',
                            severity: 'info',
                            confidence: 1,
                            detail: `Screen detection unavailable: ${err?.message || err}`,
                        }, 0);
                    }
                });
        } else if (monitorSupported) {
            evaluateMonitor();
        } else {
            report({
                kind: 'detection_unsupported',
                severity: 'info',
                confidence: 1,
                detail: 'This browser cannot detect extended displays.',
            }, 0);
        }

        if (monitorSupported) {
            monitorTimer = window.setInterval(evaluateMonitor, 15000);
        }

        return () => {
            disposed = true;
            clearAwayTimer();
            if (monitorTimer) window.clearInterval(monitorTimer);
            document.removeEventListener('visibilitychange', onVisibility);
            window.removeEventListener('blur', onBlur);
            window.removeEventListener('focus', comeBack);
            screenDetails?.removeEventListener?.('screenschange', evaluateMonitor);
        };
    }, []);

    const stopRecording = () => {
        if (!recordingRef.current) return;
        try {
            const { stream, videoStream, audioCtx, processor, behaviorCleanup } = recordingRef.current;
            behaviorCleanup?.();
            stream.getTracks().forEach((track) => track.stop());
            videoStream?.getTracks?.().forEach((track) => track.stop());
            processor.disconnect();
            audioCtx.close();
        } catch {
            // Best-effort cleanup.
        }
        recordingRef.current = null;
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
            if (wsRef.current === ws) {
                wsRef.current = null;
            }
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

    const handleSendTypedAnswer = (event) => {
        event.preventDefault();
        const text = typedAnswer.trim();
        if (!text || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
        wsRef.current.send(JSON.stringify({ action: 'text_answer', text }));
        setTypedAnswer('');
    };

    const handleCopyMeetingLink = async () => {
        if (!sessionInfo?.meetingUrl || !navigator.clipboard) return;
        await navigator.clipboard.writeText(sessionInfo.meetingUrl);
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
            setError(err.message || 'Chưa tải được báo cáo. Vui lòng thử lại sau vài giây.');
        } finally {
            setLoadingReport(false);
        }
    };

    const saveSessionToHistory = (evaluation) => {
        if (!evaluation?.session_id) return;
        const storedHistory = localStorage.getItem('lancerai_interview_history') || '[]';
        let historyList = [];
        try {
            historyList = JSON.parse(storedHistory);
        } catch {
            historyList = [];
        }

        const scorecardScore = Number(evaluation.scorecard?.overall_score || 0);
        const score = scorecardScore ? Math.round((scorecardScore / 5) * 100) : Math.round((evaluation.overall_score || 0) * 10);
        const newSession = {
            id: evaluation.session_id,
            title: `Phỏng vấn ${evaluation.job_title || sessionInfo?.jobTitle || 'CV'}`,
            date: new Date().toLocaleDateString('vi-VN'),
            score,
            behaviorScore: Math.round(evaluation.behavior_score || 100),
        };

        const updatedHistory = [newSession, ...historyList.filter((item) => item.id !== newSession.id)];
        localStorage.setItem('lancerai_interview_history', JSON.stringify(updatedHistory));
    };

    const statusText = {
        connecting: 'Đang kết nối phòng phỏng vấn',
        listening: 'Đang nghe ứng viên',
        processing: 'Đang xử lý câu trả lời',
        speaking: 'AI đang đặt câu hỏi',
        ended: 'Phiên phỏng vấn đã kết thúc',
    }[phase] || phase;

    const statusTextClean = {
        connecting: 'Đang kết nối phòng phỏng vấn',
        listening: 'Đang nghe ứng viên',
        processing: 'Đang phân tích câu trả lời',
        speaking: 'AI đang đặt câu hỏi',
        ended: 'Phiên phỏng vấn đã kết thúc',
    }[phase] || phase;
    const statusHintClean = {
        connecting: 'Đang mở WebSocket, microphone và camera.',
        listening: 'Bạn có thể trả lời bằng giọng nói hoặc nhập text.',
        processing: 'Hệ thống đang chuyển giọng nói thành transcript và đánh giá ngữ cảnh.',
        speaking: 'Đợi AI hỏi xong để tránh chồng âm thanh.',
        ended: 'Bạn có thể xem báo cáo tổng hợp ngay khi hệ thống lưu xong.',
    }[phase] || '';

    return (
        <div style={styles.page}>
            <Navbar />
            <main style={styles.container}>
                <div style={styles.topBar}>
                    <button className="btn-tertiary" onClick={() => navigate('/interview')}>
                        Quay lại
                    </button>
                    <div style={styles.roomMeta}>
                        <span style={styles.metaLabel}>Phòng phỏng vấn CV live</span>
                        <strong style={styles.metaTitle}>{sessionInfo?.jobTitle || 'CV Interview'}</strong>
                    </div>
                    {sessionInfo?.meetingUrl && (
                        <button className="btn-outline" type="button" onClick={handleCopyMeetingLink}>
                            Copy link
                        </button>
                    )}
                </div>

                {error && <div style={styles.errorBox}>{error}</div>}

                <section style={styles.roomGrid}>
                    <div style={styles.leftPane}>
                        <div style={styles.videoShell}>
                            <video ref={videoPreviewRef} style={styles.videoPreview} />
                            {cameraStatus !== 'active' && (
                                <div style={styles.videoPlaceholder}>
                                    {cameraStatus === 'unavailable' ? 'Không có camera' : 'Đang bật camera'}
                                </div>
                            )}
                            <div style={styles.videoBadge}>
                                {cameraStatus === 'active' ? 'Camera đang bật' : 'Camera chưa sẵn sàng'}
                            </div>
                        </div>

                        <div style={styles.statusCard}>
                            <div style={styles.statusLine}>
                                <span style={styles.statusDot(phase)} />
                                <div>
                                    <strong style={styles.statusTitle}>{statusTextClean}</strong>
                                    <p style={styles.statusHintActive}>{statusHintClean}</p>
                                    <p style={styles.statusHint}>
                                        {phase === 'listening'
                                            ? 'Bạn có thể nói trực tiếp hoặc nhập câu trả lời bằng text.'
                                            : 'Hệ thống đang giữ lượt nói để tránh chồng âm thanh.'}
                                    </p>
                                </div>
                            </div>
                            <div style={styles.controls}>
                                {phase !== 'ended' ? (
                                    <button style={styles.btnStop} onClick={handleStopInterview}>
                                        Kết thúc
                                    </button>
                                ) : (
                                    <button className="btn-primary" onClick={handleViewReport} disabled={loadingReport}>
                                        {loadingReport ? 'Đang tải báo cáo...' : 'Xem báo cáo'}
                                    </button>
                                )}
                            </div>
                        </div>

                        <div style={styles.behaviorCard}>
                            <div style={styles.panelHeader}>
                                <strong>Quan sát hành vi</strong>
                                <span style={styles.smallMuted}>Tín hiệu phụ</span>
                            </div>
                            <div style={styles.behaviorEvents}>
                                {behaviorEvents.length === 0 ? (
                                    <span style={styles.smallMuted}>Chưa có tín hiệu đáng chú ý.</span>
                                ) : behaviorEvents.map((event, idx) => (
                                    <span key={`${event.kind}-${idx}`} style={styles.behaviorChip(event.severity)}>
                                        {event.kind.replaceAll('_', ' ')}
                                    </span>
                                ))}
                            </div>
                        </div>

                    </div>

                    <div style={styles.chatPane}>
                        <div style={styles.panelHeader}>
                            <div>
                                <strong>Log hội thoại</strong>
                                <p style={styles.statusHintActive}>Transcript dùng để chấm STAR và tạo report.</p>
                            </div>
                            <span style={styles.messageCount}>{messages.length} lượt</span>
                        </div>

                        <div style={styles.chatBox}>
                            {messages.length === 0 && (
                                <div style={styles.emptyChat}>
                                    Đang chuẩn bị câu hỏi đầu tiên. Cho phép microphone và camera để bắt đầu.
                                </div>
                            )}
                            {messages.map((msg) => {
                                const isUser = msg.sender === 'user';
                                const isSystem = msg.sender === 'system';
                                return (
                                    <div
                                        key={msg.id}
                                        style={{
                                            display: 'flex',
                                            justifyContent: isUser ? 'flex-end' : 'flex-start',
                                        }}
                                    >
                                        <div style={isSystem ? styles.bubbleSystem : isUser ? styles.bubbleUser : styles.bubbleAI}>
                                            <span style={styles.senderLabel}>
                                                {isSystem ? 'Hệ thống' : isUser ? 'Bạn' : 'AI phỏng vấn'}
                                            </span>
                                            <div>{msg.text}</div>
                                        </div>
                                    </div>
                                );
                            })}
                            <div ref={chatEndRef} />
                        </div>

                        <form style={styles.textForm} onSubmit={handleSendTypedAnswer}>
                            <input
                                style={styles.textInput}
                                value={typedAnswer}
                                onChange={(event) => setTypedAnswer(event.target.value)}
                                placeholder="Nhập câu trả lời nếu muốn dùng text thay microphone..."
                                disabled={phase === 'ended' || phase === 'speaking' || phase === 'connecting'}
                            />
                            <button
                                className="btn-primary"
                                type="submit"
                                disabled={!typedAnswer.trim() || phase === 'ended' || phase === 'speaking' || phase === 'connecting'}
                            >
                                Gửi
                            </button>
                        </form>
                    </div>
                </section>
            </main>
        </div>
    );
};

const styles = {
    page: {
        height: '100vh',
        maxHeight: '100vh',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, var(--canvas) 0%, var(--canvas-soft) 55%, var(--surface-strong) 100%)',
        display: 'flex',
        flexDirection: 'column',
    },
    container: {
        height: 'calc(100vh - var(--nav-height))',
        minHeight: 0,
        width: '100%',
        maxWidth: '1440px',
        margin: '0 auto',
        padding: '12px 18px 16px',
        display: 'flex',
        flexDirection: 'column',
        gap: '10px',
        overflow: 'hidden',
    },
    topBar: {
        minHeight: '42px',
        display: 'grid',
        gridTemplateColumns: 'auto minmax(0, 1fr) auto',
        alignItems: 'center',
        gap: '12px',
        flexShrink: 0,
    },
    roomMeta: {
        minWidth: 0,
        display: 'flex',
        flexDirection: 'column',
    },
    metaLabel: {
        fontSize: '11px',
        color: 'var(--muted)',
        textTransform: 'uppercase',
        letterSpacing: '0.6px',
    },
    metaTitle: {
        color: 'var(--ink)',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
    },
    errorBox: {
        flexShrink: 0,
        background: 'var(--gradient-rose)',
        color: 'var(--ink)',
        padding: '8px 12px',
        borderRadius: 'var(--rounded-md)',
        fontSize: '13px',
        fontWeight: 600,
    },
    roomGrid: {
        flex: 1,
        minHeight: 0,
        display: 'grid',
        gridTemplateColumns: 'minmax(320px, 0.85fr) minmax(420px, 1.15fr)',
        gap: '14px',
        alignItems: 'stretch',
        overflow: 'hidden',
    },
    leftPane: {
        display: 'grid',
        gridTemplateRows: 'minmax(220px, 1fr) auto minmax(92px, 128px)',
        gap: '10px',
        minWidth: 0,
        minHeight: 0,
        overflow: 'hidden',
    },
    chatPane: {
        minWidth: 0,
        minHeight: 0,
        display: 'flex',
        flexDirection: 'column',
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-lg)',
        background: 'var(--surface-card)',
        overflow: 'hidden',
    },
    videoShell: {
        position: 'relative',
        width: '100%',
        height: '100%',
        minHeight: 0,
        borderRadius: 'var(--rounded-lg)',
        background: 'var(--surface-strong)',
        border: '1px solid var(--hairline)',
        overflow: 'hidden',
    },
    videoPreview: {
        width: '100%',
        height: '100%',
        objectFit: 'cover',
        display: 'block',
        background: 'var(--surface-strong)',
    },
    videoPlaceholder: {
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'var(--muted)',
        background: 'var(--surface-strong)',
    },
    videoBadge: {
        position: 'absolute',
        left: '12px',
        bottom: '12px',
        padding: '6px 10px',
        borderRadius: 'var(--rounded-pill)',
        background: 'rgba(0, 0, 0, 0.55)',
        color: '#fff',
        fontSize: '12px',
    },
    statusCard: {
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-lg)',
        background: 'var(--surface-card)',
        padding: '12px',
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) auto',
        alignItems: 'center',
        gap: '10px',
        minHeight: '78px',
    },
    statusLine: {
        display: 'flex',
        alignItems: 'center',
        gap: '10px',
        minWidth: 0,
    },
    statusTitle: {
        display: 'block',
        color: 'var(--ink)',
        lineHeight: 1.2,
        whiteSpace: 'nowrap',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
    },
    statusDot: (currentPhase) => ({
        width: '12px',
        height: '12px',
        borderRadius: 'var(--rounded-full)',
        flexShrink: 0,
        background:
            currentPhase === 'listening'
                ? 'var(--gradient-mint)'
                : currentPhase === 'processing'
                    ? 'var(--primary)'
                    : currentPhase === 'speaking'
                        ? 'var(--gradient-peach)'
                        : 'var(--muted)',
        boxShadow: currentPhase === 'listening' ? '0 0 0 6px rgba(88, 166, 111, 0.12)' : 'none',
    }),
    statusHint: {
        display: 'none',
    },
    statusHintActive: {
        margin: '4px 0 0',
        color: 'var(--muted)',
        fontSize: '12px',
        lineHeight: 1.4,
    },
    controls: {
        display: 'flex',
        gap: 'var(--sp-xs)',
    },
    btnStop: {
        background: 'var(--gradient-rose)',
        color: 'var(--ink)',
        padding: '10px 16px',
        border: 'none',
        borderRadius: 'var(--rounded-md)',
        cursor: 'pointer',
        fontWeight: 700,
    },
    behaviorCard: {
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-lg)',
        background: 'var(--surface-card)',
        padding: 0,
        minHeight: 0,
        overflow: 'hidden',
    },
    panelHeader: {
        display: 'flex',
        justifyContent: 'space-between',
        gap: 'var(--sp-sm)',
        alignItems: 'flex-start',
        padding: '8px 10px',
        borderBottom: '1px solid var(--hairline)',
        color: 'var(--ink)',
        flexShrink: 0,
    },
    smallMuted: {
        color: 'var(--muted)',
        fontSize: '12px',
    },
    behaviorEvents: {
        display: 'flex',
        gap: '6px',
        flexWrap: 'wrap',
        padding: '8px 10px 10px',
        overflow: 'hidden',
    },
    behaviorChip: (severity) => ({
        fontSize: '11px',
        padding: '4px 8px',
        borderRadius: 'var(--rounded-pill)',
        border: '1px solid var(--hairline)',
        background:
            severity === 'high'
                ? 'var(--gradient-rose)'
                : severity === 'medium'
                    ? 'var(--gradient-peach)'
                    : 'var(--surface-strong)',
        color: 'var(--ink)',
        textTransform: 'capitalize',
    }),
    messageCount: {
        color: 'var(--muted)',
        fontSize: '12px',
        whiteSpace: 'nowrap',
    },
    chatBox: {
        flex: 1,
        minHeight: 0,
        overflowY: 'auto',
        padding: 'var(--sp-base)',
        display: 'flex',
        flexDirection: 'column',
        gap: 'var(--sp-sm)',
    },
    emptyChat: {
        color: 'var(--muted)',
        textAlign: 'center',
        margin: 'auto',
        maxWidth: '320px',
        lineHeight: 1.6,
    },
    senderLabel: {
        display: 'block',
        fontSize: '11px',
        fontWeight: 700,
        color: 'var(--muted)',
        marginBottom: '4px',
        textTransform: 'uppercase',
        letterSpacing: '0.4px',
    },
    bubbleUser: {
        maxWidth: '82%',
        padding: '10px 12px',
        borderRadius: 'var(--rounded-lg) var(--rounded-lg) var(--rounded-xs) var(--rounded-lg)',
        background: 'var(--primary)',
        color: 'var(--on-primary)',
        fontSize: '14px',
        lineHeight: 1.55,
    },
    bubbleAI: {
        maxWidth: '82%',
        padding: '10px 12px',
        borderRadius: 'var(--rounded-lg) var(--rounded-lg) var(--rounded-lg) var(--rounded-xs)',
        background: 'var(--surface-strong)',
        color: 'var(--body-strong, var(--ink))',
        border: '1px solid var(--hairline)',
        fontSize: '14px',
        lineHeight: 1.55,
    },
    bubbleSystem: {
        maxWidth: '90%',
        padding: '10px 12px',
        borderRadius: 'var(--rounded-md)',
        background: 'var(--canvas-soft)',
        color: 'var(--muted)',
        border: '1px solid var(--hairline)',
        fontSize: '13px',
        lineHeight: 1.5,
    },
    textForm: {
        display: 'grid',
        gridTemplateColumns: 'minmax(0, 1fr) auto',
        gap: 'var(--sp-xs)',
        padding: 'var(--sp-sm)',
        borderTop: '1px solid var(--hairline)',
        background: 'var(--surface-card)',
        flexShrink: 0,
    },
    textInput: {
        minWidth: 0,
        border: '1px solid var(--hairline)',
        borderRadius: 'var(--rounded-md)',
        padding: '10px 12px',
        background: 'var(--canvas)',
        color: 'var(--ink)',
        outline: 'none',
    },
};

export default ChatPage;
