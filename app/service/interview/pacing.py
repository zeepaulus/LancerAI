"""Pacing clock for live CV interviews.

The runtime owns timing decisions; the LLM only receives concise guidance.
This mirrors the reference project's "code owns the clock" design while
staying independent from LiveKit.
"""

from __future__ import annotations

from collections.abc import Callable
from enum import StrEnum


class PacingSignal(StrEnum):
    ON_TRACK = "on_track"
    WRAP_SOON = "wrap_soon"
    WRAP_UP_NOW = "wrap_up_now"
    FORCE_END = "force_end"
    DEAD_AIR = "dead_air"
    ABANDON = "abandon"


_INSTRUCTIONS: dict[PacingSignal, str] = {
    PacingSignal.WRAP_SOON: (
        "Time check: begin steering toward the end. Ask only one high-value "
        "follow-up if it directly improves CV/JD evaluation."
    ),
    PacingSignal.WRAP_UP_NOW: (
        "The target interview time has been reached. Move to a brief closing, "
        "thank the candidate, and do not ask a new question."
    ),
    PacingSignal.FORCE_END: (
        "The hard time limit has been reached. Close the interview immediately "
        "in one short, polite turn."
    ),
    PacingSignal.DEAD_AIR: (
        "The candidate has been quiet for a while. Rephrase the last question "
        "or offer a short prompt to help them continue."
    ),
    PacingSignal.ABANDON: (
        "The candidate has been silent too long. Close the session and mark it "
        "as incomplete."
    ),
}

_TERMINAL = {PacingSignal.FORCE_END, PacingSignal.ABANDON}


def signal_instruction(signal: PacingSignal) -> str | None:
    """Return runtime instruction text for an actionable pacing signal."""
    return _INSTRUCTIONS.get(signal)


def is_terminal(signal: PacingSignal) -> bool:
    """Whether this signal must end the session."""
    return signal in _TERMINAL


class PacingClock:
    """Testable wall-clock controller for an interview session."""

    def __init__(
        self,
        *,
        duration_minutes: int,
        grace_minutes: int = 2,
        dead_air_prompt_sec: int = 45,
        max_silence_end_min: int = 5,
        wrap_soon_minutes: int = 1,
        now: Callable[[], float],
    ) -> None:
        self._duration_sec = max(1, duration_minutes) * 60
        self._grace_sec = max(0, grace_minutes) * 60
        self._dead_air_sec = max(1, dead_air_prompt_sec)
        self._max_silence_sec = max(1, max_silence_end_min) * 60
        self._wrap_soon_sec = max(0, wrap_soon_minutes) * 60
        self._now = now
        self._start: float | None = None
        self._last_activity: float | None = None
        self._paused_at: float | None = None
        self._paused_total = 0.0

    def start(self) -> None:
        current = self._clock_now()
        self._start = current
        self._last_activity = current

    def note_activity(self) -> None:
        """Record candidate activity and reset silence tracking."""
        self._last_activity = self._clock_now()

    def pause(self) -> None:
        """Pause active elapsed time, useful for future reconnect handling."""
        if self._paused_at is None:
            self._paused_at = self._now()

    def resume(self) -> None:
        if self._paused_at is not None:
            self._paused_total += self._now() - self._paused_at
            self._paused_at = None

    def elapsed(self) -> float:
        if self._start is None:
            return 0.0
        return max(0.0, self._clock_now() - self._start)

    def remaining_to_target(self) -> float:
        return max(0.0, self._duration_sec - self.elapsed())

    def signal(self) -> PacingSignal:
        elapsed = self.elapsed()
        hard_cap = self._duration_sec + self._grace_sec

        if elapsed >= hard_cap:
            return PacingSignal.FORCE_END

        silence = self._silence()
        if silence >= self._max_silence_sec:
            return PacingSignal.ABANDON
        if silence >= self._dead_air_sec:
            return PacingSignal.DEAD_AIR

        if elapsed >= self._duration_sec:
            return PacingSignal.WRAP_UP_NOW
        if elapsed >= self._duration_sec - self._wrap_soon_sec:
            return PacingSignal.WRAP_SOON
        return PacingSignal.ON_TRACK

    def _clock_now(self) -> float:
        raw = self._now()
        paused = self._paused_total
        if self._paused_at is not None:
            paused += raw - self._paused_at
        return raw - paused

    def _silence(self) -> float:
        if self._last_activity is None:
            return 0.0
        return max(0.0, self._clock_now() - self._last_activity)
