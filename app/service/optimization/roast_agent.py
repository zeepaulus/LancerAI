"""Roast agent.

Identifies weak points in the CV with a recruiter's eye: vague claims, missing
metrics, weak verbs, generic statements.

TODO:
    - Build a system prompt that demands Vietnamese feedback + JSON output.
    - Run the LLM, parse the response into a list of ``RoastIssue`` records.
    - Set ``inquiry_needed`` when any issue requires user clarification.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.optimization.state import CVOptimizationState


async def roast_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Roast node."""
    raise NotImplementedError("roast_agent is not implemented yet.")
