# Browser media deployment checklist - LancerAI

Use this checklist before demo or production deployment of the live interview room.

## Required configuration

- Serve the frontend over HTTPS. Browser camera/microphone APIs only work on secure origins, except `localhost` during local development.
- Same-origin production deployment: build frontend with `VITE_API_BASE_URL=` so REST calls and WebSocket use `/api/...` through the reverse proxy.
- Cross-origin API deployment: set `VITE_API_BASE_URL=https://<api-domain>` so the interview WebSocket resolves to `wss://<api-domain>/api/v1/interview/ws`.
- Backend CORS: set `ALLOWED_ORIGINS` to the exact HTTPS frontend origins.
- Backend `FRONTEND_BASE_URL`: set to the public HTTPS app URL so generated meeting/report links are not localhost links.
- Nginx/reverse proxy: `/api/` must support WebSocket upgrade headers:
  - `proxy_http_version 1.1`
  - `proxy_set_header Upgrade $http_upgrade`
  - `proxy_set_header Connection $connection_upgrade`
  - long enough `proxy_read_timeout` and `proxy_send_timeout`
- Permissions policy should allow browser media on the app origin: `Permissions-Policy: camera=(self), microphone=(self)`.
- STT/TTS runtime dependencies must be installed on the backend host. Edge TTS playback conversion also needs audio decode support such as `pydub` plus `ffmpeg`.

## Browser checks

- Chrome/Edge desktop: allow microphone and camera. Confirm transcript appears and AI audio plays.
- Chrome/Edge desktop: deny camera, allow microphone. Confirm the session continues and UI shows "Không dùng camera".
- Chrome/Edge desktop: deny microphone. Confirm the user sees a clear error and the WebSocket session closes.
- Safari desktop: allow microphone. Confirm `AudioContext` playback starts after the first AI response.
- HTTP non-localhost URL: confirm the app blocks media with an HTTPS guidance message.
- HTTPS production URL: confirm the WebSocket URL is `wss://.../api/v1/interview/ws`, not `ws://...` and not `127.0.0.1`.

## Backend checks

- `GET /api/v1/interview/health` returns 200.
- WebSocket `/api/v1/interview/ws` accepts the first auth JSON message for a valid session.
- Binary audio frames are handled by `InterviewPipeline.feed_audio(...)`.
- Backend logs do not show attempts to open local audio/video devices.
- A session with no camera should not reduce behavior score only because camera is unavailable.

## Demo fallback plan

- If camera is blocked, continue the demo with microphone and transcript.
- If microphone is blocked by the browser or OS, reopen the room after enabling browser permission.
- If WebSocket upgrade fails behind proxy, verify Nginx upgrade headers and that the frontend build is using same-origin or HTTPS API base URL.
- If TTS fails, transcript and assistant text should still appear; collect backend logs for the TTS connector.
