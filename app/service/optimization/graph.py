"""LangGraph assembly for the CV intelligence pipeline.

Pipeline:
    START -> retrieval -> roast -> rewrite -> audit -> END

The graph itself is the only orchestration layer; each node is a single
async function that takes the shared ``CVOptimizationState`` plus an injected
``LLMConnector`` and returns a dict of state updates.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.core.llm_connector import LLMConnector
from app.repository.graph_repository import GraphRepository
from app.service.optimization.audit_agent import audit_agent
from app.service.optimization.retrieval_agent import retrieval_agent
from app.service.optimization.rewrite_agent import rewrite_agent
from app.service.optimization.roast_agent import roast_agent
from app.service.optimization.state import CVOptimizationState


def _make_node(
    agent_fn: Callable[..., Awaitable[dict[str, Any]]],
    llm: LLMConnector,
    graph_repo: GraphRepository | None = None,
) -> Any:
    async def node(state: CVOptimizationState) -> dict[str, Any]:
        if agent_fn.__name__ == "retrieval_agent":
            return await agent_fn(state, llm, graph_repo)
        return await agent_fn(state, llm)

    node.__name__ = getattr(agent_fn, "__name__", "agent_node")
    return node


def build_cv_optimization_graph(
    llm: LLMConnector,
    graph_repo: GraphRepository | None = None,
) -> CompiledStateGraph[Any, Any, Any]:
    """Construct and compile the CV optimization LangGraph."""
    builder = StateGraph(CVOptimizationState)
    builder.add_node("retrieval", _make_node(retrieval_agent, llm, graph_repo))
    builder.add_node("roast", _make_node(roast_agent, llm))
    builder.add_node("rewrite", _make_node(rewrite_agent, llm))
    builder.add_node("audit", _make_node(audit_agent, llm))
    builder.set_entry_point("retrieval")
    builder.add_edge("retrieval", "roast")
    builder.add_edge("roast", "rewrite")
    builder.add_edge("rewrite", "audit")
    builder.add_edge("audit", END)
    return builder.compile()

