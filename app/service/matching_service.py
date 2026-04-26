"""Module 3 — Job matching.

Implements the Hybrid Scoring algorithm:
    final = 0.20 * frequency + 0.30 * position + 0.50 * semantic

The semantic component combines vector similarity (against the JD embedding)
and the LLM's deep matching analysis. The frequency / position components are
deterministic keyword scoring and stay on the CPU.

TODO:
    - ``match_cv_to_jd``: parse JD (URL crawl or raw text), compute the three
      sub-scores, ask the LLM for human-readable feedback, return one payload.
    - ``get_recommendations``: vector search the job_listings collection for
      top-K matches against the candidate's CV embedding.
    - Cache parsed JDs by hash so repeated runs don't re-prompt the LLM.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector
from app.models.job_listing import JobListing
from app.repository.relational_repository import RelationalRepository
from app.repository.vector_repository import VectorRepository

WEIGHT_FREQUENCY = 0.20
WEIGHT_POSITION = 0.30
WEIGHT_SEMANTIC = 0.50


class MatchingService:
    """CV-JD scoring + job recommendation engine."""

    def __init__(
        self,
        llm_connector: LLMConnector,
        vector_repository: VectorRepository,
        job_repository: RelationalRepository[JobListing],
    ) -> None:
        self._llm = llm_connector
        self._vector_repo = vector_repository
        self._job_repo = job_repository

    async def match_cv_to_jd(
        self,
        cv_data: dict[str, Any],
        jd_text: str,
        jd_url: str = "",
    ) -> dict[str, Any]:
        """Score a CV against a Job Description and return the breakdown."""
        raise NotImplementedError("MatchingService.match_cv_to_jd is not implemented yet.")

    async def get_recommendations(
        self,
        cv_data: dict[str, Any],
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return top-N matching jobs from the crawled corpus."""
        raise NotImplementedError("MatchingService.get_recommendations is not implemented yet.")
