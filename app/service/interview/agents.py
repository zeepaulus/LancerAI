"""Interview agent nodes.

Three logical roles inside the interview state machine:
    - ``question_node``: pick the next question from CV + JD context.
    - ``evaluate_node``: STAR-score the candidate's answer.
    - ``wrap_up_node``: produce the final holistic assessment.

These are kept as plain async functions (no LangGraph wiring) because the
realtime pipeline drives them imperatively. They can be lifted into a graph
later if we want LangSmith tracing across the conversation.

TODO:
    - Fill in prompt templates (Vietnamese-friendly).
    - Wire each function to ``LLMConnector.generate`` with json_mode=True.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.interview.state import InterviewState


async def question_node(state: InterviewState, llm: LLMConnector) -> dict[str, Any]:
    """Generate the next interview question."""
    raise NotImplementedError("question_node is not implemented yet.")


async def evaluate_node(state: InterviewState, llm: LLMConnector) -> dict[str, Any]:
    """STAR-score the candidate's most recent answer."""
    raise NotImplementedError("evaluate_node is not implemented yet.")


async def wrap_up_node(state: InterviewState, llm: LLMConnector) -> dict[str, Any]:
    """Produce the final holistic assessment for the session."""
    raise NotImplementedError("wrap_up_node is not implemented yet.")
