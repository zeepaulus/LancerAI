"""Tests for ORM Models — schema constraints, enums, defaults, và relationships."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.cv_record import CVRecord
from app.models.interview_session import InterviewSession
from app.models.interview_transcript import InterviewTranscript, MessageRole
from app.models.job_listing import JobListing
from app.models.job_match_result import JobMatchResult, MatchStatus
from app.models.user import User, UserRole
from app.repository.relational_repository import RelationalRepository

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


async def _create_user(session: AsyncSession, *, user_id: str = "u-1") -> User:
    repo: RelationalRepository[User] = RelationalRepository(User)
    return await repo.create(
        session,
        id=user_id,
        tenant_id=user_id,
        email=f"{user_id}@test.local",
        display_name="Test User",
        password_hash="hashed",
        role=UserRole.USER,
    )


async def _create_cv(session: AsyncSession, *, user_id: str = "u-1", cv_id: str = "cv-1") -> CVRecord:
    repo: RelationalRepository[CVRecord] = RelationalRepository(CVRecord)
    return await repo.create(
        session,
        id=cv_id,
        user_id=user_id,
        filename="cv.pdf",
        extracted_data={"raw_text": "Software engineer with 5 years experience"},
    )


async def _create_job(session: AsyncSession, *, job_id: str = "j-1") -> JobListing:
    repo: RelationalRepository[JobListing] = RelationalRepository(JobListing)
    return await repo.create(
        session,
        id=job_id,
        title="Backend Engineer",
        company="AcmeCorp",
        source="manual",
        source_url="https://example.com/job/1",
        description="Python FastAPI required",
    )


# ---------------------------------------------------------------------------
# User Model
# ---------------------------------------------------------------------------


class TestUserModel:
    @pytest.mark.asyncio
    async def test_create_user_with_enum_role(self, async_db_session: AsyncSession) -> None:
        user = await _create_user(async_db_session)
        assert user.id == "u-1"
        assert user.role == UserRole.USER
        assert user.is_active is True

    @pytest.mark.asyncio
    async def test_user_role_value_is_string(self, async_db_session: AsyncSession) -> None:
        user = await _create_user(async_db_session)
        # role.value phải là string để API serialize đúng
        assert user.role.value == "user"

    @pytest.mark.asyncio
    async def test_user_admin_role(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        admin = await repo.create(
            async_db_session,
            id="admin-1",
            tenant_id="admin-1",
            email="admin@test.local",
            display_name="Admin",
            password_hash="hashed",
            role=UserRole.ADMIN,
        )
        assert admin.role == UserRole.ADMIN
        assert admin.role.value == "admin"


# ---------------------------------------------------------------------------
# RelationalRepository — CRUD
# ---------------------------------------------------------------------------


class TestRelationalRepository:
    @pytest.mark.asyncio
    async def test_create_and_get_by_id(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        repo: RelationalRepository[User] = RelationalRepository(User)
        fetched = await repo.get_by_id(async_db_session, "u-1")
        assert fetched is not None
        assert fetched.email == "u-1@test.local"

    @pytest.mark.asyncio
    async def test_get_by_id_returns_none_for_missing(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        result = await repo.get_by_id(async_db_session, "nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_field(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        repo: RelationalRepository[User] = RelationalRepository(User)
        updated = await repo.update(async_db_session, "u-1", display_name="Updated Name")
        assert updated is not None
        assert updated.display_name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_returns_none_for_missing(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        result = await repo.update(async_db_session, "ghost", display_name="x")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_existing_record(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        repo: RelationalRepository[User] = RelationalRepository(User)
        deleted = await repo.delete(async_db_session, "u-1")
        assert deleted is True
        assert await repo.get_by_id(async_db_session, "u-1") is None

    @pytest.mark.asyncio
    async def test_delete_missing_record_returns_false(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        assert await repo.delete(async_db_session, "ghost") is False

    @pytest.mark.asyncio
    async def test_exists_true(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        repo: RelationalRepository[User] = RelationalRepository(User)
        assert await repo.exists(async_db_session, "u-1") is True

    @pytest.mark.asyncio
    async def test_exists_false(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        assert await repo.exists(async_db_session, "ghost") is False

    @pytest.mark.asyncio
    async def test_filter_by_returns_matching(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session, user_id="u-1")
        await _create_user(async_db_session, user_id="u-2")
        repo: RelationalRepository[User] = RelationalRepository(User)
        results = await repo.filter_by(async_db_session, tenant_id="u-1")
        assert len(results) == 1
        assert results[0].id == "u-1"

    @pytest.mark.asyncio
    async def test_filter_by_invalid_column_raises(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        with pytest.raises(ValueError, match="no column"):
            await repo.filter_by(async_db_session, nonexistent_field="x")

    @pytest.mark.asyncio
    async def test_auto_generates_uuid_if_no_id(self, async_db_session: AsyncSession) -> None:
        repo: RelationalRepository[User] = RelationalRepository(User)
        user = await repo.create(
            async_db_session,
            tenant_id="t-auto",
            email="auto@test.local",
            display_name="Auto",
            password_hash="hashed",
            role=UserRole.USER,
        )
        assert user.id  # UUID được tạo tự động
        assert len(user.id) == 36  # UUID4 format


# ---------------------------------------------------------------------------
# JobMatchResult Model
# ---------------------------------------------------------------------------


class TestJobMatchResult:
    @pytest.mark.asyncio
    async def test_create_match_result_with_default_status(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        await _create_cv(async_db_session)
        await _create_job(async_db_session)

        repo: RelationalRepository[JobMatchResult] = RelationalRepository(JobMatchResult)
        result = await repo.create(
            async_db_session,
            id="m-1",
            user_id="u-1",
            cv_id="cv-1",
            job_id="j-1",
            match_score=0.75,
        )
        assert result.status == MatchStatus.RECOMMENDED
        assert result.match_score == 0.75

    @pytest.mark.asyncio
    async def test_match_status_enum_values(self) -> None:
        assert MatchStatus.RECOMMENDED.value == "recommended"
        assert MatchStatus.SAVED.value == "saved"
        assert MatchStatus.APPLIED.value == "applied"
        assert MatchStatus.REJECTED.value == "rejected"

    @pytest.mark.asyncio
    async def test_update_match_status_to_applied(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        await _create_cv(async_db_session)
        await _create_job(async_db_session)

        repo: RelationalRepository[JobMatchResult] = RelationalRepository(JobMatchResult)
        await repo.create(
            async_db_session,
            id="m-2",
            user_id="u-1",
            cv_id="cv-1",
            job_id="j-1",
            match_score=0.5,
        )
        updated = await repo.update(async_db_session, "m-2", status=MatchStatus.APPLIED)
        assert updated is not None
        assert updated.status == MatchStatus.APPLIED


# ---------------------------------------------------------------------------
# InterviewTranscript Model
# ---------------------------------------------------------------------------


class TestInterviewTranscript:
    @pytest.mark.asyncio
    async def test_create_transcript_turns(self, async_db_session: AsyncSession) -> None:
        await _create_user(async_db_session)
        await _create_cv(async_db_session)

        # Create session first
        sess_repo: RelationalRepository[InterviewSession] = RelationalRepository(InterviewSession)
        await sess_repo.create(
            async_db_session,
            id="s-1",
            user_id="u-1",
            cv_id="cv-1",
            mode="practice",
        )

        # Create transcript turns
        tr_repo: RelationalRepository[InterviewTranscript] = RelationalRepository(InterviewTranscript)
        ai_turn = await tr_repo.create(
            async_db_session,
            id="t-1",
            session_id="s-1",
            role=MessageRole.AI,
            content="Tell me about yourself.",
        )
        human_turn = await tr_repo.create(
            async_db_session,
            id="t-2",
            session_id="s-1",
            role=MessageRole.HUMAN,
            content="I am a software engineer...",
        )

        assert ai_turn.role == MessageRole.AI
        assert ai_turn.role.value == "ai"
        assert human_turn.role == MessageRole.HUMAN

    @pytest.mark.asyncio
    async def test_message_role_enum_values(self) -> None:
        assert MessageRole.AI.value == "ai"
        assert MessageRole.HUMAN.value == "human"
        assert MessageRole.SYSTEM.value == "system"


class TestModelMetadata:
    def test_foreign_key_indexes_are_set(self) -> None:
        """Kiểm tra các FK quan trọng đã được set index=True để tránh full table scan."""
        # interview_sessions
        assert InterviewSession.__table__.columns['cv_id'].index is True
        assert InterviewSession.__table__.columns['job_listing_id'].index is True
        assert InterviewSession.__table__.columns['user_id'].index is True

        # job_match_results
        assert JobMatchResult.__table__.columns['cv_id'].index is True
        assert JobMatchResult.__table__.columns['job_id'].index is True
        assert JobMatchResult.__table__.columns['user_id'].index is True
