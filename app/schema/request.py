"""Pydantic schemas for API request validation."""

from typing import Literal

from pydantic import BaseModel, Field


class AuthSignupRequest(BaseModel):
    """Payload for POST /auth/signup.

    NOTE: ``email`` is currently a plain ``str``; switch to ``EmailStr`` once
    ``pydantic[email]`` is added as a dependency.
    """

    email: str = Field(..., description="Account email (used as login identifier).")
    password: str = Field(..., min_length=8, max_length=128, description="Plain password (hashed server-side).")
    display_name: str = Field(..., min_length=1, max_length=120)
    tenant_id: str | None = Field(
        default=None,
        description="Optional tenant id; if omitted the service assigns the default tenant.",
    )


class AuthLoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    email: str
    password: str = Field(..., min_length=1)


class CVUploadRequest(BaseModel):
    """Metadata accompanying a CV file upload."""

    language: str = Field(default="vi", description="Primary language of the CV: 'vi' or 'en'.")


class OptimizationRequest(BaseModel):
    """Request to run the intelligence pipeline on an extracted CV."""

    cv_id: str = Field(..., description="Unique identifier of the extracted CV.")
    target_job_title: str = Field(default="", description="Target role to bias the analysis toward.")
    target_industry: str = Field(default="technology")
    mode: str = Field(default="standard", description="Evaluation mode: 'standard' or 'roast'.")


class JobMatchRequest(BaseModel):
    """Request to match a CV against a Job Description."""

    cv_id: str = Field(..., description="Unique identifier of the CV to match.")
    jd_url: str | None = Field(default=None, description="URL of the job posting to crawl.")
    jd_text: str | None = Field(default=None, description="Raw JD text for direct analysis.")


class InterviewSessionRequest(BaseModel):
    """Request to create a new interview session."""

    cv_id: str = Field(..., description="CV to use as interview context.")
    mode: Literal["practice", "mock", "quick"] = Field(
        default="practice",
        description="Interview mode: 'practice' (coaching), 'mock' (realistic), or 'quick' (fast-paced).",
    )
    focus_area: str | None = Field(default=None, description="Optional: Specific topic to focus on.")
    duration_minutes: int = Field(default=5, ge=1, le=60, description="Target interview duration in minutes.")
