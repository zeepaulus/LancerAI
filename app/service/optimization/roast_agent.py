"""Roast agent.

Identifies weak points in the CV with a recruiter's eye: vague claims, missing
metrics, weak verbs, generic statements.

Strategy:
    - Build a structured prompt with the raw CV data + industry benchmarks.
    - Use ``json_mode=True`` so the LLM returns a parseable list of RoastIssue.
    - Set ``inquiry_needed`` when any issue requires user clarification.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState, RoastIssue

logger = logging.getLogger(__name__)

_ROAST_SYSTEM = """Bạn là chuyên gia tư vấn CV và tuyển dụng người Việt.
Nhiệm vụ: Phân tích CV và chỉ ra các điểm yếu dưới góc nhìn của recruiter / ATS.

Trả về JSON hợp lệ (không thêm markdown):
{
  "issues": [
    {
      "field": "experience[0].key_impacts",
      "severity": "critical|high|medium|low",
      "issue_type": "vague_claim|buzzword|missing_metric|weak_verb|generic_statement",
      "original_text": "Đoạn văn bản gốc cụ thể bị lỗi",
      "explanation": "Giải thích tại sao đây là vấn đề trong bối cảnh ATS/recruiter",
      "needs_clarification": false
    }
  ],
  "summary": "Nhận xét tổng thể 2-3 câu về CV"
}

Quy tắc:
- Chỉ phê bình những điểm THỰC SỰ có vấn đề — không bịa ra lỗi.
- Ưu tiên phát hiện: thiếu số liệu cụ thể, động từ yếu (phụ trách, tham gia), tuyên bố mơ hồ.
- Tối đa 10 issue, tập trung vào critical và high severity."""


async def roast_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Roast node.

    Analyses the CV against industry benchmarks and returns a list of
    ``RoastIssue`` records plus a plain-text summary.
    """
    raw_cv = state.get("raw_cv_data", {})
    benchmarks = state.get("industry_benchmarks", {})
    job_title = state.get("target_job_title", "")

    cv_text = json.dumps(raw_cv, ensure_ascii=False)[:4000]
    benchmark_text = json.dumps(benchmarks, ensure_ascii=False)[:1500]

    prompt = f"""## Vị trí ứng tuyển: {job_title}

## Benchmark ngành
{benchmark_text}

## CV ứng viên
{cv_text}

Phân tích điểm yếu của CV và trả về JSON:"""

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=_ROAST_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )
        raw = raw.strip()
        if raw.startswith("```"):
            raw = "\n".join(raw.split("\n")[1:]).rstrip("`").strip()

        data: dict[str, Any] = json.loads(raw)
        issues_raw: list[dict[str, Any]] = data.get("issues", [])
        summary: str = data.get("summary", "")

        roast_issues: list[RoastIssue] = []
        inquiry_needed = False
        for item in issues_raw:
            try:
                issue = RoastIssue(**item)
                roast_issues.append(issue)
                if issue.needs_clarification:
                    inquiry_needed = True
            except Exception as parse_exc:
                logger.debug("[roast_agent] Skipping malformed issue: %s", parse_exc)

        logger.info("[roast_agent] Found %d issues (inquiry_needed=%s)", len(roast_issues), inquiry_needed)
        return {
            "roast_issues": roast_issues,
            "roast_summary": summary,
            "inquiry_needed": inquiry_needed,
            "current_step": "roast_done",
        }

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("[roast_agent] JSON parse failed (%s) — raw=%r", exc, raw[:200])
        return {
            "roast_issues": [],
            "roast_summary": "",
            "inquiry_needed": False,
            "current_step": "roast_done",
        }
    except Exception as exc:
        logger.error("[roast_agent] Failed: %s", exc)
        return {
            "roast_issues": [],
            "roast_summary": "",
            "inquiry_needed": False,
            "error_message": str(exc),
            "current_step": "roast_done",
        }
