# Browser media pipeline audit - LancerAI

Date: 2026-07-09

Scope: Browser -> Frontend -> Backend WebSocket -> STT -> LLM -> TTS -> Frontend playback.

## Executive summary

The interview media flow is browser-owned, not server-device-owned. The frontend requests microphone/camera permission in `frontend/src/pages/ChatPage.jsx`; the backend receives browser audio as raw PCM bytes over `/api/v1/interview/ws` and never attempts to open a local microphone or camera.

Safe fixes were applied for demo-critical confusion:

- Production frontend builds now default to same-origin `/api` instead of `http://127.0.0.1:8000`.
- Fatal microphone/browser-media failures now close the WebSocket instead of leaving a live interview session hanging.
- Camera is treated as optional in both UI and backend behavior scoring.
- WebSocket/media errors shown to the user are now Vietnamese and actionable.

## Verified pipeline

1. Session setup: `InterviewPage` uploads CV and creates an interview session, then navigates to `/chat`.
2. WebSocket setup: `ChatPage.buildInterviewWsUrl()` builds `/api/v1/interview/ws` from same-origin proxy or `VITE_API_BASE_URL`.
3. Auth: frontend sends `{ token, session_id, duration_minutes }` as the first WebSocket message.
4. Microphone: `ChatPage.startRecording()` calls `navigator.mediaDevices.getUserMedia({ audio: true })`.
5. Camera: `ChatPage.startRecording()` separately calls `navigator.mediaDevices.getUserMedia({ video: ..., audio: false })`; failure is non-fatal.
6. Browser audio processing: `AudioContext` + `ScriptProcessorNode` resample microphone data to raw PCM Int16 mono 16 kHz and send binary WebSocket frames only while phase is `listening`.
7. Backend routing: `app/router/v1/interview_api.py` receives binary frames and calls `InterviewPipeline.feed_audio(...)`.
8. STT: `VoiceSTTConnector.transcribe(...)` consumes raw PCM bytes and returns Vietnamese transcript.
9. LLM: `InterviewPipeline._generate_and_speak()` streams interviewer text from the LLM connector.
10. TTS: `VoiceTTSConnector.synthesize_stream(...)` returns PCM Int16 mono 24 kHz chunks.
11. Playback: frontend receives WebSocket binary frames and plays them via `AudioContext`.

## Direct answers

1. Mic permission is requested in `frontend/src/pages/ChatPage.jsx` inside `startRecording()`, after the WebSocket opens and before audio chunks are sent.
2. Yes, the frontend uses `navigator.mediaDevices.getUserMedia()`.
3. Browser media APIs are used correctly for the current implementation: secure-context guard, `getUserMedia`, `AudioContext`, stream track cleanup, and binary WebSocket frames. `createScriptProcessor()` is deprecated but still broadly supported; replacing it with `AudioWorklet` is future polish, not a demo blocker.
4. Camera is not required. It is requested separately from microphone; denial or missing camera keeps the session running.
5. Microphone is mandatory for the current voice UI. Backend already supports `text_answer`, but the frontend does not expose a typed-answer fallback in the interview room.
6. Permission denial is handled with user-facing messages. Fatal mic/browser-media errors now close the active WebSocket to avoid a stuck session.
7. HTTPS is now documented in `frontend/.env.example` and `.design/deployment/browser_media_checklist.md`. Nginx also sets `Permissions-Policy` for camera/microphone.
8. Localhost assumptions were found and fixed for production builds: `frontend/src/config/env.js` now uses same-origin API by default in production.
9. The backend does not expect or open a local microphone/camera. Searches found no `pyaudio`, `sounddevice`, or `VideoCapture` usage in the backend media path.

## Issues fixed

| Priority | Issue | Evidence | Fix |
| --- | --- | --- | --- |
| P1 | Production build could silently target `http://127.0.0.1:8000` if `VITE_API_BASE_URL` was omitted. | `frontend/src/config/env.js` defaulted to localhost. | Production default is now `''`, so REST/WebSocket use the deployed same-origin proxy. |
| P1 | Microphone denial/unsupported media set the UI to ended but left the WebSocket open. | `startRecording()` returned after fatal media failures without closing `ws`. | Added `closeSocketQuietly(ws)` for HTTPS/media unsupported/mic denied/audio setup failures. |
| P1 | Camera denial was optional in frontend but still penalized as a behavior concern in backend reports. | `camera_unavailable` was catalogued as `sentiment: concern`. | Changed it to neutral/system and added a regression test. |
| P2 | Several WebSocket/media errors were still in English. | `ChatPage.jsx` showed English connection and session errors. | Replaced them with concise Vietnamese messages. |
| P2 | Camera UI implied the app was waiting forever when camera failed. | Overlay kept showing "Đang chờ camera". | UI now shows "Không dùng camera" and explains the session continues by micro/transcript. |

## Remaining risks

- Full browser permission testing requires a Playwright/real browser runtime with camera/micro permission emulation. If browser binaries are unavailable in the environment, this must be verified manually before demo.
- `ScriptProcessorNode` is deprecated. It is acceptable for the demo but should be migrated to `AudioWorklet` later for lower latency and future browser resilience.
- The backend supports typed fallback through `text_answer`, but the current frontend voice room does not expose that fallback. Keep microphone mandatory for demo or add a small typed fallback in a later UX pass.
