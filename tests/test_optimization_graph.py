from unittest.mock import MagicMock

from app.core.llm_connector import LLMConnector
from app.service.optimization.graph import build_cv_optimization_graph


def test_build_cv_optimization_graph() -> None:
    mock_llm = MagicMock(spec=LLMConnector)
    graph = build_cv_optimization_graph(mock_llm)

    assert graph is not None
    # Basic verification that it's compiled correctly
    assert hasattr(graph, "ainvoke")
