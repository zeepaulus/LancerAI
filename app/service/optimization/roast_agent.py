"""CV review agent.

The public response schema still uses ``roast_issues`` for backward
compatibility, but the agent behavior is intentionally evidence-led and
professional. It identifies concrete CV weaknesses without aggressive tone or
unsupported assumptions.
"""

# ruff: noqa: E501

from __future__ import annotations

import json
import logging
import unicodedata
from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState, RoastIssue

logger = logging.getLogger(__name__)

_CV_REVIEW_SYSTEM = """Bạn là chuyên gia Prompt Engineering cho đánh giá CV và tuyển dụng IT.
Nhiệm vụ: phân tích CV một cách công bằng, dựa trên bằng chứng có trong CV và bối cảnh vị trí ứng tuyển.

Nguyên tắc bắt buộc:
- Không dùng giọng "roast", châm biếm, công kích hoặc kết luận quá mức.
- Không bịa lỗi. Chỉ nêu vấn đề khi có bằng chứng trong CV hoặc khi thiếu thông tin quan trọng thật sự ảnh hưởng đến đánh giá.
- Phân biệt rõ "thiếu evidence" với "làm sai". Ví dụ: thiếu số liệu impact là điểm cần cải thiện, không phải bằng chứng ứng viên kém.
- Không phạt ứng viên vì thiếu công nghệ không xuất hiện trong target role/JD/benchmark.
- Không bắt lỗi các chi tiết hành chính hoặc học thuật ít ảnh hưởng đến tuyển dụng IT, ví dụ:
  cách tính/thang điểm GPA khi CV đã có GPA, địa chỉ trường, ngày sinh, tình trạng hôn nhân,
  ảnh cá nhân, số CCCD hoặc thông tin không được nhà tuyển dụng dùng để đánh giá năng lực.
- Với học vấn/GPA: chỉ nêu vấn đề nếu thông tin bị sai, mâu thuẫn, hoặc target role/JD yêu cầu rõ.
  Không viết nhận xét kiểu "không rõ cách tính GPA" khi ứng viên đã cung cấp GPA và GPA không phải tiêu chí cốt lõi.
- Nếu một phần chưa hoàn hảo nhưng không ảnh hưởng đáng kể đến quyết định tuyển dụng, hãy bỏ qua thay vì tạo issue severity low.
- Với mỗi issue, trích đúng đoạn gốc vào original_text nếu issue đến từ một câu/bullet cụ thể.
- Nếu issue là thiếu thông tin ở cả section, original_text có thể là "" nhưng needs_clarification phải là true.
- Severity phải hợp lý:
  critical: thiếu/mơ hồ ở thông tin cốt lõi làm recruiter khó đánh giá vai trò, impact hoặc kinh nghiệm.
  high: điểm yếu rõ ảnh hưởng ATS/recruiter nhưng có thể sửa bằng rewrite hoặc bổ sung evidence.
  medium: cải thiện về clarity, format, action verb, scope.
  low: polish nhỏ, không ảnh hưởng lớn đến quyết định.

Rubric đánh giá:
1. Role fit: CV có nêu kỹ năng/kinh nghiệm liên quan đến target role không.
2. Evidence quality: mô tả có action, scope, result, metric hoặc artifact kiểm chứng không.
3. Ownership: có rõ vai trò cá nhân, quyết định kỹ thuật, trade-off không.
4. Structure: các section có đủ và dễ quét cho ATS/recruiter không.
5. Factual safety: có claim nào quá rộng hoặc không được CV hỗ trợ không.

Trả về JSON object đúng schema:
{
  "issues": [
    {
      "field": "experience[0].descriptions[0]",
      "severity": "critical|high|medium|low",
      "issue_type": "vague_claim|buzzword|missing_metric|weak_verb|generic_statement",
      "original_text": "Đoạn gốc cụ thể hoặc chuỗi rỗng nếu thiếu cả section",
      "explanation": "Giải thích ngắn gọn, dựa trên rubric và bằng chứng CV",
      "needs_clarification": false
    }
  ],
  "summary": "Tóm tắt 2-3 câu: điểm mạnh chính, điểm cần cải thiện chính, mức độ sẵn sàng cho target role."
}

Giới hạn:
- Tối đa 8 issues.
- Ưu tiên high-impact issues thay vì bắt lỗi nhỏ; nếu CV tương đối ổn, trả về ít issue hoặc mảng rỗng.
- Không nhắc đến các field path trong explanation; field chỉ để hệ thống định vị dữ liệu."""


_LOW_IMPACT_MARKERS = {
    "cach tinh gpa",
    "thang diem gpa",
    "gpa scale",
    "grading scale",
    "he diem",
    "quy doi gpa",
    "gpa formula",
    "academic grading",
    "dia chi truong",
    "ngay sinh",
    "tinh trang hon nhan",
    "can cuoc",
    "cccd",
    "anh ca nhan",
}


def _norm(value: Any) -> str:
    normalized = unicodedata.normalize("NFKD", str(value or ""))
    stripped = "".join(char for char in normalized if not unicodedata.combining(char))
    return stripped.lower()


def _cv_has_gpa(raw_cv: dict[str, Any]) -> bool:
    education = raw_cv.get("education")
    if not isinstance(education, list):
        return False
    return any(isinstance(item, dict) and str(item.get("gpa") or "").strip() for item in education)


def _is_low_impact_issue(issue: RoastIssue, raw_cv: dict[str, Any], job_title: str) -> bool:
    combined = _norm(f"{issue.field} {issue.original_text} {issue.explanation}")
    target = _norm(job_title)
    if any(marker in combined for marker in _LOW_IMPACT_MARKERS):
        return True
    if "gpa" in combined and _cv_has_gpa(raw_cv) and "gpa" not in target:
        gpa_noise = ("cach tinh", "thang diem", "scale", "grading", "he diem", "quy doi")
        if any(marker in combined for marker in gpa_noise):
            return True
    return False


def _should_keep_issue(issue: RoastIssue, raw_cv: dict[str, Any], job_title: str) -> bool:
    """Backend guardrail for noisy LLM findings before they reach the user."""
    if _is_low_impact_issue(issue, raw_cv, job_title):
        return False

    if issue.severity == "low":
        return False

    # Medium issues without a concrete source quote are usually vague system
    # guesses. Keep high/critical section-level gaps, but suppress medium noise.
    if issue.severity == "medium" and not issue.original_text.strip():
        return False

    return True


def _normalize_issue(item: dict[str, Any]) -> dict[str, Any]:
    item["field"] = str(item.get("field", "") or "cv")
    item["explanation"] = str(item.get("explanation", "") or "").strip()
    item["needs_clarification"] = bool(item.get("needs_clarification", False))

    original_text = item.get("original_text")
    if isinstance(original_text, list):
        item["original_text"] = ", ".join(str(value) for value in original_text)
    elif original_text is None:
        item["original_text"] = ""
    else:
        item["original_text"] = str(original_text)

    severity = str(item.get("severity", "")).lower()
    if "critical" in severity:
        item["severity"] = "critical"
    elif "high" in severity:
        item["severity"] = "high"
    elif "low" in severity:
        item["severity"] = "low"
    else:
        item["severity"] = "medium"

    issue_type = str(item.get("issue_type", "")).lower()
    if "buzz" in issue_type or "word" in issue_type:
        item["issue_type"] = "buzzword"
    elif "metric" in issue_type or "number" in issue_type:
        item["issue_type"] = "missing_metric"
    elif "verb" in issue_type or "action" in issue_type:
        item["issue_type"] = "weak_verb"
    elif "generic" in issue_type or "statement" in issue_type:
        item["issue_type"] = "generic_statement"
    else:
        item["issue_type"] = "vague_claim"

    if not item["original_text"].strip():
        item["needs_clarification"] = True
        if item["severity"] == "critical":
            item["severity"] = "high"
    return item


async def roast_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return professional CV review issues for the optimization graph."""
    raw_cv = state.get("raw_cv_data", {})
    benchmarks = state.get("industry_benchmarks", {})
    job_title = state.get("target_job_title", "")

    cv_text = json.dumps(raw_cv, ensure_ascii=False)[:5000]
    benchmark_text = json.dumps(benchmarks, ensure_ascii=False)[:1800]

    prompt = f"""## Target role
{job_title or "Not specified"}

## Industry / role benchmark
{benchmark_text}

## Parsed CV JSON
{cv_text}

Hãy đánh giá CV theo rubric evidence-first và trả về JSON."""

    raw = ""
    try:
        raw = await llm.generate(
            prompt,
            system=_CV_REVIEW_SYSTEM,
            use_cloud=llm.has_cloud,
            json_mode=True,
        )
        from app.core.json_extractor import clean_and_parse_json

        data: dict[str, Any] = clean_and_parse_json(raw)
        issues_raw = data.get("issues", [])
        summary = str(data.get("summary", "") or "")

        review_issues: list[RoastIssue] = []
        inquiry_needed = False
        for item in issues_raw[:8] if isinstance(issues_raw, list) else []:
            if not isinstance(item, dict):
                logger.warning("[cv_review_agent] Skipping non-dict issue item: %s", item)
                continue
            try:
                issue = RoastIssue(**_normalize_issue(item))
                if not issue.explanation:
                    continue
                if not _should_keep_issue(issue, raw_cv, job_title):
                    logger.info("[cv_review_agent] Skipping low-impact issue: %s", issue.explanation)
                    continue
                review_issues.append(issue)
                inquiry_needed = inquiry_needed or issue.needs_clarification
            except Exception as parse_exc:
                logger.warning("[cv_review_agent] Skipping malformed issue: %s. Item was: %s", parse_exc, item)

        logger.info("[cv_review_agent] Found %d issues (inquiry_needed=%s)", len(review_issues), inquiry_needed)
        return {
            "roast_issues": review_issues,
            "roast_summary": summary,
            "inquiry_needed": inquiry_needed,
            "current_step": "roast_done",
        }

    except (json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.warning("[cv_review_agent] JSON parse failed (%s); raw_length=%d", exc, len(raw or ""))
        return {
            "roast_issues": [],
            "roast_summary": "",
            "inquiry_needed": False,
            "current_step": "roast_done",
        }
    except Exception as exc:
        logger.error("[cv_review_agent] Failed: %s", exc)
        return {
            "roast_issues": [],
            "roast_summary": "",
            "inquiry_needed": False,
            "error_message": str(exc),
            "current_step": "roast_done",
        }
