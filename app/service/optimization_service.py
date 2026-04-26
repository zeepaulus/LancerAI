"""Module 2 — CV intelligence and optimization.

Drives the LangGraph multi-agent pipeline:
    retrieval -> roast -> rewrite -> audit  ->  optimized CV

This service is the only public entry point for Module 2; routers should not
talk to LangGraph directly. The graph itself lives in ``app/service/agents``.

TODO:
    - ``analyze_cv``: instantiate ``CVOptimizationState`` from the persisted
      CV, run the compiled graph, persist ``optimized_data`` back on the
      CVRecord, return the final response shape.
    - ``render_template_cv``: ask the LLM to project the optimized CV into a
      named template (Harvard / Stanford / Modern) — return structured JSON.
    - ``render_template_pdf``: turn the structured template into HTML and use
      WeasyPrint to produce a downloadable PDF.
    - Multi-tenancy: enforce that ``cv_id`` belongs to the calling user/tenant.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_connector import LLMConnector
from app.models.cv_record import CVRecord
from app.repository.relational_repository import RelationalRepository
from app.repository.vector_repository import VectorRepository


class OptimizationService:
    """Orchestrates the CV multi-agent pipeline + template rendering."""

    def __init__(
        self,
        llm_connector: LLMConnector,
        vector_repository: VectorRepository,
        cv_repository: RelationalRepository[CVRecord],
    ) -> None:
        self._llm = llm_connector
        self._vector_repo = vector_repository
        self._cv_repo = cv_repository

    async def analyze_cv(
        self,
        cv_id: str,
        cv_data: dict[str, Any],
        target_job_title: str = "",
        target_industry: str = "technology",
        session: AsyncSession | None = None,
    ) -> dict[str, Any]:
        """Run the multi-agent CV analysis pipeline and persist the result."""
        raise NotImplementedError("OptimizationService.analyze_cv is not implemented yet.")

    async def render_template_cv(
        self,
        cv_data: dict[str, Any],
        template: str = "harvard",
    ) -> dict[str, Any]:
        """Project structured CV data into a named template via the LLM."""
        raise NotImplementedError("OptimizationService.render_template_cv is not implemented yet.")

    async def render_template_pdf(
        self,
        cv_data: dict[str, Any],
        template: str = "harvard",
    ) -> bytes:
        """Render the chosen template to a downloadable PDF byte stream."""
        raise NotImplementedError("OptimizationService.render_template_pdf is not implemented yet.")
