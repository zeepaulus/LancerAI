"""Module 2 — CV intelligence and optimization.

Drives the LangGraph multi-agent pipeline:
    retrieval -> roast -> rewrite -> audit  ->  optimized CV

This service is the only public entry point for the pipeline; routers should
not talk to LangGraph directly. Template rendering (JSON / PDF) lives in
``app/service/optimization/template_renderer.py``.
"""

from __future__ import annotations

import logging
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.llm_connector import LLMConnector
from app.models.cv_record import CVRecord
from app.repository.base_vector_repository import BaseVectorRepository
from app.repository.graph_repository import GraphRepository
from app.repository.relational_repository import RelationalRepository
from app.schema.response import CVOptimizationResponse
from app.service.cv_analysis.scorecard import build_cv_scorecard
from app.service.optimization.graph import build_cv_optimization_graph

logger = logging.getLogger(__name__)


class OptimizationService:
    """Orchestrates the CV multi-agent pipeline."""

    def __init__(
        self,
        llm_connector: LLMConnector,
        vector_repository: BaseVectorRepository,
        cv_repository: RelationalRepository[CVRecord],
        graph_repository: GraphRepository | None = None,
    ) -> None:
        self._llm = llm_connector
        self._vector_repo = vector_repository
        self._cv_repo = cv_repository
        self._graph_repo = graph_repository
        # Build the compiled graph once per service instance (thread-safe, stateless)
        self._graph = build_cv_optimization_graph(llm_connector, graph_repository)


    async def analyze_cv(
        self,
        cv_id: str,
        user_id: str,
        session: AsyncSession,
        target_job_title: str = "",
        target_industry: str = "technology",
        mode: str = "standard",
    ) -> CVOptimizationResponse:
        """Run the multi-agent CV analysis pipeline and persist the result.

        Steps:
          1. Fetch CVRecord and verify ownership (raises ValueError if not found).
          2. Build the initial ``CVOptimizationState`` from the CV's extracted data.
          3. Execute the compiled LangGraph workflow via ``ainvoke()``.
          4. Extract ``optimized_cv`` and ``overall_improvement_score`` from
             the completed state.
          5. Persist the ``optimized_data`` back to the CVRecord.
          6. Return a ``CVOptimizationResponse``.
        """
        # 1. Fetch and validate CV ownership
        results = await self._cv_repo.filter_by(session, id=cv_id, user_id=user_id)
        if not results:
            raise ValueError(f"CV '{cv_id}' not found or does not belong to user '{user_id}'")
        cv_record: CVRecord = results[0]

        extracted_data: dict[str, Any] = cv_record.extracted_data or {}

        # 2. Build initial state for the LangGraph pipeline
        initial_state: dict[str, Any] = {
            "cv_id": cv_id,
            "raw_cv_data": extracted_data,
            "target_job_title": target_job_title.strip(),
            "target_industry": target_industry,
            "mode": mode,  # "standard" | "roast"
            # Initialise append-only lists to empty so reducers don't crash
            "roast_issues": [],
            "inquiry_questions": [],
            "rewritten_sections": [],
            "audit_flags": [],
            "current_step": "start",
            "pipeline_complete": False,
        }

        logger.info(
            "[OptimizationService] Starting pipeline for CV=%s user=%s job='%s'",
            cv_id,
            user_id,
            initial_state["target_job_title"],
        )

        # 3. Execute LangGraph pipeline
        final_state = await self._graph.ainvoke(initial_state)

        # 4. Extract results
        optimized_cv: dict[str, Any] = final_state.get("optimized_cv") or extracted_data
        improvement_score: float = final_state.get("overall_improvement_score", 0.0)

        deterministic_scorecard = build_cv_scorecard(
            optimized_cv,
            target_job_title=initial_state["target_job_title"],
            target_industry=target_industry,
        )
        deterministic_scorecard["pipeline_improvement_score"] = round(
            min(100.0, max(0.0, improvement_score * 100)),
            1,
        )
        audit_score = float(deterministic_scorecard["overall_score"])

        # 5. Persist optimized data back to CVRecord
        await self._cv_repo.update(session, cv_id, optimized_data=optimized_cv)
        await session.commit()

        # Persist new analytics columns (additive — does not affect existing logic)
        await self._cv_repo.update(
            session,
            cv_id,
            audit_score=audit_score,
            optimization_mode=mode,
            status="optimized",
        )
        await session.commit()

        logger.info(
            "[OptimizationService] Pipeline complete for CV=%s — score=%.1f",
            cv_id,
            audit_score,
        )

        # 6. Return response
        return CVOptimizationResponse(
            cv_id=cv_id,
            audit_score=audit_score,
            optimized_data=optimized_cv,
            roast_summary=final_state.get("roast_summary"),
            roast_issues=[
                issue.model_dump() if hasattr(issue, "model_dump") else dict(issue)
                for issue in final_state.get("roast_issues", [])
            ] if final_state.get("roast_issues") is not None else None,
            rewritten_sections=[
                sec.model_dump() if hasattr(sec, "model_dump") else dict(sec)
                for sec in final_state.get("rewritten_sections", [])
            ] if final_state.get("rewritten_sections") is not None else None,
            cv_scorecard=deterministic_scorecard,
        )
