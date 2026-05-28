"""Audit agent.

Final compliance gate: verifies that rewrites are truthful, grounded, and not
exaggerated. Approved rewrites are merged into ``state.optimized_cv``;
rejections become ``AuditFlag`` entries for the user to inspect.

Strategy:
    - Compare each ``RewrittenSection`` against ``state.raw_cv_data``.
    - LLM verifies truthfulness and rates each rewrite as approved / needs_revision / rejected.
    - Build the merged ``optimized_cv`` blob with applied rewrites.
    - Compute ``overall_improvement_score`` from approved rewrites.
"""

from __future__ import annotations

import copy
import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import AuditFlag, CVOptimizationState, RewrittenSection

logger = logging.getLogger(__name__)

_AUDIT_SYSTEM = """Bạn là chuyên gia kiểm duyệt CV, đảm bảo tính trung thực và không thổi phồng.
Nhiệm vụ: Đánh giá từng nội dung viết lại — có trung thực và được hỗ trợ bởi CV gốc không?

Trả về JSON hợp lệ:
{
  "verdicts": [
    {
      "field": "experience[0].key_impacts[0]",
      "rewritten_text": "Nội dung đã viết lại",
      "original_text": "Nội dung gốc",
      "issue": "Lý do nếu không được duyệt (để trống nếu approved)",
      "verdict": "approved|needs_revision|rejected"
    }
  ]
}

Tiêu chí:
- "approved": Viết lại trung thực, rõ ràng hơn gốc, không bịa đặt.
- "needs_revision": Cải thiện nhẹ nhưng có chi tiết chưa rõ nguồn gốc.
- "rejected": Bịa đặt số liệu hoặc thành tích không có trong CV gốc."""


async def audit_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Audit node.

    Verifies each ``RewrittenSection`` for truthfulness against the raw CV,
    assembles the final ``optimized_cv``, and computes ``overall_improvement_score``.
    """
    rewritten_sections: list[RewrittenSection] = state.get("rewritten_sections", [])
    raw_cv = state.get("raw_cv_data", {})

    if not rewritten_sections:
        logger.info("[audit_agent] No rewrites to audit — passing through raw CV")
        return {
            "audit_flags": [],
            "audit_passed": True,
            "optimized_cv": raw_cv,
            "overall_improvement_score": 0.0,
            "pipeline_complete": True,
            "current_step": "audit_done",
        }

    rewrites_text = json.dumps(
        [s.model_dump() for s in rewritten_sections],
        ensure_ascii=False,
    )
    cv_text = json.dumps(raw_cv, ensure_ascii=False)[:3000]

    prompt = f"""## CV gốc
{cv_text}

## Các đoạn đã viết lại cần kiểm duyệt
{rewrites_text}

Kiểm tra tính trung thực và trả về JSON:"""

    raw = ""
    audit_flags: list[AuditFlag] = []
    approved_sections: list[RewrittenSection] = []

    try:
        raw = await llm.generate(
            prompt,
            system=_AUDIT_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )
        from app.core.json_extractor import clean_and_parse_json
        data: dict[str, Any] = clean_and_parse_json(raw)
        verdicts_raw: list[dict[str, Any]] = data.get("verdicts", [])

        # Map field → RewrittenSection for quick lookup
        section_map = {s.field: s for s in rewritten_sections}

        for item in verdicts_raw:
            try:
                flag = AuditFlag(**item)
                verdict = flag.verdict
                if verdict == "approved":
                    matched = section_map.get(flag.field)
                    if matched:
                        approved_sections.append(matched)
                else:
                    audit_flags.append(flag)
            except Exception as parse_exc:
                logger.debug("[audit_agent] Skipping malformed verdict: %s", parse_exc)

        # For rewrites that didn't get a verdict, auto-approve them
        audited_fields = {item.get("field") for item in verdicts_raw}
        for section in rewritten_sections:
            if section.field not in audited_fields:
                approved_sections.append(section)

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("[audit_agent] JSON parse failed (%s) — falling back to raw CV (no rewrites applied)", exc)
        return {
            "audit_flags": [],
            "audit_passed": False,
            "optimized_cv": raw_cv,
            "overall_improvement_score": 0.0,
            "pipeline_complete": True,
            "current_step": "audit_done",
        }
    except Exception as exc:
        logger.error("[audit_agent] LLM call failed (%s) — falling back to raw CV (no rewrites applied)", exc)
        return {
            "audit_flags": [],
            "audit_passed": False,
            "optimized_cv": raw_cv,
            "overall_improvement_score": 0.0,
            "pipeline_complete": True,
            "current_step": "audit_done",
        }

    # Build optimized_cv by applying approved rewrites to raw_cv
    optimized_cv = _apply_rewrites(raw_cv, approved_sections)

    # Compute overall improvement score (average of approved sections)
    if approved_sections:
        overall_score = sum(s.improvement_score for s in approved_sections) / len(approved_sections)
        overall_score = min(1.0, max(0.0, overall_score))
    else:
        overall_score = 0.0

    audit_passed = len(audit_flags) == 0
    logger.info(
        "[audit_agent] Approved=%d Flagged=%d Score=%.2f",
        len(approved_sections),
        len(audit_flags),
        overall_score,
    )

    return {
        "audit_flags": audit_flags,
        "audit_passed": audit_passed,
        "optimized_cv": optimized_cv,
        "overall_improvement_score": round(overall_score, 3),
        "pipeline_complete": True,
        "current_step": "audit_done",
    }


def _apply_rewrites(
    raw_cv: dict[str, Any],
    approved_sections: list[RewrittenSection],
) -> dict[str, Any]:
    """Merge approved rewrites into a copy of ``raw_cv``.

    Field paths use dot/bracket notation, e.g.:
        - ``"experience[0].key_impacts[0]"``
        - ``"skills_matrix.languages"``

    Invalid paths are logged and skipped.
    """
    optimized = copy.deepcopy(raw_cv)

    for section in approved_sections:
        try:
            _set_nested(optimized, section.field, section.rewritten)
        except Exception as exc:
            logger.debug("[audit_agent] Could not apply rewrite at '%s': %s", section.field, exc)

    return optimized


def _set_nested(obj: Any, path: str, value: str) -> None:
    """Set a deeply nested value in a dict/list using a dotted path string.

    Examples:
        ``experience[0].key_impacts[0]`` → obj["experience"][0]["key_impacts"][0] = value
        ``skills_matrix.languages``       → obj["skills_matrix"]["languages"] = value
    """

    parts: list[str | int] = []
    for raw_tok in path.replace("]", "").split("."):
        if "[" in raw_tok:
            key, *indices = raw_tok.split("[")
            parts.append(key)
            for idx in indices:
                if idx:
                    parts.append(int(idx))
        else:
            parts.append(raw_tok)

    current: Any = obj
    for part in parts[:-1]:
        if isinstance(current, dict) and isinstance(part, str):  # noqa: SIM114
            current = current[part]
        elif isinstance(current, list) and isinstance(part, int):
            current = current[part]
        else:
            raise KeyError(f"Cannot traverse path at '{part}'")

    last = parts[-1]
    if isinstance(current, dict) and isinstance(last, str):  # noqa: SIM114
        current[last] = value
    elif isinstance(current, list) and isinstance(last, int):
        current[last] = value
    else:
        raise KeyError(f"Cannot set value at '{last}' on type {type(current).__name__}")
