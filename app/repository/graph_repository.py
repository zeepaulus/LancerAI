"""Knowledge Graph repository for skill relationship mapping.

Abstracts Neo4j operations for domain-aware skill analysis.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class GraphRepositoryError(Exception):
    """Raised when Neo4j operations fail."""


class GraphRepository:
    """Manages the technology/skill knowledge graph in Neo4j.

    Used by:
    - Module 2: Understanding skill relationships for contextual roasting.
    - Module 3: Domain-aware weighting in Hybrid Scoring (Context Score).
    """

    def __init__(self, uri: str, user: str, password: str, *, driver: Any = None) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = driver
        if self._driver is None:
            try:
                from neo4j import AsyncGraphDatabase
                self._driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            except ImportError:
                logger.warning("Neo4j python package is not installed. Driver init skipped.")

    async def close(self) -> None:
        """Release the Neo4j driver connection."""
        if self._driver is not None:
            await self._driver.close()

    async def get_related_skills(self, skill_name: str, depth: int = 2) -> list[dict[str, Any]]:
        """Find skills related to the given skill within N hops."""
        if self._driver is None:
            logger.warning("Neo4j driver is not initialized. get_related_skills returning empty list.")
            return []

        if not isinstance(depth, int) or depth < 1:
            raise ValueError("depth must be a positive integer")

        query = (
            f"MATCH (s {{name: $skill_name}})-[p*1..{depth}]-(o) "
            "WHERE o.name IS NOT NULL AND o <> s "
            "WITH o, min(length(p)) AS dist "
            "RETURN o.name AS name, dist AS distance "
            "ORDER BY distance, name"
        )
        try:
            async with self._driver.session() as session:
                result = await session.run(query, {"skill_name": skill_name})
                records = await result.data()
                return [
                    {"name": str(r["name"]), "distance": int(r["distance"])}
                    for r in records
                ]
        except Exception as e:
            logger.exception("Neo4j: get_related_skills failed")
            raise GraphRepositoryError("Failed to query related skills") from e

    async def get_skill_importance(self, skill_name: str, domain: str) -> float:
        """Calculate the importance score of a skill within a specific domain."""
        if self._driver is None:
            logger.warning("Neo4j driver is not initialized. get_skill_importance returning 0.0.")
            return 0.0

        query = (
            "MATCH (s {name: $skill_name}), (d {name: $domain}) "
            "MATCH p = shortestPath((s)-[*1..5]-(d)) "
            "RETURN length(p) AS distance"
        )
        try:
            async with self._driver.session() as session:
                result = await session.run(query, {"skill_name": skill_name, "domain": domain})
                record = await result.single()
                if record and record["distance"] is not None:
                    distance = int(record["distance"])
                    if distance == 0:
                        return 1.0
                    return round(1.0 / distance, 2)
                return 0.0
        except Exception as e:
            logger.exception("Neo4j: get_skill_importance failed")
            raise GraphRepositoryError("Failed to calculate skill importance") from e

