"""Rewrite agent.

Rewrites weak CV sections using the Google XYZ formula
(``Accomplished X, as measured by Y, by doing Z``).

Strategy:
    - Take the issues produced by ``roast_agent`` (and any user clarifications).
    - For each issue, ask the LLM to produce a concrete, grounded rewrite.
    - Never invent metrics — the rewrite must stay grounded in the original CV.
    - Return a list of ``RewrittenSection`` instances.
"""

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState, RewrittenSection, RoastIssue

logger = logging.getLogger(__name__)

_REWRITE_SYSTEM = """Bạn là chuyên gia viết CV người Việt, thành thạo công thức Google XYZ.
Công thức XYZ: "Accomplished [X], as measured by [Y], by doing [Z]"
Ví dụ: "Tăng tốc độ tải trang 40%, đo bằng Lighthouse score, bằng cách tối ưu hóa lazy loading và bundle splitting."

Nhiệm vụ: Viết lại các đoạn CV bị phê bình. Trả về JSON hợp lệ:
{
  "rewrites": [
    {
      "field": "experience[0].key_impacts[0]",
      "original": "Đoạn văn bản gốc",
      "rewritten": "Câu viết lại theo công thức XYZ",
      "formula_used": "xyz|star|car|direct",
      "improvement_score": 0.85
    }
  ]
}

Quy tắc NGHIÊM NGẶT:
- KHÔNG bịa đặt số liệu nếu CV gốc không có — dùng "đáng kể", "hiệu quả" thay thế.
- Giữ nguyên thông tin thực tế; chỉ cải thiện cách diễn đạt.
- improvement_score từ 0.0 đến 1.0 (0 = không cải thiện, 1 = hoàn hảo).
- Chỉ viết lại những issue có severity "critical" hoặc "high"."""


async def rewrite_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Rewrite node.

    Takes ``roast_issues`` from the previous node and uses the LLM to
    produce concrete ``RewrittenSection`` improvements.
    """
    roast_issues: list[RoastIssue] = state.get("roast_issues", [])
    raw_cv = state.get("raw_cv_data", {})

    if not roast_issues:
        logger.info("[rewrite_agent] No issues to rewrite — skipping")
        return {"rewritten_sections": [], "current_step": "rewrite_done"}

    # Filter to high/critical issues only (avoid over-rewriting)
    priority_issues = [
        issue for issue in roast_issues
        if issue.severity in ("critical", "high")
    ]
    if not priority_issues:
        priority_issues = roast_issues[:5]  # fallback: top 5 issues

    issues_text = json.dumps(
        [issue.model_dump() for issue in priority_issues],
        ensure_ascii=False,
    )
    cv_text = json.dumps(raw_cv, ensure_ascii=False)[:3000]

    prompt = f"""## CV gốc (để tham chiếu)
{cv_text}

## Các vấn đề cần viết lại
{issues_text}

Viết lại các đoạn trên theo công thức XYZ/STAR. Trả về JSON:"""

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=_REWRITE_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )
        from app.core.json_extractor import clean_and_parse_json
        data: dict[str, Any] = clean_and_parse_json(raw)
        rewrites_raw: list[dict[str, Any]] = data.get("rewrites", [])

        rewritten_sections: list[RewrittenSection] = []
        for item in rewrites_raw:
            if not isinstance(item, dict):
                logger.warning("[rewrite_agent] Skipping non-dict rewrite item: %s", item)
                continue
            try:
                # Normalize formula_used
                formula = str(item.get("formula_used", "")).lower()
                if "xyz" in formula:
                    item["formula_used"] = "xyz"
                elif "star" in formula:
                    item["formula_used"] = "star"
                elif "car" in formula:
                    item["formula_used"] = "car"
                elif "direct" in formula:
                    item["formula_used"] = "direct"
                else:
                    item["formula_used"] = "xyz"

                section = RewrittenSection(**item)
                rewritten_sections.append(section)
            except Exception as parse_exc:
                logger.warning("[rewrite_agent] Skipping malformed rewrite: %s. Item was: %s", parse_exc, item)

        logger.info("[rewrite_agent] Produced %d rewrites", len(rewritten_sections))
        return {
            "rewritten_sections": rewritten_sections,
            "current_step": "rewrite_done",
        }

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("[rewrite_agent] JSON parse failed (%s) — raw=%r", exc, raw[:200])
        return {"rewritten_sections": [], "current_step": "rewrite_done"}
    except Exception as exc:
        logger.error("[rewrite_agent] Failed: %s", exc)
        return {
            "rewritten_sections": [],
            "error_message": str(exc),
            "current_step": "rewrite_done",
        }
