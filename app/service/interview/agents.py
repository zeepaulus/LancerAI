"""Interview agent nodes — async functions driven by InterviewPipeline.

Three logical roles:
    - ``question_node``: pick the next interview question from CV + JD context.
    - ``evaluate_node``: STAR-score the candidate's most recent answer (json_mode).
    - ``wrap_up_node``: produce the final holistic assessment.

All prompts are in Vietnamese. Output is parsed from JSON for evaluate_node
and wrap_up_node. question_node returns plain text for the LLM chat stream.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
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
