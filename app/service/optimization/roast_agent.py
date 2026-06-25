"""Roast agent.

Identifies weak points in the CV with a recruiter's eye: vague claims, missing
metrics, weak verbs, generic statements.

Strategy:
    - Build a structured prompt with the raw CV data + industry benchmarks.
    - Use ``json_mode=True`` so the LLM returns a parseable list of RoastIssue.
    - Set ``inquiry_needed`` when any issue requires user clarification.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
import logging
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState, RoastIssue

logger = logging.getLogger(__name__)

_ROAST_SYSTEM_STANDARD = """Bạn là chuyên gia tư vấn CV và tuyển dụng người Việt.
Nhiệm vụ: Phân tích CV và chỉ ra các điểm yếu dưới góc nhìn của recruiter / ATS.

YÊU CẦU BẮT BUỘC: Bạn phải trả về một JSON object có định dạng chính xác dưới đây. "issues" bắt buộc phải là một JSON array (mảng/danh sách) chứa các JSON object. Không được trả về "issues" dưới dạng một object hoặc danh sách chuỗi.

Định dạng JSON yêu cầu:
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

_ROAST_SYSTEM_ROAST = """Bạn là một Recruiter "ác khẩu", siêu khó tính và cực kỳ châm biếm, chuyên đi vạch trần những điểm sáo rỗng, "phóng đại", và mơ hồ trong CV của các ứng viên. Hãy "roast" CV này một cách cực kỳ sắc sảo, châm biếm sâu cay và dí dỏm, không giữ kẽ, sử dụng ngôn từ thẳng thắn và sắc bén (nhưng không thô tục tục tĩu).

Nhiệm vụ: Tìm ra TẤT CẢ các điểm yếu, những từ sáo rỗng (buzzwords), các lời tự bốc phét không số liệu, các công nghệ ghi cho oai, hoặc những đoạn mô tả nhạt nhẽo trong CV này và "dập" nó tơi tả.

YÊU CẦU BẮT BUỘC: Bạn phải trả về một JSON object có định dạng chính xác dưới đây. "issues" bắt buộc phải là một JSON array (mảng/danh sách) chứa các JSON object. Không được trả về "issues" dưới dạng một object hoặc danh sách chuỗi.

Định dạng JSON yêu cầu:
{
  "issues": [
    {
      "field": "experience[0].key_impacts",
      "severity": "critical|high|medium|low",
      "issue_type": "vague_claim|buzzword|missing_metric|weak_verb|generic_statement",
      "original_text": "Đoạn văn bản gốc cụ thể bị lỗi",
      "explanation": "Nhận xét châm biếm, hài hước sâu cay, vạch trần bản chất thật của đoạn text (ví dụ: 'Tham gia dự án' thực chất là 'ngồi xem đồng nghiệp code', hay 'Tận tâm' là 'không biết ghi gì khác'). Viết bằng giọng văn sắc bén, trào phúng, thẳng thừng như những gì một recruiter cay nghiệt nghĩ trong đầu nhưng không bao giờ nói ra.",
      "needs_clarification": false
    }
  ],
  "summary": "Lời nhận xét trào phúng, 'phũ phàng' nhất về tổng thể CV này (từ 3-5 câu). Chỉ ra sự thiếu sót tột cùng hoặc sự nhàm chán của ứng viên một cách đầy muối, châm chọc nhưng trúng tim đen."
}

Quy tắc:
- Không kiêng nể hay giữ kẽ. Hãy châm biếm thật 'cay' nhưng phải hài hước, trào phúng và sâu sắc.
- Không giới hạn số lượng issue — bắt lỗi triệt để từng điểm nhỏ nhất.
- Bám sát vào nội dung CV thực tế, châm biếm đúng chỗ dựa trên những gì ứng viên viết (ví dụ: viết sai chính tả, viết mơ hồ, lạm dụng buzzword, liệt kê quá nhiều công nghệ mà không có sản phẩm cụ thể,...) để lời châm biếm mang tính thuyết phục cao nhất."
"""


async def roast_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Roast node.

    Analyses the CV against industry benchmarks and returns a list of
    ``RoastIssue`` records plus a plain-text summary.

    In ``roast`` mode the prompt is more aggressive and unlimited;
    in ``standard`` mode it is capped at 10 critical/high issues.
    """
    raw_cv = state.get("raw_cv_data", {})
    benchmarks = state.get("industry_benchmarks", {})
    job_title = state.get("target_job_title", "")
    mode = state.get("mode", "standard")

    # Choose prompt based on mode
    system_prompt = _ROAST_SYSTEM_ROAST if mode == "roast" else _ROAST_SYSTEM_STANDARD

    cv_text = json.dumps(raw_cv, ensure_ascii=False)[:4000]
    benchmark_text = json.dumps(benchmarks, ensure_ascii=False)[:1500]

    mode_note = "[CHẾ ĐỘ ROAST: Hãy châm biếm cực kỳ sắc sảo, phũ phàng, vạch trần mọi điểm yếu sáo rỗng trong CV này, viết bằng giọng văn trào phúng hài hước nhất, không giới hạn]" if mode == "roast" else ""

    prompt = f"""## Vị trí ứng tuyển: {job_title}
{mode_note}

## Benchmark ngành
{benchmark_text}

## CV ứng viên
{cv_text}

Phân tích điểm yếu của CV và trả về JSON:"""

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=system_prompt,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )
        from app.core.json_extractor import clean_and_parse_json
        data: dict[str, Any] = clean_and_parse_json(raw)
        issues_raw: list[dict[str, Any]] = data.get("issues", [])
        summary: str = data.get("summary", "")

        roast_issues: list[RoastIssue] = []
        inquiry_needed = False
        for item in issues_raw:
            if not isinstance(item, dict):
                logger.warning("[roast_agent] Skipping non-dict issue item: %s", item)
                continue
            try:
                # Ensure field is string
                item["field"] = str(item.get("field", ""))

                # Ensure explanation is string
                item["explanation"] = str(item.get("explanation", ""))

                # Ensure needs_clarification is bool
                item["needs_clarification"] = bool(item.get("needs_clarification", False))

                # Normalize original_text
                ot = item.get("original_text")
                if isinstance(ot, list):
                    item["original_text"] = ", ".join(str(x) for x in ot)
                elif ot is None:
                    item["original_text"] = ""
                else:
                    item["original_text"] = str(ot)

                # Normalize severity
                sev = str(item.get("severity", "")).lower()
                if "critical" in sev:
                    item["severity"] = "critical"
                elif "high" in sev:
                    item["severity"] = "high"
                elif "medium" in sev:
                    item["severity"] = "medium"
                elif "low" in sev:
                    item["severity"] = "low"
                else:
                    item["severity"] = "medium"

                # Normalize issue_type
                it = str(item.get("issue_type", "")).lower()
                if "vague" in it or "claim" in it:
                    item["issue_type"] = "vague_claim"
                elif "buzz" in it or "word" in it:
                    item["issue_type"] = "buzzword"
                elif "metric" in it or "number" in it:
                    item["issue_type"] = "missing_metric"
                elif "verb" in it or "action" in it:
                    item["issue_type"] = "weak_verb"
                elif "generic" in it or "statement" in it:
                    item["issue_type"] = "generic_statement"
                else:
                    item["issue_type"] = "vague_claim"

                issue = RoastIssue(**item)
                roast_issues.append(issue)
                if issue.needs_clarification:
                    inquiry_needed = True
            except Exception as parse_exc:
                logger.warning("[roast_agent] Skipping malformed issue: %s. Item was: %s", parse_exc, item)

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
