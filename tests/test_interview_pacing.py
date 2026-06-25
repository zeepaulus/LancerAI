from app.service.interview.pacing import PacingClock, PacingSignal, is_terminal, signal_instruction


class MutableClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


def test_pacing_clock_wraps_and_force_ends() -> None:
    now = MutableClock()
    clock = PacingClock(
        duration_minutes=5,
        grace_minutes=2,
        dead_air_prompt_sec=999,
        max_silence_end_min=99,
        wrap_soon_minutes=1,
        now=now,
    )
    clock.start()

    assert clock.signal() == PacingSignal.ON_TRACK

    now.advance(4 * 60)
    assert clock.signal() == PacingSignal.WRAP_SOON
    assert signal_instruction(PacingSignal.WRAP_SOON)

    now.advance(60)
    assert clock.signal() == PacingSignal.WRAP_UP_NOW
    assert not is_terminal(PacingSignal.WRAP_UP_NOW)

    now.advance(2 * 60)
    assert clock.signal() == PacingSignal.FORCE_END
    assert is_terminal(PacingSignal.FORCE_END)


def test_pacing_clock_tracks_dead_air_and_activity() -> None:
    now = MutableClock()
    clock = PacingClock(
        duration_minutes=10,
        grace_minutes=1,
        dead_air_prompt_sec=30,
        max_silence_end_min=2,
        wrap_soon_minutes=1,
        now=now,
    )
    clock.start()

    now.advance(31)
    assert clock.signal() == PacingSignal.DEAD_AIR

    clock.note_activity()
    assert clock.signal() == PacingSignal.ON_TRACK

    now.advance(2 * 60)
    assert clock.signal() == PacingSignal.ABANDON
    assert is_terminal(PacingSignal.ABANDON)
