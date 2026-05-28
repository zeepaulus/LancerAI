"""Tests for LLM Cache Repository — semantic lookup and persistence."""

from __future__ import annotations

import math
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repository.llm_cache_repository import (
    LLMCacheRepository,
    _cosine_similarity,
    sha256_hex,
)

# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------


def test_cosine_similarity_identical() -> None:
    vec = [1.0, 2.0, 3.0]
    assert math.isclose(_cosine_similarity(vec, vec), 1.0, abs_tol=1e-6)


def test_cosine_similarity_orthogonal() -> None:
    assert math.isclose(_cosine_similarity([1.0, 0.0], [0.0, 1.0]), 0.0, abs_tol=1e-6)


def test_cosine_similarity_zero_vector() -> None:
    assert _cosine_similarity([0.0, 0.0], [1.0, 2.0]) == 0.0


def test_cosine_similarity_known_value() -> None:
    # [1, 0] vs [1, 1]/sqrt(2) => cos = 1/sqrt(2) ≈ 0.7071
    score = _cosine_similarity([1.0, 0.0], [1.0, 1.0])
    assert math.isclose(score, 1.0 / math.sqrt(2), abs_tol=1e-5)


def test_sha256_hex_consistency() -> None:
    h1 = sha256_hex("hello")
    h2 = sha256_hex("hello")
    assert h1 == h2
    assert len(h1) == 64


def test_sha256_hex_different_inputs() -> None:
    assert sha256_hex("hello") != sha256_hex("world")


# ---------------------------------------------------------------------------
# Repository integration tests (mock session)
# ---------------------------------------------------------------------------


def _make_mock_entry(
    entry_id: str = "id-1",
    prompt_embedding: list[float] | None = None,
    response_text: str = "cached response",
    model_name: str = "google/gemma-4-31b-it",
    hit_count: int = 5,
) -> MagicMock:
    entry = MagicMock()
    entry.id = entry_id
    entry.prompt_embedding = prompt_embedding or [1.0, 0.0, 0.0]
    entry.response_text = response_text
    entry.model_name = model_name
    entry.hit_count = hit_count
    return entry


@pytest.fixture()
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.execute = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_find_similar_hit(mock_session: AsyncMock) -> None:
    """find_similar returns entry when cosine similarity >= threshold."""
    # Two rows: first has low similarity, second is identical to query
    row1 = MagicMock()
    row1.id = "id-1"
    row1.prompt_embedding = [0.0, 1.0, 0.0]  # orthogonal

    row2 = MagicMock()
    row2.id = "id-2"
    row2.prompt_embedding = [1.0, 0.0, 0.0]  # identical to query

    rows_result = MagicMock()
    rows_result.all.return_value = [row1, row2]

    # Full entry for winner
    winner_entry = _make_mock_entry("id-2", prompt_embedding=[1.0, 0.0, 0.0])
    winner_result = MagicMock()
    winner_result.scalar_one_or_none.return_value = winner_entry

    mock_session.execute.side_effect = [rows_result, winner_result]

    repo = LLMCacheRepository(mock_session)
    result = await repo.find_similar(
        prompt_embedding=[1.0, 0.0, 0.0],
        model_name="google/gemma-4-31b-it",
        threshold=0.92,
    )

    assert result is not None
    entry, score = result
    assert entry.id == "id-2"
    assert math.isclose(score, 1.0, abs_tol=1e-5)


@pytest.mark.asyncio
async def test_find_similar_miss(mock_session: AsyncMock) -> None:
    """find_similar returns None when best score is below threshold."""
    row1 = MagicMock()
    row1.id = "id-1"
    row1.prompt_embedding = [0.0, 1.0, 0.0]  # orthogonal to query

    rows_result = MagicMock()
    rows_result.all.return_value = [row1]

    mock_session.execute.return_value = rows_result

    repo = LLMCacheRepository(mock_session)
    result = await repo.find_similar(
        prompt_embedding=[1.0, 0.0, 0.0],
        model_name="google/gemma-4-31b-it",
        threshold=0.92,
    )

    assert result is None


@pytest.mark.asyncio
async def test_find_similar_empty_db(mock_session: AsyncMock) -> None:
    """find_similar returns None when the table is empty."""
    rows_result = MagicMock()
    rows_result.all.return_value = []
    mock_session.execute.return_value = rows_result

    repo = LLMCacheRepository(mock_session)
    result = await repo.find_similar([1.0, 0.0], "any-model", threshold=0.92)
    assert result is None


@pytest.mark.asyncio
async def test_save_creates_entry(mock_session: AsyncMock) -> None:
    """save adds a new LLMResponseCache entry to the session."""
    repo = LLMCacheRepository(mock_session)
    entry = await repo.save(
        prompt_text="What is Python?",
        response_text="Python is a programming language.",
        prompt_embedding=[0.1, 0.2, 0.3],
        model_name="google/gemma-4-31b-it",
        backend="nvidia",
        triggered_by_user_id="user-abc",
    )

    mock_session.add.assert_called_once_with(entry)
    mock_session.flush.assert_awaited_once()
    assert entry.prompt_text == "What is Python?"
    assert entry.response_text == "Python is a programming language."
    assert entry.backend == "nvidia"
    assert entry.triggered_by_user_id == "user-abc"
    assert entry.hit_count == 0


@pytest.mark.asyncio
async def test_increment_hit_executes_update(mock_session: AsyncMock) -> None:
    """increment_hit issues an UPDATE statement."""
    repo = LLMCacheRepository(mock_session)
    await repo.increment_hit("some-entry-id")

    mock_session.execute.assert_awaited_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_find_exact_returns_entry(mock_session: AsyncMock) -> None:
    """find_exact returns the matching entry from DB."""
    mock_entry = _make_mock_entry()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = mock_entry
    mock_session.execute.return_value = result_mock

    repo = LLMCacheRepository(mock_session)
    entry = await repo.find_exact("hello", "google/gemma-4-31b-it")
    assert entry is mock_entry


@pytest.mark.asyncio
async def test_find_exact_returns_none(mock_session: AsyncMock) -> None:
    """find_exact returns None when no matching hash in DB."""
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = result_mock

    repo = LLMCacheRepository(mock_session)
    entry = await repo.find_exact("not-cached", "google/gemma-4-31b-it")
    assert entry is None
