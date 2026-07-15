"""Integration tests for auth and extraction API routes.

Uses FastAPI's dependency_overrides to inject an in-memory SQLite session
so no real PostgreSQL is needed.
"""

from __future__ import annotations

import io
from collections.abc import AsyncGenerator, Generator
from typing import Any

import pytest
from fastapi import Depends
from fastapi.testclient import TestClient
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import get_db_session
from app.core.providers.auth import get_current_user
from app.core.providers.repositories import (
    get_cv_repository,
    get_interview_session_repository,
)
from app.core.providers.services import (
    get_extraction_service,
    get_interview_service,
    get_matching_service,
    get_optimization_service,
    get_template_renderer,
)
from app.main import app
from app.models import (  # noqa: F401
    cv_record,
    interview_session,
    interview_transcript,
    job_listing,
    job_match_result,
    user,
)
from app.models.base import Base
from app.schema.response import (
    CVExtractionResponse,
    CVOptimizationResponse,
    InterviewReportResponse,
    JobMatchResponse,
    SkillGap,
    STARScore,
)

_TEST_DB_URL = "sqlite+aiosqlite:///:memory:"
_test_engine = create_async_engine(_TEST_DB_URL, echo=False)
_TestSession = async_sessionmaker(bind=_test_engine, class_=AsyncSession, expire_on_commit=False)


class MockExtractionService:
    def __init__(self, cv_repo: Any) -> None:
        self._cv_repo = cv_repo

    async def extract_from_pdf(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        created_cv = await self._cv_repo.create(
            session,
            user_id=user_id,
            filename=filename,
            language="vi",
            extracted_data={
                "personal_info": {
                    "name": "Nguyễn Văn A",
                    "email": "test@test.com",
                    "phone": "123",
                    "linkedin": "",
                    "location": "",
                },
                "education": [
                    {
                        "school": "DH ABC",
                        "degree": "Bachelor",
                        "major": "IT",
                        "gpa": "3.5",
                        "period": "",
                    }
                ],
                "experience": [
                    {
                        "company": "Company A",
                        "title": "Developer",
                        "period": "",
                        "descriptions": ["Dev things"],
                        "key_impacts": ["Impacts"],
                        "tech_stack": ["Python"],
                    }
                ],
                "projects": [],
                "skills_matrix": {
                    "languages": ["Python"],
                    "frameworks": [],
                    "tools": [],
                    "soft_skills": [],
                },
                "certifications": [],
                "languages": [],
            },
        )
        await session.commit()
        await session.refresh(created_cv)
        return CVExtractionResponse(cv_id=created_cv.id, **created_cv.extracted_data)

    async def extract_from_image(
        self,
        file_bytes: bytes,
        filename: str,
        user_id: str,
        session: AsyncSession,
    ) -> CVExtractionResponse:
        return await self.extract_from_pdf(file_bytes, filename, user_id, session)

    async def get_cv(
        self,
        session: AsyncSession,
        cv_id: str,
        user_id: str,
    ) -> Any:
        results = await self._cv_repo.filter_by(session, id=cv_id, user_id=user_id)
        return results[0] if results else None

    async def list_user_cvs(
        self,
        session: AsyncSession,
        user_id: str,
        limit: int = 50,
    ) -> list[Any]:
        from sqlalchemy import select

        from app.models.cv_record import CVRecord

        safe_limit = max(1, min(int(limit or 50), 100))
        result = await session.execute(
            select(CVRecord).where(CVRecord.user_id == user_id).order_by(CVRecord.created_at.desc()).limit(safe_limit)
        )
        return list(result.scalars().all())


def _override_get_extraction_service(
    cv_repo: Any = Depends(get_cv_repository),  # noqa: B008
) -> MockExtractionService:
    return MockExtractionService(cv_repo)


class MockOptimizationService:
    def __init__(self, cv_repo: Any) -> None:
        self._cv_repo = cv_repo

    async def analyze_cv(
        self,
        cv_id: str,
        user_id: str,
        session: AsyncSession,
        target_job_title: str = "",
        target_industry: str = "technology",
        mode: str = "standard",
    ) -> CVOptimizationResponse:
        results = await self._cv_repo.filter_by(session, id=cv_id, user_id=user_id)
        if not results:
            raise ValueError(f"CV '{cv_id}' not found or does not belong to user '{user_id}'")
        cv_record_obj = results[0]
        optimized = cv_record_obj.extracted_data or {}
        await self._cv_repo.update(session, cv_id, optimized_data=optimized)
        await session.commit()
        return CVOptimizationResponse(
            cv_id=cv_id,
            audit_score=95.0,
            optimized_data=optimized,
        )


def _override_get_optimization_service(
    cv_repo: Any = Depends(get_cv_repository),  # noqa: B008
) -> MockOptimizationService:
    return MockOptimizationService(cv_repo)


class MockMatchingService:
    async def match_cv_to_jd(
        self,
        cv_data: dict[str, Any],
        jd_text: str,
        jd_url: str = "",
    ) -> JobMatchResponse:
        return JobMatchResponse(
            overall_score=85.0,
            frequency_score=80.0,
            position_score=90.0,
            semantic_score=85.0,
            improvement_feedback="CV looks good. Consider adding more details about cloud experience.",
            missing_skills=[
                SkillGap(
                    skill_name="Cloud Architecture",
                    impact_level="critical",
                    reason="JD specifically asks for AWS/GCP experience",
                )
            ],
        )

    async def save_match_result(
        self,
        session: AsyncSession,
        user_id: str,
        cv_id: str,
        result: JobMatchResponse,
        job_id: str | None = None,
    ) -> None:
        return None


def _override_get_matching_service() -> MockMatchingService:
    return MockMatchingService()


class MockInterviewService:
    def __init__(self, session_repo: Any) -> None:
        self._sessions = session_repo

    async def create_session(
        self,
        session: AsyncSession,
        cv_id: str,
        user_id: str,
        mode: str,
        job_listing_id: str | None = None,
        focus_area: str | None = None,
        duration_minutes: int = 5,
    ) -> str:
        record = await self._sessions.create(
            session,
            user_id=user_id,
            cv_id=cv_id,
            job_listing_id=job_listing_id,
            mode=mode,
            total_questions=0,
            overall_confidence=0.0,
            star_scores={},
            logic_issues=[],
            improvement_suggestions=[],
        )
        await session.commit()
        return str(record.id)

    async def get_report(
        self,
        session: AsyncSession,
        session_id: str,
    ) -> InterviewReportResponse:
        record = await self._sessions.get_by_id(session, session_id)
        if record is None:
            raise ValueError(f"InterviewSession '{session_id}' not found")
        return InterviewReportResponse(
            session_id=session_id,
            overall_confidence=85.0,
            total_questions=3,
            star_scores=[
                STARScore(situation=8.0, task=8.5, action=9.0, result=8.0),
                STARScore(situation=7.5, task=8.0, action=8.0, result=8.5),
            ],
            logic_issues=["Answered too quickly in part 1"],
            improvement_suggestions=["Structure your answer more clearly using STAR format"],
        )


def _override_get_interview_service(
    session_repo: Any = Depends(get_interview_session_repository),  # noqa: B008
) -> MockInterviewService:
    return MockInterviewService(session_repo)


class MockCVTemplateRenderer:
    async def render_cv(self, cv_data: dict[str, Any], template: str = "harvard") -> dict[str, Any]:
        if template not in {"harvard", "modern", "minimal", "creative"}:
            raise ValueError(f"Unknown template '{template}'")
        return {"template": template, "rendered_data": cv_data}

    async def render_pdf(self, cv_data: dict[str, Any], template: str = "harvard") -> bytes:
        return b"%PDF-1.4 mock pdf content"


def _override_get_template_renderer() -> MockCVTemplateRenderer:
    return MockCVTemplateRenderer()


async def _override_get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with _TestSession() as session:
        try:
            yield session
            await session.commit()
        except SQLAlchemyError:
            await session.rollback()
            raise


async def _override_get_current_user() -> user.User:
    return user.User(
        id="test-user",
        tenant_id="test-tenant",
        email="test@test.com",
        display_name="Test User",
        password_hash="hash",
        role=user.UserRole.USER,
    )


@pytest.fixture(scope="module", autouse=True)
def _setup_test_db() -> Generator[None, None, None]:
    """Create tables once for the module, then teardown after."""
    import asyncio

    async def _create() -> None:
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _drop() -> None:
        async with _test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(_create())
    yield
    asyncio.run(_drop())


@pytest.fixture(scope="module")
def integration_client() -> Generator[TestClient, None, None]:
    """Test client with test SQLite DB; no auth override (real JWT / auth flow)."""
    app.dependency_overrides[get_db_session] = _override_get_db_session
    app.dependency_overrides[get_extraction_service] = _override_get_extraction_service
    app.dependency_overrides[get_optimization_service] = _override_get_optimization_service
    app.dependency_overrides[get_matching_service] = _override_get_matching_service
    app.dependency_overrides[get_interview_service] = _override_get_interview_service
    app.dependency_overrides[get_template_renderer] = _override_get_template_renderer
    client = TestClient(app, raise_server_exceptions=False)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_mock_user(integration_client: TestClient) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_current_user] = _override_get_current_user
    yield integration_client
    app.dependency_overrides.pop(get_current_user, None)


class TestAuthRoutes:
    def test_signup_success(self, integration_client: TestClient) -> None:
        resp = integration_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "secret123",
                "display_name": "New User",
            },
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["email"] == "newuser@example.com"
        assert body["display_name"] == "New User"
        assert body["tenant_id"]
        assert body["role"] == "user"

    def test_signup_duplicate_email(self, integration_client: TestClient) -> None:
        payload = {
            "email": "dup@example.com",
            "password": "secret123",
            "display_name": "One",
        }
        assert integration_client.post("/api/v1/auth/signup", json=payload).status_code == 201
        resp2 = integration_client.post("/api/v1/auth/signup", json=payload)
        assert resp2.status_code == 400

    def test_login_returns_token(self, integration_client: TestClient) -> None:
        integration_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "loginuser@example.com",
                "password": "secret123",
                "display_name": "Login User",
            },
        )
        resp = integration_client.post(
            "/api/v1/auth/login",
            json={"identifier": "loginuser@example.com", "password": "secret123"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()
        assert resp.json().get("token_type") == "bearer"

    def test_login_wrong_password(self, integration_client: TestClient) -> None:
        integration_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "pwcheck@example.com",
                "password": "secret123",
                "display_name": "Pw",
            },
        )
        resp = integration_client.post(
            "/api/v1/auth/login",
            json={"identifier": "pwcheck@example.com", "password": "wrongpass1"},
        )
        assert resp.status_code == 401

    def test_me_with_valid_token(self, integration_client: TestClient) -> None:
        integration_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "meuser@example.com",
                "password": "secret123",
                "display_name": "Me User",
            },
        )
        token = integration_client.post(
            "/api/v1/auth/login",
            json={"identifier": "meuser@example.com", "password": "secret123"},
        ).json()["access_token"]
        resp = integration_client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "meuser@example.com"

    def test_me_no_token_returns_401(self, integration_client: TestClient) -> None:
        resp = integration_client.get("/api/v1/auth/me")
        assert resp.status_code == 401

    def test_me_invalid_bearer_returns_401(self, integration_client: TestClient) -> None:
        resp = integration_client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid.token.here"})
        assert resp.status_code == 401

    def test_display_name_cannot_be_updated(self, integration_client: TestClient) -> None:
        integration_client.post(
            "/api/v1/auth/signup",
            json={
                "email": "immutable-name@example.com",
                "password": "secret123",
                "display_name": "Original Name",
            },
        )
        token = integration_client.post(
            "/api/v1/auth/login",
            json={"identifier": "immutable-name@example.com", "password": "secret123"},
        ).json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        response = integration_client.patch(
            "/api/v1/auth/me",
            json={"display_name": "Changed Name"},
            headers=headers,
        )

        assert response.status_code == 405
        profile = integration_client.get("/api/v1/auth/me", headers=headers)
        assert profile.status_code == 200
        assert profile.json()["display_name"] == "Original Name"

    def test_cors_rejects_patch_preflight(self, integration_client: TestClient) -> None:
        response = integration_client.options(
            "/api/v1/auth/me",
            headers={
                "Origin": "http://localhost:5173",
                "Access-Control-Request-Method": "PATCH",
            },
        )

        assert response.status_code == 400


class TestExtractionRoutes:
    def test_upload_wrong_content_type_returns_415(self, client_with_mock_user: TestClient) -> None:
        resp = client_with_mock_user.post(
            "/api/v1/extraction/cvs",
            files={"file": ("test.txt", b"hello world", "text/plain")},
        )
        assert resp.status_code == 415

    def test_upload_oversized_file_returns_413(self, client_with_mock_user: TestClient) -> None:
        large = io.BytesIO(b"A" * (11 * 1024 * 1024))
        resp = client_with_mock_user.post(
            "/api/v1/extraction/cvs",
            files={"file": ("big.pdf", large, "application/pdf")},
        )
        assert resp.status_code == 413

    def test_upload_valid_pdf_returns_201(self, client_with_mock_user: TestClient) -> None:
        """MVP MOCK: valid PDF upload should persist and return structured CV."""
        minimal_pdf = b"%PDF-1.4 stub"
        resp = client_with_mock_user.post(
            "/api/v1/extraction/cvs",
            files={"file": ("cv.pdf", minimal_pdf, "application/pdf")},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert "cv_id" in body
        assert body["personal_info"]["name"] == "Nguyễn Văn A"
        assert len(body["experience"]) > 0

    def test_get_cv_returns_saved_data(self, client_with_mock_user: TestClient) -> None:
        """Upload then fetch should return the same CV."""
        upload = client_with_mock_user.post(
            "/api/v1/extraction/cvs",
            files={"file": ("cv.pdf", b"%PDF-1.4 stub", "application/pdf")},
        )
        cv_id = upload.json()["cv_id"]
        resp = client_with_mock_user.get(f"/api/v1/extraction/cv/{cv_id}")
        assert resp.status_code == 200
        assert resp.json()["cv_id"] == cv_id

    def test_uploaded_cv_appears_in_history(self, client_with_mock_user: TestClient) -> None:
        """Upload -> history should return the same authenticated user's CV."""
        upload = client_with_mock_user.post(
            "/api/v1/extraction/cvs",
            files={"file": ("history-cv.pdf", b"%PDF-1.4 stub", "application/pdf")},
        )
        assert upload.status_code == 201
        cv_id = upload.json()["cv_id"]

        resp = client_with_mock_user.get("/api/v1/extraction/cvs")

        assert resp.status_code == 200
        body = resp.json()
        history_item = next((item for item in body if item["cv_id"] == cv_id), None)
        assert history_item is not None
        assert history_item["filename"] == "history-cv.pdf"
        assert history_item["candidate_name"] == upload.json()["personal_info"]["name"]
        assert history_item["skills_count"] == 1
        assert history_item["experience_count"] == 1

    def test_get_cv_not_found_returns_404(self, client_with_mock_user: TestClient) -> None:
        resp = client_with_mock_user.get("/api/v1/extraction/cv/nonexistent-id")
        assert resp.status_code == 404

    def test_no_token_upload_returns_401(self, integration_client: TestClient) -> None:
        resp = integration_client.post(
            "/api/v1/extraction/cvs",
            files={"file": ("cv.pdf", b"%PDF-1.4", "application/pdf")},
        )
        assert resp.status_code == 401


class TestOptimizationRoutes:
    def _upload_cv(self, client: TestClient) -> str:
        resp = client.post(
            "/api/v1/extraction/cvs",
            files={"file": ("cv.pdf", b"%PDF-1.4 stub", "application/pdf")},
        )
        return str(resp.json()["cv_id"])

    def test_optimization_returns_200(self, client_with_mock_user: TestClient) -> None:
        cv_id = self._upload_cv(client_with_mock_user)
        resp = client_with_mock_user.post(
            f"/api/v1/optimization/cvs/{cv_id}/optimizations",
            json={},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["cv_id"] == cv_id
        assert 0 <= body["audit_score"] <= 100
        assert body["optimized_data"]

    def test_optimization_wrong_cv_returns_404(self, client_with_mock_user: TestClient) -> None:
        resp = client_with_mock_user.post(
            "/api/v1/optimization/cvs/wrong-id/optimizations",
            json={},
        )
        assert resp.status_code == 404

    def test_render_returns_200(self, client_with_mock_user: TestClient) -> None:
        cv_id = self._upload_cv(client_with_mock_user)
        resp = client_with_mock_user.post(
            f"/api/v1/optimization/cvs/{cv_id}/render",
            json={"template": "harvard"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["template_name"] == "harvard"
        assert body["rendered_data"]


class TestJobMatchRoutes:
    def _upload_cv(self, client: TestClient) -> str:
        resp = client.post(
            "/api/v1/extraction/cvs",
            files={"file": ("cv.pdf", b"%PDF-1.4 stub", "application/pdf")},
        )
        return str(resp.json()["cv_id"])

    def test_match_returns_201(self, client_with_mock_user: TestClient) -> None:
        cv_id = self._upload_cv(client_with_mock_user)
        resp = client_with_mock_user.post(
            "/api/v1/jobs/matches",
            json={"cv_id": cv_id, "jd_text": "Looking for a Python developer"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert 0 <= body["overall_score"] <= 100
        assert 0 <= body["frequency_score"] <= 100
        assert 0 <= body["position_score"] <= 100
        assert 0 <= body["semantic_score"] <= 100
        assert len(body["missing_skills"]) > 0

    def test_match_wrong_cv_returns_404(self, client_with_mock_user: TestClient) -> None:
        resp = client_with_mock_user.post(
            "/api/v1/jobs/matches",
            json={"cv_id": "nonexistent", "jd_text": "Something"},
        )
        assert resp.status_code == 404


class TestInterviewRoutes:
    def _upload_cv(self, client: TestClient) -> str:
        resp = client.post(
            "/api/v1/extraction/cvs",
            files={"file": ("cv.pdf", b"%PDF-1.4 stub", "application/pdf")},
        )
        return str(resp.json()["cv_id"])

    def test_create_session_returns_201(self, client_with_mock_user: TestClient) -> None:
        cv_id = self._upload_cv(client_with_mock_user)
        resp = client_with_mock_user.post(
            "/api/v1/interview/sessions",
            json={"cv_id": cv_id, "mode": "practice"},
        )
        assert resp.status_code == 201
        body = resp.json()
        assert body["session_id"]
        assert body["cv_id"] == cv_id
        assert body["mode"] == "practice"
        assert body["status"] == "created"

    def test_create_session_wrong_cv_returns_404(self, client_with_mock_user: TestClient) -> None:
        resp = client_with_mock_user.post(
            "/api/v1/interview/sessions",
            json={"cv_id": "nonexistent", "mode": "practice"},
        )
        assert resp.status_code == 404

    def test_get_report_returns_200(self, client_with_mock_user: TestClient) -> None:
        """Report requires a valid session that was created by the user."""
        cv_id = self._upload_cv(client_with_mock_user)
        # Create a session first so GET /report can find it
        create_resp = client_with_mock_user.post(
            "/api/v1/interview/sessions",
            json={"cv_id": cv_id, "mode": "practice"},
        )
        session_id = create_resp.json()["session_id"]

        resp = client_with_mock_user.get(f"/api/v1/interview/sessions/{session_id}/report")
        assert resp.status_code == 200
        body = resp.json()
        assert body["session_id"] == session_id
        assert 0 <= body["overall_confidence"] <= 100
        assert body["total_questions"] > 0
        assert len(body["star_scores"]) > 0

    def test_get_report_nonexistent_session_returns_404(self, client_with_mock_user: TestClient) -> None:
        """Report for a session that doesn't exist should return 404."""
        resp = client_with_mock_user.get("/api/v1/interview/sessions/nonexistent-session/report")
        assert resp.status_code == 404


class TestSmokeRoutes:
    def test_root_banner(self, integration_client: TestClient) -> None:
        response = integration_client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert body["service"] == "LancerAI"
        assert body["status"] == "ok"
        assert body["api_prefix"] == "/api/v1"
        assert isinstance(body["endpoints"], list)

    def test_health(self, integration_client: TestClient) -> None:
        response = integration_client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_ready_database_ok(self, integration_client: TestClient) -> None:
        response = integration_client.get("/ready")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ready"
        assert body["checks"]["database"] == "ok"

    def test_ready_returns_503_when_db_unreachable(
        self, integration_client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        class BoomConn:
            async def execute(self, *args: Any, **kwargs: Any) -> Any:
                raise RuntimeError("simulated DB failure")

            async def __aenter__(self) -> BoomConn:
                return self

            async def __aexit__(self, *args: Any) -> bool:
                return False

        class BoomEngine:
            def connect(self) -> BoomConn:
                return BoomConn()

        monkeypatch.setattr("app.main.get_engine", lambda: BoomEngine())
        response = integration_client.get("/ready")
        assert response.status_code == 503
        detail = response.json()["detail"]
        assert detail["status"] == "not_ready"
        assert "database" in detail["checks"]

    def test_openapi_loads(self, integration_client: TestClient) -> None:
        response = integration_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()
        assert "/api/v1/auth/signup" in schema["paths"]
        assert "/api/v1/extraction/cvs" in schema["paths"]
        assert "/api/v1/optimization/cvs/{cv_id}/optimizations" in schema["paths"]
        assert "/api/v1/jobs/matches" in schema["paths"]
        assert "/api/v1/interview/sessions" in schema["paths"]

    def test_interview_health(self, integration_client: TestClient) -> None:
        response = integration_client.get("/api/v1/interview/health")
        assert response.status_code == 200
        assert response.json()["module"] == "interview"
