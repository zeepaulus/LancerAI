# `app/service/interview/` - Real-Time Voice Interview

This bounded context owns interview planning, realtime voice conversation and final reporting.

## Components

| File | Role |
|---|---|
| `service.py` | REST-side session lifecycle, persistence and report assembly |
| `pipeline.py` | WebSocket session orchestrator: audio -> STT -> LLM -> TTS |
| `agents.py` | Question, evaluation and wrap-up LLM node functions |
| `planning.py` | Builds interview plan from CV/JD/job title/focus |
| `pacing.py` | Time and pacing helpers |
| `behavior.py` | Browser/candidate behavior event scoring |
| `scoring.py` | STAR/report score helpers and fallbacks |
| `state.py` | Interview state and sub-schemas |
| `state_machine.py` | Phase/state transition helpers |

## REST Flow

```text
POST /api/v1/interview/sessions
  -> validate InterviewSessionRequest
  -> verify CV ownership
  -> build JD data from text/url/job_listing_id
  -> infer/normalize job title
  -> build interview plan
  -> create InterviewSession
  -> return session_id, room_name, meeting_url, plan
```

Report flow:

```text
GET /api/v1/interview/sessions/{session_id}/report
  -> verify session ownership
  -> read star_scores JSON
  -> read transcript rows
  -> InterviewReportResponse
```

## WebSocket Flow

Endpoint: `WS /api/v1/interview/ws`

First client message:

```json
{"token":"<jwt>","session_id":"<session_id>","duration_minutes":5}
```

Then:

```text
Client binary PCM Int16 mono 16 kHz
  -> InterviewPipeline.feed_audio
  -> VAD detects end of utterance
  -> VoiceSTTConnector.transcribe
  -> transcript event
  -> LLM evaluate/respond
  -> VoiceTTSConnector.synthesize_stream
  -> server binary PCM Int16 mono 24 kHz
```

JSON actions:

- `{"action":"stop"}`
- `{"action":"text_answer","text":"..."}`
- `{"action":"behavior_event","event":{...}}`

## Audio Contract

| Direction | Format |
|---|---|
| Client -> server | PCM Int16 mono 16 kHz |
| Server -> client | PCM Int16 mono 24 kHz |

STT:

- Attempts Groq Whisper API when a real key is configured.
- Falls back to faster-whisper local.
- Skips very short or low-energy audio before loading a heavy model.

TTS:

- `edge`: Edge TTS with MP3 decode to PCM.
- `piper`: local Piper CLI/model with Edge fallback if missing.
- `vieneu`: VieNeu SDK/CLI/GGUF. Local GGUF failure raises so it does not silently use network TTS.

## Persistence

`InterviewService.create_session` creates a session shell and stores setup context plus interview plan in `star_scores`.

`InterviewService.persist_session` updates:

- `total_questions`
- `overall_confidence`
- `star_scores`
- `logic_issues`
- `improvement_suggestions`
- `completed_at`
- `status="completed"`
- `InterviewTranscript` rows

## Current Risks And Follow-Ups

- Transcript turns are mainly persisted at final stop; incremental persistence is recommended.
- Add server-side throttle for behavior events.
- Add max utterance duration to avoid unbounded audio buffers.
- Add explicit frontend events for no-speech, STT started, LLM thinking, TTS started and TTS error.
- Add preflight health checks for STT/TTS local models.
