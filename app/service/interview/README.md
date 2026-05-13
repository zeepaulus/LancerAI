# `app/service/interview/` — Real-time Voice Interview Pipeline (Module 4)

Sub-package triển khai **real-time voice interview** qua WebSocket. Một instance `InterviewPipeline` quản lý toàn bộ lifecycle của một phiên phỏng vấn giọng nói: nhận PCM audio từ microphone, transcribe, generate AI response, synthesize speech, và gửi lại client.

## Audio Flow

```
Mic PCM (16kHz)
  └─→ silence-based turn detection (energy gate)
      └─→ VoiceSTTConnector.transcribe()         → candidate transcript
          └─→ LLMConnector.generate_chat_stream() → interviewer tokens
              └─→ VoiceTTSConnector.synthesize_stream() → PCM chunks (24kHz)
                  └─→ WebSocket.send_bytes()      → speaker
```

## Files

### `service.py` — InterviewService (REST Companion)

REST-side orchestrator của Module 4. Không xử lý audio hay conversation — chỉ quản lý session lifecycle qua REST endpoints.

| Method | Description |
|---|---|
| `create_session(cv_id, user_id, mode, job_listing_id, duration_minutes)` | Tạo session shell record (status: created), trả về `session_id` |
| `persist_session(payload)` | Chuyển `InterviewState` hoàn chỉnh → `InterviewSession` row + `InterviewTranscript` rows (PostgreSQL) |
| `get_report(session_id)` | Assemble `InterviewReportResponse` cho frontend analytics dashboard |

Dependencies: `LLMConnector` (post-hoc scoring), `RelationalRepository[InterviewSession]`.

`InterviewService` không inject STT/TTS — xử lý audio trong `InterviewPipeline`.

---

### `state.py` — Interview Session State Schema

`InterviewState` (Pydantic `BaseModel`) là shared state của một phiên phỏng vấn.

**State sections:**

| Section | Fields | Description |
|---|---|---|
| Session info | `session_id`, `cv_data`, `jd_data`, `job_title`, `interview_mode` | Context khởi tạo phiên |
| Duration | `duration_minutes`, `start_time`, `elapsed_seconds` | Time-based session control (không phải question-count-based) |
| Chat history | `chat_history: list[ChatMessage]` | LLM context window (system + assistant + user messages) |
| Turns | `turns: Annotated[list[InterviewTurn], operator.add]` | Conversation transcript (append-only, cho STAR analysis) |
| STAR scores | `star_scores: Annotated[list[STARScore], operator.add]` | Per-answer evaluation (filled post-hoc) |
| Current state | `current_question`, `waiting_for_answer`, `latest_transcript` | STT output từ user turn gần nhất |
| Final assessment | `overall_score`, `strengths`, `improvements`, `final_feedback` | Tổng kết phiên |
| Control | `next_action: Literal[...]`, `error` | `ask` / `evaluate` / `follow_up` / `wrap_up` / `done` |

**Sub-schemas:**

| Schema | Description |
|---|---|
| `STARScore` | Structured per-answer eval: `situation_score`, `task_score`, `action_score`, `result_score` (0–10 each), `overall_score`, `feedback`, `follow_up_triggered` |
| `ChatMessage` | LLM message format: `role` (`system`/`assistant`/`user`), `content`, `timestamp` |
| `InterviewTurn` | Transcript turn: `role` (`interviewer`/`candidate`), `content`, `audio_duration_ms` |

**Helper methods:**
- `get_remaining_seconds()` — tính thời gian còn lại dựa trên `start_time` + `duration_minutes`.
- `is_time_up()` — boolean check, dùng bởi pipeline để trigger wrap-up.
- `to_llm_messages()` — convert `chat_history` sang `list[dict]` format của LLM API.

**Design note**: Interview chạy theo **time-based model** (flexible, không phải question-count-based) — phù hợp với real conversation flow.

### `pipeline.py` — Interview Session Orchestrator

`InterviewPipeline` quản lý một WebSocket session.

```python
class InterviewPipeline:
    def __init__(self, llm, stt, tts, send_json, send_bytes): ...
```

Dependencies được inject qua constructor (không phụ thuộc FastAPI); `send_json` và `send_bytes` là callables — dễ mock trong tests.

| Method | Description |
|---|---|
| `start(job_title, cv_data, jd_data, mode, duration_minutes)` | Build system prompt từ CV + JD context, emit interviewer greeting |
| `feed_audio(pcm_bytes)` | Consume một chunk PCM Int16 mono 16kHz, trigger turn detection |
| `stop()` | Teardown session, chạy STAR evaluation, return final payload |

**Internal components (planned):**
- `_silence_detection_loop`: energy-based turn detection, flush user audio đến STT.
- `_generate_and_speak`: stream LLM tokens → sentence-by-sentence TTS → send PCM chunks.
- `_run_final_evaluation`: STAR scoring cho toàn bộ conversation (Vietnamese).

State machine điều phối bởi `InterviewState.next_action`:
```
ask → (candidate answers) → evaluate → [follow_up | ask | wrap_up] → done
```

### `agents.py` — Interview Agent Node Functions

Ba async functions đóng vai trò "agent nodes" trong interview state machine. Không dùng LangGraph wiring (driven imperatively bởi `InterviewPipeline`) — có thể nâng cấp thành LangGraph graph sau nếu cần LangSmith tracing.

| Function | Description |
|---|---|
| `question_node(state, llm)` | Generate câu hỏi tiếp theo từ CV + JD context |
| `evaluate_node(state, llm)` | STAR-score candidate's most recent answer (json_mode=True) |
| `wrap_up_node(state, llm)` | Produce final holistic assessment cho phiên |

Prompt templates: Vietnamese-friendly, structured JSON output.

## Technology

| Component | Library |
|---|---|
| State schema | **Pydantic v2** (`BaseModel`, `Annotated`, `operator.add`) |
| Speech-to-Text | `VoiceSTTConnector` (PhoWhisper-base @ 16kHz) |
| Text-to-Speech | `VoiceTTSConnector` (Edge TTS / Piper / VieNeu @ 24kHz) |
| LLM | `LLMConnector` streaming API (`generate_chat_stream`) |
| Transport | FastAPI `WebSocket` (binary frames for PCM, JSON frames for events) |
| Async | Python `asyncio` (`asyncio.Event` cho abort generation) |
