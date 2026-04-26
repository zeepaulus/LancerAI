"""Pydantic schemas for API response serialization."""

from pydantic import BaseModel, Field


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


# --- Module 3: Matching ---
class SkillGap(BaseModel):
    """A single missing skill with its impact assessment."""

    skill_name: str
    impact_level: str = Field(description="'critical', 'important', or 'nice_to_have'")
    reason: str = ""


class JobMatchResponse(BaseModel):
    """Result of CV-JD matching analysis."""

    match_score: float = Field(ge=0, le=100, description="Overall compatibility percentage.")
    highlighted_jd: str = Field(default="", description="JD text with inline match annotations.")
    gap_list: list[SkillGap] = Field(default_factory=list, description="Prioritized missing skills.")


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
