from app.service.interview.behavior import BehaviorSummary
from app.service.interview.scoring import fallback_scorecard


def test_fallback_scorecard_does_not_reward_missing_answer_evidence() -> None:
    scorecard = fallback_scorecard(
        star_scores=[],
        behavior_summary=BehaviorSummary(score=100.0),
        transcript_turn_count=0,
    )

    assert scorecard.overall_score == 0.0
    assert scorecard.recommendation == "strong_no_hire"
