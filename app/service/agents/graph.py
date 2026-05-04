"""LangGraph assembly for the CV intelligence pipeline.

Pipeline:
    START -> retrieval -> roast -> rewrite -> audit -> END

The graph itself is the only orchestration layer; each node is a single
async function that takes the shared ``CVOptimizationState`` plus an injected
``LLMConnector`` and returns a dict of state updates.
"""

from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.core.llm_connector import LLMConnector
from app.service.agents.audit_agent import audit_agent
from app.service.agents.retrieval_agent import retrieval_agent
from app.service.agents.rewrite_agent import rewrite_agent
from app.service.agents.roast_agent import roast_agent
from app.service.agents.state import CVOptimizationState


def _make_node(agent_fn, llm: LLMConnector):
    async def node(state: CVOptimizationState) -> dict:
        return await agent_fn(state, llm)

    node.__name__ = getattr(agent_fn, "__name__", "agent_node")
    return node


def build_cv_optimization_graph(llm: LLMConnector) -> CompiledStateGraph:
    """Construct and compile the CV optimization LangGraph."""
    builder = StateGraph(CVOptimizationState)
    builder.add_node("retrieval", _make_node(retrieval_agent, llm))
    builder.add_node("roast", _make_node(roast_agent, llm))
    builder.add_node("rewrite", _make_node(rewrite_agent, llm))
    builder.add_node("audit", _make_node(audit_agent, llm))
    builder.set_entry_point("retrieval")
    builder.add_edge("retrieval", "roast")
    builder.add_edge("roast", "rewrite")
    builder.add_edge("rewrite", "audit")
    builder.add_edge("audit", END)
    return builder.compile()
