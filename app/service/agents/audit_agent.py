"""Audit agent.

Final compliance gate: verifies that rewrites are truthful, grounded, and not
exaggerated. Approved rewrites are merged into ``state.optimized_cv``;
rejections become ``AuditFlag`` entries for the user to inspect.

TODO:
    - Compare each ``RewrittenSection`` against ``state.raw_cv_data``.
    - Build the merged ``optimized_cv`` blob with applied rewrites.
    - Compute ``overall_improvement_score`` from approved rewrites.
"""

from __future__ import annotations

from typing import Any

from app.core.llm_connector import LLMConnector
from app.service.agents.state import CVOptimizationState


async def audit_agent(state: CVOptimizationState, llm: LLMConnector) -> dict[str, Any]:
    """Return state updates for the Audit node."""
    raise NotImplementedError("audit_agent is not implemented yet.")
