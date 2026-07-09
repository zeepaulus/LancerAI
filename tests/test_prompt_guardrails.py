import pytest

from app.service.optimization.audit_agent import audit_agent
from app.service.optimization.retrieval_agent import retrieval_agent
from app.service.optimization.rewrite_agent import rewrite_agent
from app.service.optimization.roast_agent import _is_low_impact_issue, _should_keep_issue
from app.service.optimization.state import RewrittenSection, RoastIssue


def test_gpa_scale_comment_is_low_impact_when_gpa_exists() -> None:
    issue = RoastIssue(
        field="education[0].gpa",
        severity="medium",
        issue_type="vague_claim",
        original_text="GPA: 3.8",
        explanation="Không rõ cách tính GPA, dù ứng viên đạt GPA cao.",
        needs_clarification=False,
    )
    raw_cv = {"education": [{"school": "ABC University", "gpa": "3.8"}]}

    assert _is_low_impact_issue(issue, raw_cv, "Backend Developer")


def test_medium_issue_without_evidence_is_filtered() -> None:
    issue = RoastIssue(
        field="experience",
        severity="medium",
        issue_type="generic_statement",
        original_text="",
        explanation="Kinh nghiệm chưa đủ rõ.",
        needs_clarification=True,
    )

    assert not _should_keep_issue(issue, {"experience": []}, "Backend Developer")


@pytest.mark.asyncio
async def test_rewrite_agent_skips_non_priority_issues() -> None:
    medium_issue = RoastIssue(
        field="education[0].gpa",
        severity="medium",
        issue_type="vague_claim",
        original_text="GPA: 3.8",
        explanation="GPA chưa ghi rõ thang điểm.",
        needs_clarification=False,
    )
    result = await rewrite_agent({"roast_issues": [medium_issue], "raw_cv_data": {}}, llm=None)

    assert result["rewritten_sections"] == []
    assert result["current_step"] == "rewrite_done"


@pytest.mark.asyncio
async def test_rewrite_agent_rejects_invented_numeric_claim() -> None:
    class FakeLLM:
        has_cloud = False

        async def generate(self, *args, **kwargs) -> str:
            return """{
              "rewrites": [{
                "field": "experience[0].descriptions[0]",
                "original": "Built API services.",
                "rewritten": "Reduced API latency by 50% by building API services.",
                "formula_used": "xyz",
                "improvement_score": 0.9
              }]
            }"""

    issue = RoastIssue(
        field="experience[0].descriptions[0]",
        severity="high",
        issue_type="missing_metric",
        original_text="Built API services.",
        explanation="Thiếu kết quả đo lường.",
        needs_clarification=False,
    )

    result = await rewrite_agent({"roast_issues": [issue], "raw_cv_data": {}}, llm=FakeLLM())

    assert result["rewritten_sections"] == []


@pytest.mark.asyncio
async def test_audit_agent_does_not_apply_rewrite_without_verdict() -> None:
    class FakeLLM:
        has_cloud = False

        async def generate(self, *args, **kwargs) -> str:
            return '{"verdicts": []}'

    raw_cv = {"experience": [{"descriptions": ["Built API services."]}]}
    rewrite = RewrittenSection(
        field="experience[0].descriptions[0]",
        original="Built API services.",
        rewritten="Built API services for internal users.",
        formula_used="direct",
        improvement_score=0.7,
    )

    result = await audit_agent(
        {
            "raw_cv_data": raw_cv,
            "rewritten_sections": [rewrite],
            "roast_issues": [],
        },
        llm=FakeLLM(),
    )

    assert result["optimized_cv"] == raw_cv
    assert result["audit_flags"]
    assert not result["audit_passed"]


@pytest.mark.asyncio
async def test_retrieval_agent_skips_benchmark_without_target_role() -> None:
    class FailingLLM:
        has_cloud = False

        async def generate(self, *args, **kwargs) -> str:
            raise AssertionError("LLM should not be called without target role")

    result = await retrieval_agent({"target_job_title": "", "target_industry": "technology"}, FailingLLM())

    assert result["industry_benchmarks"] == {}
    assert result["keyword_frequency_map"] == {}
    assert result["current_step"] == "retrieval_done"
