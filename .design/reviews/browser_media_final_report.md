# Browser media final report - LancerAI

Date: 2026-07-09

## Result

Status: Pass for safe blocker/critical fixes.

The live interview media architecture is valid for a browser app: browser permission and capture happen on the frontend; backend receives audio bytes over WebSocket and does not depend on server-local microphone/camera hardware.

## What changed

- `frontend/src/config/env.js`: production builds now default to same-origin API calls instead of `http://127.0.0.1:8000`.
- `frontend/.env.example`: added local/prod API guidance and HTTPS/WSS notes for camera/microphone.
- `frontend/src/pages/ChatPage.jsx`: uses the shared `INTERVIEW_WS_PATH`, closes WebSocket on fatal media failures, checks `AudioContext`, keeps mic audio muted locally while processing, and clarifies camera is optional.
- `frontend/src/components/Common/Visuals.jsx`: camera placeholder now accepts a contextual hint.
- `frontend/src/pages/InterviewPage.jsx` and `frontend/src/pages/MainDashboard.jsx`: copy now says microphone/transcript are core and camera is used only when available.
- `app/service/interview/behavior.py`: `camera_unavailable` is now a neutral system signal, not a behavior concern that reduces score.
- `tests/test_interview_behavior.py`: regression coverage added so missing camera stays neutral.

## Validation

- Frontend production build: `npm run build` passed.
- Backend targeted test: `uv run python -m pytest tests\test_interview_behavior.py` passed with `3 passed`.
- Full backend test suite: `uv run python -m pytest` passed with `171 passed, 7 deselected, 2 warnings`.
- Backend import/startup smoke: app import passed; 29 routes registered; `/api/v1/interview/ws` and `/api/v1/interview/health` are present.
- Browser media smoke: passed with system Chrome using fake camera/microphone. `navigator.mediaDevices.getUserMedia` was available in a secure context and returned 2 media tracks.

## Demo readiness notes

- Camera denial should no longer block or penalize a session.
- Microphone denial still blocks the voice interview, which matches the current product behavior.
- WebSocket must be `wss://` when the frontend is loaded over HTTPS.
- Same-origin production deployment should leave `VITE_API_BASE_URL` empty and proxy `/api/` through Nginx.

## Remaining manual checks

- Run a real authenticated browser flow: login -> create interview session -> allow mic/camera -> answer -> transcript -> report.
- Repeat with camera denied and microphone allowed.
- Repeat with microphone denied and confirm the room exits cleanly with the new message.
- Verify the deployed reverse proxy upgrades `/api/v1/interview/ws` to WebSocket successfully.
