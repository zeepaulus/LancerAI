"""Tests for Pydantic request/response schemas — validation, defaults, constraints."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schema.request import (
    AuthLoginRequest,
    AuthSignupRequest,
    CVUploadRequest,
    InterviewSessionRequest,
    JobMatchRequest,
)
from app.schema.response import (
    InterviewReportResponse,
    JobMatchResponse,
    STARScore,
)


class TestAuthSignupRequest:
    def test_valid_signup(self) -> None:
        req = AuthSignupRequest(email="user@test.com", password="securepass", display_name="Alice")
        assert req.email == "user@test.com"
        assert req.tenant_id is None  # optional

    def test_password_too_short_raises(self) -> None:
        with pytest.raises(ValidationError, match="string_too_short"):
            AuthSignupRequest(email="user@test.com", password="short", display_name="Alice")

    def test_password_too_long_raises(self) -> None:
        with pytest.raises(ValidationError, match="string_too_long"):
            AuthSignupRequest(email="user@test.com", password="x" * 129, display_name="Alice")

    def test_display_name_empty_raises(self) -> None:
        with pytest.raises(ValidationError, match="string_too_short"):
            AuthSignupRequest(email="user@test.com", password="validpassword", display_name="")

    def test_tenant_id_optional(self) -> None:
        req = AuthSignupRequest(
            email="user@test.com",
            password="validpass",
            display_name="Alice",
            tenant_id="my-org",
        )
        assert req.tenant_id == "my-org"


class TestAuthLoginRequest:
    def test_valid_login(self) -> None:
        req = AuthLoginRequest(identifier="user@test.com", password="mypassword")
        assert req.identifier == "user@test.com"

    def test_short_password_raises(self) -> None:
        with pytest.raises(ValidationError, match="string_too_short"):
            AuthLoginRequest(identifier="user@test.com", password="short")


class TestInterviewSessionRequest:
    def test_default_mode_is_practice(self) -> None:
        req = InterviewSessionRequest(cv_id="cv-123")
        assert req.mode == "practice"

    def test_default_duration_is_5(self) -> None:
        req = InterviewSessionRequest(cv_id="cv-123")
        assert req.duration_minutes == 5

    def test_invalid_mode_raises(self) -> None:
        with pytest.raises(ValidationError):
            InterviewSessionRequest(cv_id="cv-123", mode="invalid_mode")  # type: ignore[arg-type]

    def test_valid_modes(self) -> None:
        for mode in ("practice", "mock", "quick"):
            req = InterviewSessionRequest(cv_id="cv-123", mode=mode)
            assert req.mode == mode

    def test_duration_min_boundary(self) -> None:
        req = InterviewSessionRequest(cv_id="cv-123", duration_minutes=1)
        assert req.duration_minutes == 1

    def test_duration_max_boundary(self) -> None:
        req = InterviewSessionRequest(cv_id="cv-123", duration_minutes=60)
        assert req.duration_minutes == 60

    def test_duration_over_max_raises(self) -> None:
        with pytest.raises(ValidationError):
            InterviewSessionRequest(cv_id="cv-123", duration_minutes=61)

    def test_duration_zero_raises(self) -> None:
        with pytest.raises(ValidationError):
            InterviewSessionRequest(cv_id="cv-123", duration_minutes=0)


class TestJobMatchRequest:
    def test_jd_url_and_text_both_missing_raises(self) -> None:
        with pytest.raises(ValidationError, match="Either 'jd_url' or 'jd_text' must be provided."):
            JobMatchRequest(cv_id="cv-1")

    def test_with_jd_url(self) -> None:
        req = JobMatchRequest(cv_id="cv-1", jd_url="https://example.com/job")
        assert req.jd_url == "https://example.com/job"

    def test_with_jd_text(self) -> None:
        req = JobMatchRequest(cv_id="cv-1", jd_text="Python backend engineer...")
        assert req.jd_text == "Python backend engineer..."


class TestCVUploadRequest:
    def test_default_language_is_vi(self) -> None:
        req = CVUploadRequest()
        assert req.language == "vi"

    def test_english_language_valid(self) -> None:
        req = CVUploadRequest(language="en")
        assert req.language == "en"

    def test_invalid_language_raises(self) -> None:
        with pytest.raises(ValidationError):
            CVUploadRequest(language="fr")  # type: ignore[arg-type]


class TestSTARScoreResponse:
    def test_scores_within_range(self) -> None:
        score = STARScore(situation=8.5, task=7.0, action=9.0, result=6.5)
        assert 0 <= score.situation <= 10
        assert 0 <= score.result <= 10

    def test_score_above_max_raises(self) -> None:
        with pytest.raises(ValidationError):
            STARScore(situation=11.0, task=5.0, action=5.0, result=5.0)

    def test_score_below_min_raises(self) -> None:
        with pytest.raises(ValidationError):
            STARScore(situation=-1.0, task=5.0, action=5.0, result=5.0)


class TestJobMatchResponse:
    def test_valid_full_response(self) -> None:
        resp = JobMatchResponse(
            overall_score=80.0,
            frequency_score=70.0,
            position_score=75.0,
            semantic_score=85.0,
        )
        assert resp.overall_score == 80.0
        assert resp.missing_skills == []
        assert resp.improvement_feedback == ""

    def test_score_above_100_raises(self) -> None:
        with pytest.raises(ValidationError):
            JobMatchResponse(
                overall_score=101.0,
                frequency_score=70.0,
                position_score=75.0,
                semantic_score=85.0,
            )

    def test_score_below_0_raises(self) -> None:
        with pytest.raises(ValidationError):
            JobMatchResponse(
                overall_score=80.0,
                frequency_score=70.0,
                position_score=75.0,
                semantic_score=-1.0,
            )

    def test_missing_required_field_raises(self) -> None:
        with pytest.raises(ValidationError):
            JobMatchResponse(overall_score=80.0)  # type: ignore[call-arg]


class TestInterviewReportResponse:
    def test_required_fields(self) -> None:
        report = InterviewReportResponse(
            session_id="s-1",
            overall_confidence=85.5,
        )
        assert report.session_id == "s-1"
        assert report.star_scores == []
        assert report.logic_issues == []

    def test_confidence_out_of_range_raises(self) -> None:
        with pytest.raises(ValidationError):
            InterviewReportResponse(session_id="s-1", overall_confidence=101.0)
