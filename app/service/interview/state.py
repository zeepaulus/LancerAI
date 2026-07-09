"""Interview Agent State Schema.

Manages the full state of a voice interview session:
- Interview metadata (job, candidate, mode, duration)
- CV data (from UC2: Upload CV)
- JD data (from UC4: Job matching — required for interview context)
- Conversation history (chat messages for LLM context)
- Per-answer STAR evaluation scores (post-hoc analysis)
- Final assessment

Pre-conditions (per spec UC5):
    1. Ứng viên đã đăng nhập và đã có CV được số hóa trên hệ thống.
    2. Ứng viên đã chọn được một vị trí công việc (JD) cụ thể.
"""

import operator
import time
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field

from app.service.interview.behavior import BehaviorEvent


class STARScore(BaseModel):
    """Structured evaluation of a candidate's answer using the STAR method."""

    answer_index: int = 0
    question: str = ""
    answer_transcript: str = ""

    # STAR components (0-10 each)
    situation_score: float = Field(0.0, ge=0.0, le=10.0)
    task_score: float = Field(0.0, ge=0.0, le=10.0)
    action_score: float = Field(0.0, ge=0.0, le=10.0)
    result_score: float = Field(0.0, ge=0.0, le=10.0)

    overall_score: float = Field(0.0, ge=0.0, le=10.0)
    feedback: str = ""
    follow_up_triggered: bool = False
    ask_follow_up: bool = False
    follow_up_question: str = ""
    follow_up_reason: str = ""
    evaluation_notes: str = ""
    next_action: Literal["ask_next", "ask_follow_up", "wrap_up"] = "ask_next"


class ChatMessage(BaseModel):
    """A single message in the interview conversation (LLM chat format)."""

    role: Literal["system", "assistant", "user"]
    content: str
    timestamp: float = Field(default_factory=time.time)


class InterviewTurn(BaseModel):
    """A single turn in the interview conversation."""

    role: Literal["interviewer", "candidate"]
    content: str
    audio_duration_ms: int = 0
    created_at: float = Field(default_factory=time.time)


class InterviewState(BaseModel):
    """Shared state for a real-time voice interview session.

    The interview runs as a natural conversation:
    - LLM receives a system prompt defining it as an interviewer
    - Chat history is maintained for context
    - STAR evaluation happens post-hoc when session ends
    - Duration is time-based (flexible, not question-count-based)
    """

    # --- Session info ---
    session_id: str = ""
    cv_data: dict[str, Any] = Field(default_factory=dict)
    jd_data: dict[str, Any] = Field(default_factory=dict)  # Job Description data (from DB)
    interview_plan: dict[str, Any] = Field(default_factory=dict)
    job_title: str = ""
    job_description: str = ""
    interview_mode: Literal["practice", "mock", "quick"] = "practice"

    # --- Duration (time-based) ---
    duration_minutes: int = 5  # Target duration: 3, 5, 10, 15, or custom
    start_time: float = 0.0  # Unix timestamp when session started
    elapsed_seconds: float = 0.0  # Updated periodically

    # --- Chat history (for LLM context) ---
    chat_history: list[ChatMessage] = Field(default_factory=list)

    # --- Conversation turns (append-only, for STAR analysis) ---
    turns: Annotated[list[InterviewTurn], operator.add] = Field(default_factory=list)

    # --- STAR scores (append-only, filled post-hoc) ---
    star_scores: Annotated[list[STARScore], operator.add] = Field(default_factory=list)

    # --- Behavioral observations from camera/browser signals ---
    behavior_events: list[BehaviorEvent] = Field(default_factory=list)

    # --- Current state ---
    current_question: str = ""
    current_question_index: int = 0
    total_questions: int = 0  # Estimated, flexible
    waiting_for_answer: bool = False
    latest_transcript: str = ""  # STT output from last user turn
    follow_up_depth: int = 0
    max_follow_ups_per_question: int = 1
    pending_follow_up_question: str = ""
    pending_follow_up_reason: str = ""
    latest_evaluation_notes: str = ""

    # --- Final assessment ---
    overall_score: float = 0.0
    strengths: list[str] = Field(default_factory=list)
    improvements: list[str] = Field(default_factory=list)
    final_feedback: str = ""
    session_complete: bool = False

    # --- Control ---
    next_action: Literal["ask", "evaluate", "follow_up", "wrap_up", "done"] = "ask"
    error: str = ""

    model_config = {"arbitrary_types_allowed": True}

    def get_remaining_seconds(self) -> float:
        """Calculate remaining time in the interview."""
        if self.start_time == 0:
            return self.duration_minutes * 60
        elapsed = time.time() - self.start_time
        return max(0.0, (self.duration_minutes * 60) - elapsed)

    def is_time_up(self) -> bool:
        """Check if the interview has exceeded its target duration."""
        return self.get_remaining_seconds() <= 0

    def to_llm_messages(self) -> list[dict[str, Any]]:
        """Convert chat history to the format expected by LLM."""
        return [{"role": m.role, "content": m.content} for m in self.chat_history]
