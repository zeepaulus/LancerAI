from unittest.mock import AsyncMock, MagicMock

import pytest

from app.repository.graph_repository import GraphRepository, GraphRepositoryError


@pytest.mark.asyncio
async def test_get_related_skills_success() -> None:
    # Arrange
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_result = AsyncMock()

    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_session.run.return_value = mock_result

    # Mock records returned by result.data()
    mock_result.data.return_value = [
        {"name": "FastAPI", "distance": 1},
        {"name": "Django", "distance": 2},
    ]

    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)

    # Act
    results = await repo.get_related_skills("Python", depth=2)

    # Assert
    assert len(results) == 2
    assert results[0]["name"] == "FastAPI"
    assert results[0]["distance"] == 1
    assert results[1]["name"] == "Django"
    assert results[1]["distance"] == 2

    # Verify Cypher query execution
    mock_session.run.assert_called_once()
    query_arg = mock_session.run.call_args[0][0]
    assert "MATCH" in query_arg
    assert "$skill_name" in query_arg


@pytest.mark.asyncio
async def test_get_related_skills_invalid_depth() -> None:
    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=MagicMock())
    with pytest.raises(ValueError, match="depth must be an integer between 1 and 5"):
        await repo.get_related_skills("Python", depth=0)


@pytest.mark.asyncio
async def test_get_related_skills_failure() -> None:
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_session.run.side_effect = Exception("Neo4j down")

    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)
    with pytest.raises(GraphRepositoryError, match="Failed to query related skills"):
        await repo.get_related_skills("Python")


@pytest.mark.asyncio
async def test_get_skill_importance_success() -> None:
    # Arrange
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()

    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_session.run.return_value = mock_result

    # Mock single() returning a record
    mock_result.single.return_value = mock_record
    mock_record.__getitem__.side_effect = lambda key: 2 if key == "distance" else None

    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)

    # Act
    score = await repo.get_skill_importance("FastAPI", "Backend")

    # Assert
    assert score == 0.5
    mock_session.run.assert_called_once()


@pytest.mark.asyncio
async def test_get_skill_importance_zero_distance() -> None:
    # Arrange
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_result = AsyncMock()
    mock_record = MagicMock()

    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_session.run.return_value = mock_result

    # Mock single() returning a record with distance 0
    mock_result.single.return_value = mock_record
    mock_record.__getitem__.side_effect = lambda key: 0 if key == "distance" else None

    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)

    # Act
    score = await repo.get_skill_importance("FastAPI", "Backend")

    # Assert
    assert score == 1.0


@pytest.mark.asyncio
async def test_get_skill_importance_no_path() -> None:
    # Arrange
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_result = AsyncMock()

    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_session.run.return_value = mock_result
    mock_result.single.return_value = None

    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)

    # Act
    score = await repo.get_skill_importance("FastAPI", "Backend")

    # Assert
    assert score == 0.0


@pytest.mark.asyncio
async def test_get_skill_importance_failure() -> None:
    mock_driver = MagicMock()
    mock_session = AsyncMock()
    mock_driver.session.return_value.__aenter__.return_value = mock_session
    mock_session.run.side_effect = Exception("Neo4j down")

    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)
    with pytest.raises(GraphRepositoryError, match="Failed to calculate skill importance"):
        await repo.get_skill_importance("FastAPI", "Backend")


@pytest.mark.asyncio
async def test_neo4j_driver_missing() -> None:
    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=None)
    repo._driver = None

    related = await repo.get_related_skills("Python")
    assert related == []

    importance = await repo.get_skill_importance("Python", "Web")
    assert importance == 0.0


@pytest.mark.asyncio
async def test_repo_close() -> None:
    mock_driver = AsyncMock()
    repo = GraphRepository("bolt://localhost:7687", "neo4j", "password", driver=mock_driver)
    await repo.close()
    mock_driver.close.assert_called_once()
