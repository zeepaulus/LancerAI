"""Retrieval agent.

First node in the CV optimization graph. Pulls industry benchmarks (must-have
skills, ATS criteria, top keywords) for the target role so downstream agents
have grounded context.

TODO:
    - Query the vector DB for similar JDs / role profiles using
      ``vector_repository.search_similar(query_embedding, top_k=10)``.
    - Optionally call the LLM for a synthesized benchmark summary when
      vector data is thin (fewer than 3 matches).
    - Populate ``industry_benchmarks`` and ``keyword_frequency_map`` on state.

NOTE:
    The agent currently only receives ``llm`` via the graph node wrapper.
    When implementing, inject ``VectorRepository`` into ``OptimizationService``
    and pass it down to this agent via the state or a closure, following the
    same ``_make_node`` pattern in ``graph.py``.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState


async def retrieval_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Retrieval node."""
    raise NotImplementedError("retrieval_agent is not implemented yet.")
