"""Pydantic schemas for API response serialization."""

from typing import Any

from pydantic import BaseModel, Field


# --- Module 0: Auth ---
class AuthTokenResponse(BaseModel):
    """OAuth2 compliant token response."""

    access_token: str
    token_type: str = "bearer"


class UserProfileResponse(BaseModel):
    """User basic info response."""

    id: str
    email: str
    display_name: str
    tenant_id: str
    role: str


# --- Module 1: Extraction ---
class PersonalInfo(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    location: str = ""


class Education(BaseModel):
    school: str = ""
    degree: str = ""
    major: str = ""
    gpa: str = ""
    period: str = ""


class Experience(BaseModel):
    company: str = ""
    title: str = ""
    period: str = ""
    descriptions: list[str] = Field(default_factory=list)
    key_impacts: list[str] = Field(default_factory=list)
    tech_stack: list[str] = Field(default_factory=list)


class Project(BaseModel):
    name: str = ""
    role: str = ""
    tech_stack: list[str] = Field(default_factory=list)
    description: str = ""
    key_impacts: list[str] = Field(default_factory=list)
    potential_roast_points: list[str] = Field(default_factory=list)


class SkillsMatrix(BaseModel):
    languages: list[str] = Field(default_factory=list)
    frameworks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)


class CVExtractionResponse(BaseModel):
    """Deep JSON schema for a fully extracted CV."""

    cv_id: str
    personal_info: PersonalInfo = Field(default_factory=PersonalInfo)
    education: list[Education] = Field(default_factory=list)
    experience: list[Experience] = Field(default_factory=list)
    projects: list[Project] = Field(default_factory=list)
    skills_matrix: SkillsMatrix = Field(default_factory=SkillsMatrix)
    certifications: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


# --- Module 2: Optimization ---
class CVOptimizationResponse(BaseModel):
    """Result of the multi-agent optimization pipeline."""

    cv_id: str
    audit_score: float = Field(ge=0, le=100, description="Overall ATS score of the optimized CV.")
    optimized_data: dict[str, Any] = Field(
        description="Structured CV data mapped to the final JSON schema.",
    )
    roast_summary: str | None = None
    roast_issues: list[dict[str, Any]] | None = None
    rewritten_sections: list[dict[str, Any]] | None = None


# --- Module 3: Matching ---
class SkillGap(BaseModel):
    """A single missing skill with its impact assessment."""

    skill_name: str
    impact_level: str = Field(description="'critical', 'important', or 'nice_to_have'")
    reason: str = ""


class JobMatchResponse(BaseModel):
    """Result of CV-JD matching analysis."""

    overall_score: float = Field(ge=0, le=100, description="Overall compatibility percentage.")
    frequency_score: float = Field(ge=0, le=100, description="Keyword overlap score (TF-IDF).")
    position_score: float = Field(ge=0, le=100, description="Section weighted score (skills > exp).")
    semantic_score: float = Field(ge=0, le=100, description="Vector similarity score.")
    improvement_feedback: str = Field(default="", description="Human-readable LLM feedback.")
    missing_skills: list[SkillGap] = Field(default_factory=list, description="Prioritized missing skills.")


class JobRecommendationResponse(BaseModel):
    """A recommended job listing based on CV match."""

    job_id: str
    title: str
    company: str
    location: str
    match_score: float
    url: str


# --- Module 4: Interview ---
class STARScore(BaseModel):
    situation: float = Field(ge=0, le=10)
    task: float = Field(ge=0, le=10)
    action: float = Field(ge=0, le=10)
    result: float = Field(ge=0, le=10)


class InterviewReportResponse(BaseModel):
    """Comprehensive interview performance report."""

    session_id: str
    overall_confidence: float = Field(ge=0, le=100)
    total_questions: int = 0
    star_scores: list[STARScore] = Field(default_factory=list)
    logic_issues: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)
    created_at: str | None = None
    title: str | None = None
    focus_area: str | None = None
    status: str | None = None


class RenderedCVResponse(BaseModel):
    """Result of rendering a CV template."""

    template_name: str
    rendered_data: dict[str, Any]


class InterviewSessionResponse(BaseModel):
    """Response containing metadata of a created interview session."""

    session_id: str
    cv_id: str
    mode: str
    status: str
