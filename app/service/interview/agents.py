"""Interview agent nodes — async functions driven by InterviewPipeline.

Three logical roles:
    - ``question_node``: pick the next interview question from CV + JD context.
    - ``evaluate_node``: STAR-score the candidate's most recent answer (json_mode).
    - ``wrap_up_node``: produce the final holistic assessment.

All prompts are in Vietnamese. Output is parsed from JSON for evaluate_node
and wrap_up_node. question_node returns plain text for the LLM chat stream.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.interview.behavior import BehaviorSummary
from app.service.interview.scoring import (
    DEFAULT_COMPETENCY_WEIGHTS,
    CompetencyScore,
    InterviewScorecard,
    build_scorecard,
    fallback_scorecard,
)
from app.service.interview.state import InterviewState, STARScore

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------

_QUESTION_SYSTEM = """Bạn là chuyên gia phỏng vấn tuyển dụng người Việt.
Nhiệm vụ: Đề xuất CÂU HỎI TIẾP THEO phù hợp nhất để hỏi ứng viên.
- Dựa trên CV, JD, và lịch sử hội thoại.
- Không lặp lại câu hỏi đã hỏi.
- Ưu tiên câu hỏi STAR (Tình huống, Nhiệm vụ, Hành động, Kết quả).
- Chỉ trả về MỘT câu hỏi ngắn gọn, không giải thích thêm."""

_EVALUATE_SYSTEM = """Bạn là chuyên gia đánh giá phỏng vấn.
Đánh giá câu trả lời của ứng viên theo phương pháp STAR.
Trả về JSON hợp lệ với schema sau (không thêm gì khác):
{
  "situation_score": <0-10>,
  "task_score": <0-10>,
  "action_score": <0-10>,
  "result_score": <0-10>,
  "overall_score": <0-10>,
  "feedback": "<nhận xét ngắn 1-2 câu tiếng Việt>",
  "follow_up_triggered": <true|false>
}"""

_WRAP_UP_SYSTEM = """Bạn là chuyên gia phỏng vấn tuyển dụng.
Tổng kết phiên phỏng vấn dựa trên toàn bộ transcript và các điểm STAR.
Trả về JSON hợp lệ với schema sau (không thêm gì khác):
{
  "overall_score": <0-10, trung bình có trọng số>,
  "strengths": ["<điểm mạnh 1>", "<điểm mạnh 2>", ...],
  "improvements": ["<cần cải thiện 1>", "<cần cải thiện 2>", ...],
  "final_feedback": "<nhận xét tổng thể 2-3 câu tiếng Việt, chuyên nghiệp>"
}"""

_SCORECARD_SYSTEM = """Bạn là Inspector Agent chấm điểm phỏng vấn tuyển dụng.
Bạn PHẢI chấm từng năng lực dựa trên evidence trong transcript/CV/JD; không bịa thông tin.
Thang điểm mỗi năng lực: 0.0-5.0
- 5 = exceptional, vượt yêu cầu rõ ràng
- 4 = strong, đáp ứng tốt
- 3 = baseline, đạt mức chấp nhận được
- 2 = below, còn thiếu đáng kể
- 1 = weak, rất yếu
- 0 = no evidence observed

Trả về JSON hợp lệ, không markdown:
{
  "competencies": [
    {
      "name": "CV-JD Fit",
      "score": <0-5>,
      "weight": 0.30,
      "rationale": "<1-2 câu giải thích dựa trên evidence>",
      "evidence": "<trích dẫn hoặc tóm tắt evidence từ transcript/CV/JD>"
    }
  ],
  "headline": "<một câu kết luận ngắn>",
  "summary": "<tóm tắt 3-5 câu cho HR>",
  "strengths": ["<điểm mạnh>"],
  "concerns": ["<điểm cần lưu ý>"],
  "red_flags": ["<red flag nghiêm trọng nếu có>"],
  "next_steps": "<đề xuất bước tiếp theo>"
}

Các competency bắt buộc và weight:
- CV-JD Fit: 0.30
- Technical Depth: 0.25
- STAR Clarity: 0.20
- Communication: 0.15
- Professional Presence: 0.10
Không tự tính overall_score; hệ thống sẽ tính bằng weighted average."""


_QUESTION_SYSTEM = """Bạn là Senior Technical Recruiter kiêm Interview Coach, phỏng vấn bằng tiếng Việt.
Mục tiêu của bạn là chọn đúng CÂU HỎI TIẾP THEO để kiểm chứng CV/JD, không trò chuyện lan man.

Nguyên tắc bắt buộc:
- Chỉ hỏi MỘT câu tại một thời điểm.
- Bám sát CV, JD, interview plan và lịch sử hội thoại.
- Không hỏi lại nội dung ứng viên đã trả lời rõ.
- Ưu tiên STAR: Situation, Task, Action, Result.
- Nếu câu trước còn mơ hồ, hỏi follow-up để lấy evidence cụ thể: phạm vi, vai trò cá nhân, quyết định, trade-off, kết quả đo được.
- Nếu thiếu JD, đánh giá theo mức phù hợp với vai trò mục tiêu suy ra từ CV.
- Không tiết lộ điểm số, tiêu chí nội bộ hoặc kết luận tuyển dụng trong lúc hỏi.

Output: chỉ trả về đúng một câu hỏi tiếng Việt, tự nhiên, chuyên nghiệp, tối đa 35 từ."""

_EVALUATE_SYSTEM = """Bạn là Interview Evaluator chuyên chấm câu trả lời theo khung STAR.
Chỉ đánh giá dựa trên evidence có trong câu hỏi và câu trả lời; không suy diễn, không bịa thành tích.

=== RUBRIC ĐÁNH GIÁ PHỎNG VẤN — STAR FRAMEWORK ===

SITUATION (0–10): Bối cảnh và vấn đề
  9–10: Bối cảnh rất rõ — có business context, phạm vi cụ thể, timeline, vấn đề cốt lõi được nêu rõ
  7–8 : Bối cảnh đủ hiểu, có phạm vi chung nhưng thiếu một số chi tiết
  5–6 : Có bối cảnh nhưng mơ hồ về quy mô hoặc tầm quan trọng của vấn đề
  3–4 : Rất mơ hồ, người nghe phải tự đoán context
  0–2 : Hầu như không có situation rõ ràng hoặc không liên quan câu hỏi

TASK (0–10): Trách nhiệm cá nhân
  9–10: Vai trò cá nhân rõ ràng, phân biệt được với team, có scope và ownership cụ thể
  7–8 : Vai trò cá nhân rõ, đôi khi dùng "chúng tôi" nhưng đóng góp cá nhân vẫn nhận diện được
  5–6 : Đề cập vai trò nhưng chủ yếu mô tả team, khó biết phần trách nhiệm riêng
  3–4 : Hầu hết dùng "team làm", không phân biệt được đóng góp cá nhân
  0–2 : Không đề cập đến nhiệm vụ cá nhân; nói chung chung hoặc né trả lời

ACTION (0–10): Hành động cụ thể
  9–10: Các bước rõ ràng, có quyết định cá nhân, trade-off, lý do chọn giải pháp, cách triển khai
  7–8 : Hành động rõ, có quyết định cá nhân nhưng thiếu lý do hoặc trade-off
  5–6 : Hành động được mô tả chung ("tôi đã implement feature X") không có chi tiết
  3–4 : Chỉ nói "làm X" mà không có bước nào cụ thể, không có sự lựa chọn cá nhân
  0–2 : Không có action cụ thể hoặc chỉ lặp lại task

RESULT (0–10): Kết quả và tác động
  9–10: Kết quả có số liệu cụ thể, tác động business rõ (performance, UX, doanh thu), có bài học rút ra
  7–8 : Kết quả rõ, có impact nhưng thiếu số liệu định lượng
  5–6 : Kết quả đề cập nhưng chung chung ("dự án thành công", "khách hàng hài lòng")
  3–4 : Kết quả mơ hồ hoặc không liên quan đến hành động
  0–2 : Không có kết quả hoặc kết quả không đo lường được

OVERALL (0–10): Tổng hợp — chất lượng evidence, độ liên quan vị trí và độ thuyết phục tổng thể.

follow_up_triggered = true nếu: thiếu số liệu kết quả, không rõ vai trò cá nhân, né câu hỏi, hoặc STAR score trung bình < 6.

Trả về JSON hợp lệ, không markdown:
{
  "situation_score": <0-10>,
  "task_score": <0-10>,
  "action_score": <0-10>,
  "result_score": <0-10>,
  "overall_score": <0-10>,
  "feedback": "<1-2 câu tiếng Việt, nêu rõ dimension mạnh nhất và điểm yếu cần cải thiện>",
  "follow_up_triggered": <true|false>
}"""

_WRAP_UP_SYSTEM = """Bạn là Lead Interviewer tổng kết phiên phỏng vấn CV/JD.
Tổng kết phải công bằng, dựa trên transcript và STAR score; không thêm thông tin ngoài evidence.

=== RUBRIC TỔNG KẾT PHỎNG VẤN ===

Điểm mạnh (strengths) — chỉ ghi nếu có evidence rõ:
  ✓ STAR rõ ràng: Situation/Task/Action/Result đều được nêu cụ thể ở ít nhất 1 câu
  ✓ Technical depth: có trade-off, quyết định kỹ thuật, hoặc số liệu kết quả
  ✓ Communication: mạch lạc, trả lời đúng trọng tâm, tự làm rõ giả định
  ✓ CV-JD fit: kinh nghiệm/kỹ năng khớp với yêu cầu vị trí
  ✓ Initiative: chủ động chia sẻ bài học, cải tiến, hoặc ý tưởng cải thiện

Điểm cần cải thiện (improvements) — viết dạng coaching/actionable, không chỉ trích:
  ⚠ Nếu STAR thiếu số liệu: "Lần sau nên chuẩn bị 1-2 con số cụ thể cho mỗi dự án nêu."
  ⚠ Nếu vai trò cá nhân mờ: "Hãy phân biệt rõ 'team làm' và 'tôi cụ thể làm gì'."
  ⚠ Nếu action thiếu depth: "Giải thích tại sao chọn giải pháp đó thay vì lý do khác."
  ⚠ Nếu kết quả chung chung: "Cố gắng đo lường impact bằng số: %, thời gian, người dùng."

Quy tắc:
- Chỉ nêu điểm mạnh có evidence từ transcript; không khen chung chung.
- Viết improvements dạng "Làm X để đạt Y", không phán xét nhân cách.
- Nếu < 3 lượt hỏi, ghi rõ "Đánh giá hạn chế do phiên ngắn" trong final_feedback.

Trả về JSON hợp lệ, không markdown:
{
  "overall_score": <0-10>,
  "strengths": ["<điểm mạnh có evidence cụ thể>"],
  "improvements": ["<đề xuất cải thiện actionable>"],
  "final_feedback": "<2-3 câu tiếng Việt, chuyên nghiệp, phù hợp đưa vào report HR>"
}"""

_SCORECARD_SYSTEM = """Bạn là Inspector Agent chấm điểm phỏng vấn tuyển dụng theo CV/JD.
Bạn PHẢI chấm từng năng lực dựa trên evidence trong transcript, CV và JD. Không bịa thông tin, không thưởng điểm cho claim không được ứng viên chứng minh.

Thang điểm từng năng lực: 0.0-5.0
- 5.0: exceptional, evidence rất mạnh, vượt yêu cầu rõ ràng.
- 4.0: strong, đáp ứng tốt, có ví dụ cụ thể và kết quả rõ.
- 3.0: baseline, đạt mức chấp nhận được nhưng chưa nổi bật.
- 2.0: below, thiếu bằng chứng hoặc thiếu chiều sâu đáng kể.
- 1.0: weak, trả lời mơ hồ, né trọng tâm.
- 0.0: no evidence observed.

Competency bắt buộc:
- CV-JD Fit, weight 0.30: mức khớp giữa kinh nghiệm/kỹ năng CV, câu trả lời và yêu cầu vị trí.
- Technical Depth, weight 0.25: chiều sâu chuyên môn, trade-off, quyết định kỹ thuật, tác động thực tế.
- STAR Clarity, weight 0.20: cấu trúc Situation/Task/Action/Result, vai trò cá nhân, kết quả.
- Communication, weight 0.15: mạch lạc, đúng trọng tâm, biết làm rõ giả định.
- Professional Presence, weight 0.10: tác phong, sự tập trung, tín hiệu camera/audio/hành vi; chỉ dùng như yếu tố phụ.

Quy tắc red flag:
- Chỉ ghi red flag nếu có evidence nghiêm trọng: gian lận rõ, nhiều người hỗ trợ, rời tab kéo dài, trả lời mâu thuẫn lớn với CV.
- Tín hiệu hành vi không được dùng như chẩn đoán tâm lý hoặc kết luận tự động.

Trả về JSON hợp lệ, không markdown:
{
  "competencies": [
    {
      "name": "CV-JD Fit",
      "score": <0-5>,
      "weight": 0.30,
      "rationale": "<1-2 câu giải thích dựa trên evidence>",
      "evidence": "<trích dẫn/tóm tắt evidence từ transcript/CV/JD>"
    }
  ],
  "headline": "<một câu kết luận ngắn>",
  "summary": "<3-5 câu cho HR/reviewer>",
  "strengths": ["<điểm mạnh có evidence>"],
  "concerns": ["<điểm cần lưu ý hoặc thiếu evidence>"],
  "red_flags": ["<red flag nghiêm trọng nếu có>"],
  "next_steps": "<đề xuất bước tiếp theo: pass/follow-up/deep-dive/reject review>"
}

Không tự tính overall_score; hệ thống sẽ tính weighted average."""


# ---------------------------------------------------------------------------
# Agent nodes
# ---------------------------------------------------------------------------


async def question_node(state: InterviewState, llm: LLMConnector) -> dict[str, Any]:
    """Generate the next interview question given current state.

    Returns a dict with ``current_question`` key. The pipeline can use this
    to inject the question into the chat_history before calling the LLM stream.
    """
    cv_snippet = json.dumps(state.cv_data, ensure_ascii=False)[:600]
    jd_snippet = json.dumps(state.jd_data, ensure_ascii=False)[:400]

    history_lines = [
        f"{'Phỏng vấn viên' if t.role == 'interviewer' else 'Ứng viên'}: {t.content}"
        for t in state.turns[-10:]  # last 10 turns for context
    ]
    history_text = "\n".join(history_lines)

    prompt = f"""## CV ứng viên (tóm tắt)
{cv_snippet}

## Mô tả vị trí
{jd_snippet}

## Lịch sử hội thoại gần đây
{history_text if history_text else "(Chưa có — đây là câu hỏi đầu tiên)"}

## Vị trí ứng tuyển: {state.job_title}

Đề xuất câu hỏi phỏng vấn tiếp theo:"""

    try:
        question = await llm.generate(
            prompt,
            system=_QUESTION_SYSTEM,
            use_cloud=llm.has_cloud,
        )
        return {"current_question": question.strip()}
    except Exception as exc:
        logger.error("[question_node] Failed: %s", exc)
        return {"current_question": "Bạn có thể kể về kinh nghiệm làm việc của mình không?"}


async def evaluate_node(state: InterviewState, llm: LLMConnector) -> dict[str, Any]:
    """STAR-score the candidate's most recent answer.

    Calls the LLM with ``json_mode=True`` and parses the structured output
    into a ``STARScore`` that is appended to ``state.star_scores``.
    """
    if not state.latest_transcript:
        return {}

    # Find the most recent interviewer question
    last_question = state.current_question
    if not last_question:
        interviewer_turns = [t for t in state.turns if t.role == "interviewer"]
        if interviewer_turns:
            last_question = interviewer_turns[-1].content

    prompt = f"""Câu hỏi phỏng vấn: {last_question}

Câu trả lời của ứng viên: {state.latest_transcript}

Vị trí ứng tuyển: {state.job_title}

Đánh giá theo STAR:"""

    try:
        raw = await llm.generate(
            prompt,
            system=_EVALUATE_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )

        # Strip markdown code fences if present
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
            raw = raw.rstrip("`").strip()

        data = json.loads(raw)
        score = STARScore(
            answer_index=len(state.star_scores),
            question=last_question,
            answer_transcript=state.latest_transcript,
            situation_score=float(data.get("situation_score", 0)),
            task_score=float(data.get("task_score", 0)),
            action_score=float(data.get("action_score", 0)),
            result_score=float(data.get("result_score", 0)),
            overall_score=float(data.get("overall_score", 0)),
            feedback=str(data.get("feedback", "")),
            follow_up_triggered=bool(data.get("follow_up_triggered", False)),
        )
        return {"star_scores": [score]}

    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("[evaluate_node] JSON parse failed: %s — raw=%r", exc, raw[:200])
        return {}
    except Exception as exc:
        logger.error("[evaluate_node] Failed: %s", exc)
        return {}


async def wrap_up_node(state: InterviewState, llm: LLMConnector) -> dict[str, Any]:
    """Produce the final holistic assessment for the session.

    Aggregates all STAR scores and the full transcript to generate an
    overall score, strengths, areas for improvement, and final feedback.
    """
    transcript_text = "\n".join(
        f"{'Phỏng vấn viên' if t.role == 'interviewer' else 'Ứng viên'}: {t.content}"
        for t in state.turns
    )

    star_summary = ""
    if state.star_scores:
        scores_text = "\n".join(
            f"- Câu {s.answer_index + 1}: S={s.situation_score} T={s.task_score} "
            f"A={s.action_score} R={s.result_score} → Overall={s.overall_score} | {s.feedback}"
            for s in state.star_scores
        )
        star_summary = f"\n## Điểm STAR từng câu\n{scores_text}"

    duration_min = round((state.get_remaining_seconds() - state.duration_minutes * 60) * -1 / 60, 1)

    prompt = f"""## Vị trí: {state.job_title}
## Thời lượng phỏng vấn: {duration_min} phút
{star_summary}

## Toàn bộ transcript
{transcript_text[:3000]}

Tổng kết phiên phỏng vấn:"""

    if state.interview_plan:
        prompt += (
            "\n\n## Interview plan / evaluation brief\n"
            f"{json.dumps(state.interview_plan, ensure_ascii=False)[:2500]}"
        )

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=_WRAP_UP_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )

        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:])
            raw = raw.rstrip("`").strip()

        data = json.loads(raw)
        return {
            "overall_score": float(data.get("overall_score", 0.0)),
            "strengths": list(data.get("strengths", [])),
            "improvements": list(data.get("improvements", [])),
            "final_feedback": str(data.get("final_feedback", "")),
            "session_complete": True,
        }

    except (json.JSONDecodeError, KeyError, ValueError) as exc:
        logger.error("[wrap_up_node] JSON parse failed: %s — raw=%r", exc, raw[:200])
        return {"session_complete": True}
    except Exception as exc:
        logger.error("[wrap_up_node] Failed: %s", exc)
        return {"session_complete": True}


async def scorecard_node(
    state: InterviewState,
    llm: LLMConnector,
    behavior_summary: BehaviorSummary,
) -> InterviewScorecard:
    """Inspector-style final scoring: LLM scores competencies, code computes overall."""
    transcript_text = "\n".join(
        f"{'Phỏng vấn viên' if t.role == 'interviewer' else 'Ứng viên'}: {t.content}"
        for t in state.turns
    )
    star_summary = "\n".join(
        f"- Câu {s.answer_index + 1}: overall={s.overall_score}/10; "
        f"S={s.situation_score}, T={s.task_score}, A={s.action_score}, R={s.result_score}; "
        f"feedback={s.feedback}"
        for s in state.star_scores
    )
    behavior_summary_text = "\n".join(
        f"- {obs.label}: {obs.severity}, {obs.count} lần, {obs.detail}"
        for obs in behavior_summary.observations
    )

    prompt = f"""## Vị trí ứng tuyển
{state.job_title}

## CV ứng viên
{json.dumps(state.cv_data, ensure_ascii=False)[:2500]}

## JD / yêu cầu vị trí
{json.dumps(state.jd_data, ensure_ascii=False)[:2000] if state.jd_data else "(Không có JD chi tiết)"}

## Điểm STAR từng câu
{star_summary if star_summary else "(Chưa có điểm STAR chi tiết)"}

## Behavioral / integrity observations
Behavior score: {behavior_summary.score}/100
{behavior_summary_text if behavior_summary_text else "(Không có tín hiệu hành vi đáng chú ý)"}

## Transcript
{transcript_text[:6000] if transcript_text else "(Không có transcript)"}

Hãy chấm scorecard theo đúng schema."""

    if state.interview_plan:
        prompt += (
            "\n\n## Interview plan / evaluation brief\n"
            f"{json.dumps(state.interview_plan, ensure_ascii=False)[:2500]}"
        )

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=_SCORECARD_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:]).rstrip("`").strip()

        data = json.loads(raw)
        competencies = _parse_competencies(data.get("competencies", []))
        if len(competencies) < 3:
            raise ValueError("scorecard must contain at least 3 competencies")

        return build_scorecard(
            competencies,
            headline=str(data.get("headline", "")),
            summary=str(data.get("summary", "")),
            strengths=[str(item) for item in data.get("strengths", []) if str(item).strip()],
            concerns=[str(item) for item in data.get("concerns", []) if str(item).strip()],
            red_flags=[str(item) for item in data.get("red_flags", []) if str(item).strip()],
            next_steps=str(data.get("next_steps", "")),
        )
    except Exception as exc:
        logger.error("[scorecard_node] Failed: %s — raw=%r", exc, raw[:300])
        return fallback_scorecard(
            star_scores=state.star_scores,
            behavior_summary=behavior_summary,
            transcript_turn_count=len(state.turns),
        )


def _parse_competencies(raw_items: Any) -> list[CompetencyScore]:
    if not isinstance(raw_items, list):
        return []

    competencies: list[CompetencyScore] = []
    for item in raw_items:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        default_weight = DEFAULT_COMPETENCY_WEIGHTS.get(name, 0.0)
        try:
            competencies.append(
                CompetencyScore(
                    name=name,
                    score=float(item.get("score", 0.0)),
                    weight=float(item.get("weight", default_weight)),
                    rationale=str(item.get("rationale", "")),
                    evidence=str(item.get("evidence", "")),
                )
            )
        except Exception as exc:
            logger.debug("[scorecard_node] Skipping malformed competency: %s", exc)
    return _ensure_required_weights(competencies)


def _ensure_required_weights(competencies: list[CompetencyScore]) -> list[CompetencyScore]:
    """Prefer configured weights for known competencies to keep scoring auditable."""
    output: list[CompetencyScore] = []
    seen = set()
    by_name = {item.name: item for item in competencies}
    for name, weight in DEFAULT_COMPETENCY_WEIGHTS.items():
        item = by_name.get(name)
        if item is None:
            continue
        output.append(item.model_copy(update={"weight": weight}))
        seen.add(name)

    for item in competencies:
        if item.name in seen:
            continue
        output.append(item)
    return output
