"""Deterministic interview scorecard helpers.

Mirrors the reference project's Inspector idea: the LLM judges each competency
with evidence, while code computes the overall score from explicit weights.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

from app.service.interview.behavior import BehaviorSummary
from app.service.interview.state import STARScore

Recommendation = Literal["strong_hire", "hire", "lean_hire", "no_hire", "strong_no_hire"]


class CompetencyScore(BaseModel):
    """Score for one interview competency, grounded in evidence."""

    name: str = Field(min_length=1, max_length=80)
    score: float = Field(ge=0.0, le=5.0)
    weight: float = Field(ge=0.0, le=1.0)
    rationale: str = ""
    evidence: str = ""


class InterviewScorecard(BaseModel):
    """Final scorecard returned by the Inspector-style evaluator."""

    overall_score: float = Field(ge=0.0, le=5.0)
    recommendation: Recommendation
    headline: str = ""
    summary: str = ""
    competencies: list[CompetencyScore] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    concerns: list[str] = Field(default_factory=list)
    red_flags: list[str] = Field(default_factory=list)
    next_steps: str = ""


DEFAULT_COMPETENCY_WEIGHTS: dict[str, float] = {
    "CV-JD Fit": 0.30,
    "Technical Depth": 0.25,
    "STAR Clarity": 0.20,
    "Communication": 0.15,
    "Professional Presence": 0.10,
}


def compute_weighted_overall(competencies: list[CompetencyScore]) -> float:
    """Compute the weighted score on a 0-5 scale."""
    if not competencies:
        return 0.0

    total_weight = sum(item.weight for item in competencies)
    if total_weight > 0:
        return round(sum(item.score * item.weight for item in competencies) / total_weight, 1)
    return round(sum(item.score for item in competencies) / len(competencies), 1)


def recommendation_for_score(score: float, red_flags: list[str] | None = None) -> Recommendation:
    """Map final score to the same recommendation bands as the reference project."""
    has_serious_red_flags = bool(red_flags)
    adjusted = min(score, 2.7) if has_serious_red_flags and score >= 2.8 else score
    if adjusted >= 4.3:
        return "strong_hire"
    if adjusted >= 3.5:
        return "hire"
    if adjusted >= 2.8:
        return "lean_hire"
    if adjusted >= 1.8:
        return "no_hire"
    return "strong_no_hire"


def score_to_confidence(score: float) -> float:
    """Convert 0-5 score to 0-100 percentage."""
    return round(max(0.0, min(100.0, (score / 5.0) * 100.0)), 1)


def build_scorecard(
    competencies: list[CompetencyScore],
    *,
    headline: str = "",
    summary: str = "",
    strengths: list[str] | None = None,
    concerns: list[str] | None = None,
    red_flags: list[str] | None = None,
    next_steps: str = "",
    recommendation: Recommendation | None = None,
) -> InterviewScorecard:
    """Normalize a scorecard and compute deterministic overall/recommendation."""
    overall = compute_weighted_overall(competencies)
    final_red_flags = list(red_flags or [])
    return InterviewScorecard(
        overall_score=overall,
        recommendation=recommendation or recommendation_for_score(overall, final_red_flags),
        headline=headline,
        summary=summary,
        competencies=competencies,
        strengths=list(strengths or []),
        concerns=list(concerns or []),
        red_flags=final_red_flags,
        next_steps=next_steps,
    )


def fallback_scorecard(
    *,
    star_scores: list[STARScore],
    behavior_summary: BehaviorSummary,
    transcript_turn_count: int,
) -> InterviewScorecard:
    """Deterministic fallback when the LLM scorecard cannot be parsed."""
    avg_star_10 = 0.0
    if star_scores:
        avg_star_10 = sum(item.overall_score for item in star_scores) / len(star_scores)

    has_answer_evidence = bool(star_scores)
    star_5 = max(0.0, min(5.0, avg_star_10 / 2.0)) if has_answer_evidence else 0.0
    communication = 3.0 if transcript_turn_count >= 4 else (1.5 if transcript_turn_count > 0 else 0.0)
    presence = max(0.0, min(5.0, behavior_summary.score / 20.0)) if transcript_turn_count > 0 else 0.0

    competencies = [
        CompetencyScore(
            name="CV-JD Fit",
            score=star_5,
            weight=DEFAULT_COMPETENCY_WEIGHTS["CV-JD Fit"],
            rationale="Ước lượng từ câu trả lời trong phiên phỏng vấn khi chưa có scorecard LLM.",
            evidence="Transcript phiên phỏng vấn.",
        ),
        CompetencyScore(
            name="Technical Depth",
            score=star_5,
            weight=DEFAULT_COMPETENCY_WEIGHTS["Technical Depth"],
            rationale="Ước lượng từ độ cụ thể của các câu trả lời đã được STAR-score.",
            evidence="Các câu trả lời ứng viên đã cung cấp.",
        ),
        CompetencyScore(
            name="STAR Clarity",
            score=star_5,
            weight=DEFAULT_COMPETENCY_WEIGHTS["STAR Clarity"],
            rationale="Quy đổi từ điểm STAR trung bình.",
            evidence=f"STAR trung bình {avg_star_10:.1f}/10.",
        ),
        CompetencyScore(
            name="Communication",
            score=communication,
            weight=DEFAULT_COMPETENCY_WEIGHTS["Communication"],
            rationale="Ước lượng từ số lượt hội thoại và khả năng duy trì trả lời.",
            evidence=f"{transcript_turn_count} lượt hội thoại được ghi nhận.",
        ),
        CompetencyScore(
            name="Professional Presence",
            score=presence,
            weight=DEFAULT_COMPETENCY_WEIGHTS["Professional Presence"],
            rationale="Quy đổi từ behavioral score.",
            evidence=f"Behavior score {behavior_summary.score:.1f}/100.",
        ),
    ]
    return build_scorecard(
        competencies,
        headline="Scorecard fallback được tạo từ STAR và tín hiệu hành vi.",
        summary="Hệ thống chưa đọc được scorecard LLM hợp lệ nên dùng công thức dự phòng có thể audit.",
        strengths=[],
        concerns=["Cần chạy lại Inspector LLM để có rationale/evidence chi tiết hơn."],
        red_flags=[],
        next_steps="Review transcript thủ công nếu cần quyết định tuyển dụng.",
    )
