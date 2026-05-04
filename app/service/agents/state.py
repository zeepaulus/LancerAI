"""LangGraph state schema for the CV Intelligence Pipeline.

All agents read from and write to this single shared state object.
LangGraph merges state updates using the Annotated[list, operator.add] pattern
for append-only fields (e.g., messages, issues lists).
"""

import operator
from typing import Annotated, Any, Literal
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

class CVOptimizationState(BaseModel):
    """Shared state flowing through the entire LangGraph pipeline.

    LangGraph uses 'reducer' functions to merge state updates.
    Fields annotated with `Annotated[list, operator.add]` are append-only.
    """

    # --- Input ---
    cv_id: str = ""
    raw_cv_data: dict[str, Any] = Field(default_factory=dict)
    target_job_title: str = ""
    target_industry: str = ""

    # --- Retrieval Agent outputs ---
    industry_benchmarks: dict[str, Any] = Field(default_factory=dict)
    keyword_frequency_map: dict[str, int] = Field(default_factory=dict)

    # --- Roast Agent outputs (append-only) ---
    roast_issues: Annotated[list[RoastIssue], operator.add] = Field(default_factory=list)
    roast_summary: str = ""

    # --- Inquiry Agent outputs (append-only) ---
    inquiry_questions: Annotated[list[InquiryQuestion], operator.add] = Field(default_factory=list)
    inquiry_needed: bool = False
    inquiry_complete: bool = False

    # --- Rewrite Agent outputs (append-only) ---
    rewritten_sections: Annotated[list[RewrittenSection], operator.add] = Field(default_factory=list)

    # --- Audit Agent outputs (append-only) ---
    audit_flags: Annotated[list[AuditFlag], operator.add] = Field(default_factory=list)
    audit_passed: bool = False

    # --- Final output ---
    optimized_cv: dict[str, Any] = Field(default_factory=dict)
    overall_improvement_score: float = 0.0

    # --- Control flow ---
    current_step: str = "start"
    error_message: str = ""
    pipeline_complete: bool = False

    model_config = {"arbitrary_types_allowed": True}
