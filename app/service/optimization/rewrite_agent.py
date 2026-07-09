"""Rewrite agent.

Rewrites weak CV sections using the Google XYZ formula
(``Accomplished X, as measured by Y, by doing Z``).

Strategy:
    - Take the issues produced by ``roast_agent`` (and any user clarifications).
    - For each issue, ask the LLM to produce a concrete, grounded rewrite.
    - Never invent metrics — the rewrite must stay grounded in the original CV.
    - Return a list of ``RewrittenSection`` instances.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState, RewrittenSection, RoastIssue

logger = logging.getLogger(__name__)

_REWRITE_SYSTEM = """Bạn là chuyên gia viết CV người Việt, áp dụng quy chuẩn CV hiện đại cho thị trường tech Việt Nam và quốc tế.

=== RUBRIC VIẾT LẠI CV ===
Chọn công thức phù hợp theo loại issue:

Công thức XYZ (ưu tiên khi có số liệu):
  "Accomplished [X], as measured by [Y], by doing [Z]"
  VD: "Giảm thời gian load 40%, đo qua Lighthouse score, bằng cách tối ưu lazy loading và bundle splitting."

Công thức CAR (khi thiếu số liệu cụ thể):
  "Context: [bối cảnh] → Action: [hành động cá nhân] → Result: [kết quả/impact]"
  VD: "Trong dự án migration PostgreSQL → MongoDB; thiết kế lại schema và viết script chuyển đổi 50k records; đảm bảo zero downtime cho production."

Công thức STAR bullet (khi cần nhấn mạnh tình huống):
  "[Động từ mạnh] [hành động cụ thể] dẫn đến [kết quả], trong bối cảnh [tình huống]."

Công thức DIRECT (cho skills/summary ngắn):
  "[Động từ mạnh] + [đối tượng cụ thể] + [phạm vi/quy mô]."
  VD: "Triển khai CI/CD pipeline cho 3 microservices trên AWS ECS, giảm deployment time từ 45 phút xuống 8 phút."

=== TIÊU CHÍ CHẤM improvement_score ===
- 0.9–1.0: Có số liệu cụ thể + action verb mạnh + kết quả business rõ ràng
- 0.7–0.8: Có action verb mạnh + kết quả rõ nhưng thiếu số liệu chính xác
- 0.5–0.6: Rõ hơn gốc nhưng vẫn còn chung chung hoặc thiếu scope
- 0.3–0.4: Chỉ cải thiện nhẹ cách diễn đạt, không thêm được thông tin mới
- 0.0–0.2: Hầu như không cải thiện được do thiếu dữ liệu gốc

Nhiệm vụ: Viết lại các đoạn CV bị phê bình. Trả về JSON hợp lệ:
{
  "rewrites": [
    {
      "field": "experience[0].key_impacts[0]",
      "original": "Đoạn văn bản gốc",
      "rewritten": "Câu viết lại theo công thức phù hợp",
      "formula_used": "xyz|car|star|direct",
      "improvement_score": 0.85
    }
  ]
}

Quy tắc NGHIÊM NGẶT:
- KHÔNG bịa đặt hoặc ước lượng số liệu nếu CV gốc không có; chỉ mô tả impact định tính dựa trên evidence gốc.
- Giữ nguyên mọi thông tin thực tế; chỉ cải thiện cách diễn đạt và cấu trúc câu.
- Không viết lại các nhận xét nhỏ, hành chính hoặc học thuật không ảnh hưởng trực tiếp đến tuyển dụng IT.
- Không tạo rewrite cho GPA, thang điểm, địa chỉ trường, ngày sinh hoặc thông tin cá nhân phụ trừ khi issue là high/critical và có liên quan rõ tới target role.
- Bắt đầu câu bằng động từ hành động mạnh (Built, Designed, Led, Reduced, Optimized, Delivered...).
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
        logger.info("[rewrite_agent] No high-impact issues to rewrite — skipping")
        return {"rewritten_sections": [], "current_step": "rewrite_done"}

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
                if _has_new_numeric_claim(section.original, section.rewritten):
                    logger.info("[rewrite_agent] Skipping rewrite with unsupported numeric claim for %s", section.field)
                    continue
                rewritten_sections.append(section)
            except Exception as parse_exc:
                logger.warning("[rewrite_agent] Skipping malformed rewrite: %s. Item was: %s", parse_exc, item)

        logger.info("[rewrite_agent] Produced %d rewrites", len(rewritten_sections))
        return {
            "rewritten_sections": rewritten_sections,
            "current_step": "rewrite_done",
        }

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("[rewrite_agent] JSON parse failed (%s); raw_length=%d", exc, len(raw or ""))
        return {"rewritten_sections": [], "current_step": "rewrite_done"}
    except Exception as exc:
        logger.error("[rewrite_agent] Failed: %s", exc)
        return {
            "rewritten_sections": [],
            "error_message": str(exc),
            "current_step": "rewrite_done",
        }


def _numbers_in_text(value: str) -> set[str]:
    import re

    return set(re.findall(r"\d+(?:[.,]\d+)?\s*(?:%|x|k|m|ms|s|h|hours?|users?|requests?)?", value.lower()))


def _has_new_numeric_claim(original: str, rewritten: str) -> bool:
    """Return True when the rewrite introduces numbers absent from the source."""
    rewritten_numbers = _numbers_in_text(rewritten)
    if not rewritten_numbers:
        return False
    original_numbers = _numbers_in_text(original)
    return not rewritten_numbers.issubset(original_numbers)
