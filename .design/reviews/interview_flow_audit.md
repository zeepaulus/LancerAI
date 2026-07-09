# Interview Flow Audit

Date: 2026-07-07

## Scope

Reviewed the current LancerAI voice interview flow across:

- `app/service/interview/pipeline.py`
- `app/service/interview/agents.py`
- `app/service/interview/state.py`
- `app/service/interview/planning.py`
- `app/service/interview/service.py`
- `app/router/v1/interview_api.py`
- `frontend/src/pages/InterviewPage.jsx`
- `frontend/src/pages/ChatPage.jsx`
- `frontend/src/pages/InterviewReportPage.jsx`

## Answers

### 1. Does the current LLM interview flow generate isolated questions based on the CV only?

Partially. The live interviewer prompt uses CV, optional JD, interview plan, and chat history, so it is not strictly CV-only. However, the runtime does not currently enforce a structured question plan or answer-quality decision before the next AI turn. The streamed LLM decides naturally from chat context.

### 2. Does it support follow-up questions?

Prompt-level only. The system prompt says the interviewer may ask follow-up questions when an answer is unclear, but the pipeline does not make a structured follow-up decision after each candidate answer.

### 3. Is there logic like `User answers -> AI detects unclear / weak / missing information -> AI asks a follow-up question`?

Not reliably. `evaluate_node()` can mark `follow_up_triggered`, but it is mostly used in final evaluation and its decision is not wired into the live `_generate_and_speak()` flow. Therefore follow-up behavior depends on the streaming LLM improvising from the conversation history.

### 4. Where is the interview prompt defined?

- Live interviewer prompt: `_build_system_prompt()` and `_build_planned_system_prompt()` in `app/service/interview/pipeline.py`.
- Next-question prompt helper: `_QUESTION_SYSTEM` and `question_node()` in `app/service/interview/agents.py`.
- Per-answer STAR evaluation prompt: `_EVALUATE_SYSTEM` and `evaluate_node()` in `app/service/interview/agents.py`.
- Final scoring prompt: `_SCORECARD_SYSTEM` and `scorecard_node()` in `app/service/interview/agents.py`.

### 5. Where is the interview session state stored?

- In memory during the WebSocket session: `InterviewPipeline.state`, an `InterviewState` model from `app/service/interview/state.py`.
- Persisted after the session: `InterviewSession` row, especially `star_scores`, `overall_confidence`, `logic_issues`, `improvement_suggestions`, plus `InterviewTranscript` rows.
- Initial setup context and interview plan are stored in `InterviewSession.star_scores["setup"]` and `InterviewSession.star_scores["interview_plan"]`.

### 6. How are user answers, transcript, and evaluation passed to the LLM?

- Audio is transcribed in `InterviewPipeline._process_user_turn()`.
- Text answers and STT transcripts enter `_handle_user_transcript()`.
- The transcript is appended to `state.chat_history` as a user message and to `state.turns` as a candidate turn.
- `_generate_and_speak()` streams the full chat history to `LLMConnector.generate_chat_stream()`.
- Final scoring sends transcript, CV, JD, STAR scores, and session observations to `scorecard_node()`.

## Main UX/Product Issues

- Follow-up behavior is prompt-instructed but not structurally controlled.
- `evaluate_node()` returns a `follow_up_triggered` flag, but the pipeline does not use it to choose the next live AI action.
- The interview setup UI still has broad industry options, while the product should focus only on IT roles.
- Some frontend language still frames the product as a recruiter/hiring dashboard instead of a candidate-side career assistant.
- Session integrity/camera signals are useful, but should not be presented as Emotion Detection or face sentiment.

## Emotion Detection Removal Note

No dedicated Emotion Detection route or visible feature was found in the frontend. The backend still has a `behavior` module and `sentiment` field in compatibility schemas/tests, but this is used for session integrity observations such as tab switching, camera unavailable, multiple faces, low light, or secondary monitor. Removing those fields would be risky for existing tests and API compatibility, so the UI should present them only as session integrity signals and never as emotion, facial sentiment, or psychological inference.

## Safe Assumptions

- Keep the existing WebSocket and REST API contracts.
- Add follow-up control inside the pipeline without introducing a new route.
- Keep camera/browser integrity events as anti-distraction/session-quality signals, not emotion detection.
- Implement Question Bank initially as frontend MVP data and route, connected to the interview setup through route state.
