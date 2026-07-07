from app.service.interview.behavior import normalise_behavior_event, summarize_behavior


def test_browser_integrity_events_are_scored_as_concerns() -> None:
    summary = summarize_behavior(
        [
            {"kind": "camera_ready", "severity": "low", "confidence": 0.9},
            {"kind": "tab_switch", "severity": "high", "confidence": 0.9, "detail": "Away for 8s."},
            {"kind": "secondary_monitor", "severity": "high", "confidence": 0.8},
        ]
    )

    kinds = {obs.kind for obs in summary.observations}
    assert {"tab_switch", "secondary_monitor", "camera_ready"}.issubset(kinds)
    assert summary.score < 86.0
    assert any(obs.category == "integrity" and obs.sentiment == "concern" for obs in summary.observations)


def test_unknown_behavior_event_is_still_normalised() -> None:
    event = normalise_behavior_event({"kind": "custom_signal", "severity": "low"})

    assert event is not None
    assert event.label == "custom signal"
