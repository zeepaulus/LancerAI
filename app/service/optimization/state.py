"""LangGraph state schema for the CV Intelligence Pipeline.

All agents read from and write to this single shared state object.
LangGraph merges state updates using the Annotated[list, operator.add] pattern
for append-only fields (e.g., messages, issues lists).
"""

from typing import Annotated, Any, Literal, TypedDict

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Sub-schemas for structured data within the state
# ---------------------------------------------------------------------------


class RoastIssue(BaseModel):
    """A single identified problem in the CV."""

    field: str = Field(description="Which CV section this issue belongs to (e.g., 'experience[0].key_impacts')")
    severity: Literal["critical", "high", "medium", "low"] = "medium"
    issue_type: Literal["vague_claim", "buzzword", "missing_metric", "weak_verb", "generic_statement"] = "vague_claim"
    original_text: str = Field(description="The exact problematic text from the original CV")
    explanation: str = Field(description="Why this is a problem in ATS/recruiter context")
    needs_clarification: bool = Field(default=False, description="Does this require asking the user for more info?")


class InquiryQuestion(BaseModel):
    """A question to ask the user for missing context."""

    question_id: str
    related_field: str
    question: str
    expected_info: str = Field(description="What information we expect to receive (e.g., 'project scale, team size')")
    user_answer: str = ""  # Filled in after user responds


class RewrittenSection(BaseModel):
    """A single rewritten CV section using the Google XYZ formula."""

    field: str
    original: str
    rewritten: str
    formula_used: Literal["xyz", "star", "car", "direct"] = "xyz"
    improvement_score: float = Field(default=0.0, ge=0.0, le=1.0)


class AuditFlag(BaseModel):
    """A truthfulness issue flagged by the Audit Agent."""

    field: str
    rewritten_text: str
    original_text: str
    issue: str = Field(description="Why this rewrite may be inaccurate or exaggerated")
    verdict: Literal["approved", "needs_revision", "rejected"] = "needs_revision"


# ---------------------------------------------------------------------------
# Main LangGraph State
# ---------------------------------------------------------------------------


def list_reducer(left: list[Any] | None, right: Any) -> list[Any]:
    """Reducer that wraps single items into lists and safely appends them."""
    safe_left: list[Any] = left if left is not None else []
    if right is None:
        return safe_left
    if not isinstance(right, list):
        right = [right]
    from typing import cast

    return safe_left + cast(list[Any], right)


class CVOptimizationState(TypedDict, total=False):
    """Shared state flowing through the entire LangGraph pipeline.

    LangGraph uses 'reducer' functions to merge state updates.
    Fields annotated with `Annotated[list, list_reducer]` are append-only.
    """

    # --- Input ---
    cv_id: str
    raw_cv_data: dict[str, Any]
    target_job_title: str
    target_industry: str
    mode: str  # "standard" | "roast" — controls roast agent aggressiveness

    # --- Retrieval Agent outputs ---
    industry_benchmarks: dict[str, Any]
    keyword_frequency_map: dict[str, int]

    # --- Roast Agent outputs (append-only) ---
    roast_issues: Annotated[list[RoastIssue], list_reducer]
    roast_summary: str

    # --- Inquiry Agent outputs (append-only) ---
    inquiry_questions: Annotated[list[InquiryQuestion], list_reducer]
    inquiry_needed: bool
    inquiry_complete: bool

    # --- Rewrite Agent outputs (append-only) ---
    rewritten_sections: Annotated[list[RewrittenSection], list_reducer]

    # --- Audit Agent outputs (append-only) ---
    audit_flags: Annotated[list[AuditFlag], list_reducer]
    audit_passed: bool

    # --- Final output ---
    optimized_cv: dict[str, Any]
    overall_improvement_score: float

    # --- Control flow ---
    current_step: str
    error_message: str
    pipeline_complete: bool
