"""LangGraph builder for AGI pipeline."""
from langgraph.graph import StateGraph, END
from src.core import UnifiedState
from src.coordinator import AgentCoordinator


class GraphBuilder:
    """Builds LangGraph from AGI coordinator."""

    def __init__(self, coordinator: AgentCoordinator):
        self.coordinator = coordinator

    def build(self):
        """Build compiled LangGraph from coordinator."""
        graph = StateGraph(UnifiedState)

        # Add entry node
        graph.add_node("process", self._process_node)
        graph.set_entry_point("process")
        graph.add_edge("process", END)

        return graph.compile()

    def _process_node(self, state: UnifiedState) -> UnifiedState:
        """Process state through coordinator."""
        return self.coordinator.process(
            state.get("raw_input", ""),
            input_type=state.get("input_type", "text"),
        )

    def build_multi_stage(self):
        """Build LangGraph with per-agent nodes (more granular)."""
        graph = StateGraph(UnifiedState)

        pipeline = self.coordinator.pipeline
        if not pipeline:
            raise ValueError("Coordinator pipeline not configured")

        # Add nodes for each agent
        for agent_name in pipeline:
            agent = self.coordinator.agents[agent_name]
            graph.add_node(agent_name, lambda state, a=agent: a.process(state))

        # Set entry point to first agent
        graph.set_entry_point(pipeline[0])

        # Connect agents in sequence
        for i in range(len(pipeline) - 1):
            graph.add_edge(pipeline[i], pipeline[i + 1])

        # Last agent goes to END
        graph.add_edge(pipeline[-1], END)

        return graph.compile()
