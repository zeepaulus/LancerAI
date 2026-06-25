"""Pydantic schemas for API request validation."""

from typing import Literal

from pydantic import BaseModel, Field, model_validator


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
        description=(
            "Optional tenant id. MVP: IGNORED by the server — "
            "tenant_id is always set to user_id server-side. "
            "Will be used when invite/organization flow is implemented."
        ),
    )


class AuthLoginRequest(BaseModel):
    """Payload for POST /auth/login."""

    identifier: str = Field(..., description="Email or display name.")
    password: str = Field(..., min_length=8)


class CVUploadRequest(BaseModel):
    """Metadata accompanying a CV file upload."""

    language: Literal["vi", "en"] = Field(default="vi", description="Primary language of the CV: 'vi' or 'en'.")


class OptimizationRequest(BaseModel):
    """Request body for POST /optimization/cvs/{cv_id}/optimizations.

    NOTE: ``cv_id`` is supplied via the URL path parameter, not this body.
    Only pipeline-tuning fields belong here.
    """

    target_job_title: str = Field(default="", description="Target role to bias the analysis toward.")
    target_industry: str = Field(default="technology")
    mode: str = Field(default="standard", description="Evaluation mode: 'standard' or 'roast'.")


class JobMatchRequest(BaseModel):
    """Request to match a CV against a Job Description."""

    cv_id: str = Field(..., description="Unique identifier of the CV to match.")
    jd_url: str | None = Field(default=None, description="URL of the job posting to crawl.")
    jd_text: str | None = Field(default=None, description="Raw JD text for direct analysis.")

    @model_validator(mode="after")
    def _require_jd_source(self) -> "JobMatchRequest":
        """At least one JD source must be provided."""
        if not self.jd_url and not self.jd_text:
            raise ValueError("Either 'jd_url' or 'jd_text' must be provided.")
        return self


class InterviewSessionRequest(BaseModel):
    """Request to create a new interview session."""

    cv_id: str = Field(..., description="CV to use as interview context.")
    job_listing_id: str | None = Field(default=None, description="Optional JD to tailor the interview.")
    job_title: str | None = Field(
        default=None,
        max_length=160,
        description="Optional target role for CV-only interviews.",
    )
    jd_text: str | None = Field(
        default=None,
        max_length=12000,
        description="Optional pasted JD text for this interview.",
    )
    jd_url: str | None = Field(default=None, max_length=500, description="Optional JD source URL for context/audit.")
    mode: Literal["practice", "mock", "quick"] = Field(
        default="practice",
        description="Interview mode: 'practice' (coaching), 'mock' (realistic), or 'quick' (fast-paced).",
    )
    focus_area: str | None = Field(default=None, description="Optional: Specific topic to focus on.")
    duration_minutes: int = Field(default=5, ge=1, le=60, description="Target interview duration in minutes.")


class RenderTemplateRequest(BaseModel):
    """Request body for POST /optimization/cvs/{cv_id}/render.

    NOTE: ``cv_id`` is supplied via the URL path parameter, not this body.
    """

    template: str = Field(default="harvard", description="Template name: 'harvard', 'stanford', 'modern'.")
