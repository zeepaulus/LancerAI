"""Optimization package: LangGraph Multi-Agent CV Optimization Pipeline.

Bounded context for Module 2 — CV Intelligence & Optimization.
Owns the full pipeline: Retrieval → Roast → Rewrite → Audit.

Public surface:
    - OptimizationService  : orchestrator, the only entry-point for routers.
    - build_cv_optimization_graph : LangGraph factory (used by the service).
    - State / sub-schemas   : CVOptimizationState + supporting Pydantic models.
"""

from app.service.optimization.graph import build_cv_optimization_graph
from app.service.optimization.service import OptimizationService
from app.service.optimization.state import (
    AuditFlag,
    CVOptimizationState,
    InquiryQuestion,
    RewrittenSection,
    RoastIssue,
)

__all__ = [
    "OptimizationService",
    "build_cv_optimization_graph",
    "CVOptimizationState",
    "RoastIssue",
    "InquiryQuestion",
    "RewrittenSection",
    "AuditFlag",
]
