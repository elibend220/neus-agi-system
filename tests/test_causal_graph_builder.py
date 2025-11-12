"""Tests for causal graph builder placeholder."""
from core.reasoning.causal.causal_graph_builder import CausalGraphBuilder


def test_causal_graph_builder_build():
    b = CausalGraphBuilder()
    graph = b.build([])
    assert isinstance(graph, dict)
