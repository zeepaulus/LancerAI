"""Session phase enum for the interview pipeline state machine.

Kept in a dedicated module to avoid circular imports between
``pipeline.py``, ``agents.py``, and any future WebSocket handler.
"""

from __future__ import annotations

from enum import StrEnum


class SessionPhase(StrEnum):
    """Pipeline state machine phases.

    Transitions:
        LISTENING  → PROCESSING  (VAD silence threshold crossed)
        PROCESSING → SPEAKING    (STT done, LLM started)
        SPEAKING   → LISTENING   (TTS finished all queued sentences)
        Any        → STOPPED     (stop() called)
    """

    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"
    STOPPED = "stopped"
