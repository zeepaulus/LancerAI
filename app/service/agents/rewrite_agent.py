"""Rewrite agent.

Rewrites weak CV sections using the Google XYZ formula
(``Accomplished X, as measured by Y, by doing Z``).

TODO:
    - Take the issues produced by ``roast_agent`` (and optional user
      clarifications) and ask the LLM to produce concrete rewrites.
    - Never invent metrics — must stay grounded in the original CV.
    - Return a list of ``RewrittenSection`` instances.
"""

from __future__ import annotations

from app.core.llm_connector import LLMConnector
from app.service.agents.state import CVOptimizationState


async def rewrite_agent(state: CVOptimizationState, llm: LLMConnector) -> dict:
    """Return state updates for the Rewrite node."""
    raise NotImplementedError("rewrite_agent is not implemented yet.")
