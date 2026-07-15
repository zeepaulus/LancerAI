"""Behavioral signal catalog and scoring for interview sessions.

These signals are observations, not medical or psychological diagnoses. The
score should support coaching feedback and reviewer context, not automatic
candidate rejection.
"""

from __future__ import annotations

import time
from typing import Any

from pydantic import BaseModel, Field


class BehaviorEvent(BaseModel):
    """One client-side behavioral observation emitted during an interview."""

    kind: str
    category: str = "attention"
    label: str = ""
    severity: str = "info"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    detail: str = ""
    ts: float = Field(default_factory=time.time)


class BehaviorObservation(BaseModel):
    """Aggregated behavioral observation returned in the interview report."""

    kind: str
    label: str
    category: str
    sentiment: str = "neutral"
    severity: str = "info"
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    count: int = 1
    detail: str = ""
    suggestion: str = ""


class BehaviorSummary(BaseModel):
    """Session-level behavior assessment."""

    score: float = Field(default=100.0, ge=0.0, le=100.0)
    observations: list[BehaviorObservation] = Field(default_factory=list)


BEHAVIOR_CATALOG: dict[str, dict[str, str]] = {
    "camera_ready": {
        "label": "Camera hoạt động ổn định",
        "category": "presence",
        "sentiment": "positive",
        "suggestion": "Tiếp tục giữ khung hình rõ mặt và ánh sáng ổn định.",
    },
    "eye_contact_stable": {
        "label": "Nhìn thẳng vào màn hình/camera khá ổn định",
        "category": "confidence",
        "sentiment": "positive",
        "suggestion": "Duy trì ánh nhìn tự nhiên khi trình bày ý chính.",
    },
    "stable_posture": {
        "label": "Tư thế ổn định",
        "category": "confidence",
        "sentiment": "positive",
        "suggestion": "Giữ tư thế mở, hạn chế rung lắc không cần thiết.",
    },
    "face_not_visible": {
        "label": "Không thấy rõ khuôn mặt",
        "category": "presence",
        "sentiment": "concern",
        "suggestion": "Ngồi lại trong khung hình để người phỏng vấn thấy rõ biểu cảm.",
    },
    "face_off_center": {
        "label": "Thường xuyên lệch khỏi camera/màn hình",
        "category": "attention",
        "sentiment": "concern",
        "suggestion": "Đặt camera ngang tầm mắt và hạn chế nhìn sang nơi khác quá lâu.",
    },
    "restless_motion": {
        "label": "Di chuyển nhiều hoặc có dấu hiệu loay hoay",
        "category": "confidence",
        "sentiment": "concern",
        "suggestion": "Đặt tay ổn định, hít thở chậm trước khi trả lời câu khó.",
    },
    "poor_lighting": {
        "label": "Ánh sáng yếu",
        "category": "presence",
        "sentiment": "concern",
        "suggestion": "Tăng ánh sáng phía trước mặt để camera nhận diện tốt hơn.",
    },
    "multiple_faces": {
        "label": "Có nhiều khuôn mặt trong khung hình",
        "category": "integrity",
        "sentiment": "concern",
        "suggestion": "Đảm bảo chỉ có ứng viên xuất hiện trong khung hình phỏng vấn.",
    },
    "camera_unavailable": {
        "label": "Không dùng camera trong phiên",
        "category": "system",
        "sentiment": "neutral",
        "suggestion": "Phiên vẫn có thể đánh giá qua micro và transcript nếu âm thanh hoạt động ổn định.",
    },
    "camera_analysis_limited": {
        "label": "Trình duyệt không hỗ trợ nhận diện khuôn mặt",
        "category": "system",
        "sentiment": "neutral",
        "suggestion": "Báo cáo sẽ bỏ qua phần nhận diện khuôn mặt nếu trình duyệt không hỗ trợ.",
    },
}

BEHAVIOR_CATALOG.update(
    {
        "detection_unsupported": {
            "label": "Trình duyệt không hỗ trợ một số kiểm tra hành vi",
            "category": "system",
            "sentiment": "neutral",
            "suggestion": "Hãy xem đây là giới hạn kỹ thuật của trình duyệt khi đọc báo cáo.",
        },
        "tab_switch": {
            "label": "Rời khỏi tab hoặc cửa sổ phỏng vấn",
            "category": "integrity",
            "sentiment": "concern",
            "suggestion": "Giữ phòng phỏng vấn ở màn hình đang dùng trong suốt buổi phỏng vấn.",
        },
        "secondary_monitor": {
            "label": "Phát hiện màn hình phụ hoặc không gian hiển thị mở rộng",
            "category": "integrity",
            "sentiment": "concern",
            "suggestion": "Chỉ sử dụng một màn hình trong buổi phỏng vấn.",
        },
        "gaze_away": {
            "label": "Nhìn ra ngoài màn hình hoặc camera trong thời gian dài",
            "category": "attention",
            "sentiment": "concern",
            "suggestion": "Giữ ánh nhìn tự nhiên về phía màn hình và trả lời tập trung hơn.",
        },
        "phone_detected": {
            "label": "Có tín hiệu điện thoại trong khung hình",
            "category": "integrity",
            "sentiment": "concern",
            "suggestion": "Đặt điện thoại ra khỏi khu vực phỏng vấn nếu không cần thiết.",
        },
        "candidate_silence": {
            "label": "Im lặng quá lâu hoặc không phản hồi",
            "category": "attention",
            "sentiment": "concern",
            "suggestion": "Nên trả lời nhanh gọn hơn và hạn chế khoảng lặng kéo dài.",
        },
    }
)


_SEVERITY_PENALTY = {
    "info": 0.0,
    "low": 2.0,
    "medium": 6.0,
    "high": 12.0,
}

_POSITIVE_BONUS = {
    "info": 0.5,
    "low": 1.0,
    "medium": 2.0,
    "high": 3.0,
}


def normalise_behavior_event(raw: dict[str, Any]) -> BehaviorEvent | None:
    """Validate and enrich a raw client event."""
    if not isinstance(raw, dict):
        return None
    kind = str(raw.get("kind") or "").strip()
    if not kind:
        return None

    catalog = BEHAVIOR_CATALOG.get(kind, {})
    payload = {
        "kind": kind,
        "category": raw.get("category") or catalog.get("category", "attention"),
        "label": raw.get("label") or catalog.get("label", kind.replace("_", " ")),
        "severity": raw.get("severity") or "info",
        "confidence": raw.get("confidence", 0.5),
        "detail": raw.get("detail") or "",
        "ts": raw.get("ts") or time.time(),
    }
    try:
        return BehaviorEvent(**payload)
    except Exception:
        return None


def summarize_behavior(events: list[dict[str, Any] | BehaviorEvent]) -> BehaviorSummary:
    """Aggregate raw behavior events into report-ready observations and score."""
    grouped: dict[str, list[BehaviorEvent]] = {}
    for item in events:
        event = item if isinstance(item, BehaviorEvent) else normalise_behavior_event(item)
        if event is None:
            continue
        grouped.setdefault(event.kind, []).append(event)

    score = 86.0
    observations: list[BehaviorObservation] = []
    for kind, items in grouped.items():
        catalog = BEHAVIOR_CATALOG.get(kind, {})
        count = len(items)
        severity = _strongest_severity([event.severity for event in items])
        confidence = sum(event.confidence for event in items) / max(1, count)
        sentiment = catalog.get("sentiment", "neutral")
        if sentiment == "positive":
            score += min(6.0, _POSITIVE_BONUS.get(severity, 0.5) * count)
        elif sentiment == "concern":
            score -= min(28.0, _SEVERITY_PENALTY.get(severity, 3.0) * (1 + (count - 1) * 0.35))

        observations.append(
            BehaviorObservation(
                kind=kind,
                label=catalog.get("label", items[0].label),
                category=catalog.get("category", items[0].category),
                sentiment=sentiment,
                severity=severity,
                confidence=round(confidence, 2),
                count=count,
                detail=items[-1].detail,
                suggestion=catalog.get("suggestion", ""),
            )
        )

    observations.sort(key=lambda obs: (_sentiment_rank(obs.sentiment), _severity_rank(obs.severity), -obs.count))
    return BehaviorSummary(score=round(max(0.0, min(100.0, score)), 1), observations=observations)


def behavior_feedback_lines(summary: BehaviorSummary) -> tuple[list[str], list[str]]:
    """Split observations into report issue/suggestion lines."""
    issues: list[str] = []
    suggestions: list[str] = []
    for obs in summary.observations:
        if obs.sentiment != "concern":
            continue
        issues.append(f"{obs.label} ({obs.count} lần). {obs.detail}".strip())
        if obs.suggestion:
            suggestions.append(obs.suggestion)
    return issues, list(dict.fromkeys(suggestions))


def _strongest_severity(values: list[str]) -> str:
    return max(values or ["info"], key=_severity_rank)


def _severity_rank(value: str) -> int:
    return {"info": 0, "low": 1, "medium": 2, "high": 3}.get(value, 0)


def _sentiment_rank(value: str) -> int:
    return {"concern": 0, "neutral": 1, "positive": 2}.get(value, 1)
