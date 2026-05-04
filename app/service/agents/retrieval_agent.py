"""Retrieval agent.

First node in the CV optimization graph. Pulls industry benchmarks (must-have
skills, ATS criteria, top keywords) for the target role so downstream agents
have grounded context.

TODO:
    - Query the vector DB for similar JDs / role profiles.
    - Optionally call the LLM for a synthesized benchmark when vector data is
      thin.
    - Populate ``industry_benchmarks`` and ``keyword_frequency_map`` on state.
"""

from __future__ import annotations

from app.core.llm_connector import LLMConnector
from app.service.agents.state import CVOptimizationState


async def retrieval_agent(state: CVOptimizationState, llm: LLMConnector) -> dict:
    """Return state updates for the Retrieval node."""
    raise NotImplementedError("retrieval_agent is not implemented yet.")
