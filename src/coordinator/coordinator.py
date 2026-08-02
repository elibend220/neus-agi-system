"""Multi-agent coordinator - orchestrates agent collaboration."""
from typing import Optional, Callable
from src.core import UnifiedState, ProcessingStage, MemoryManager, LLMProvider
from src.agents import BaseAgent


class AgentCoordinator:
    """Orchestrates multiple agents to solve complex tasks."""

    def __init__(self, llm: LLMProvider, memory: MemoryManager):
        self.llm = llm
        self.memory = memory
        self.agents: dict[str, BaseAgent] = {}
        self.pipeline: list[str] = []

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent for coordination."""
        self.agents[agent.name] = agent

    def set_pipeline(self, agent_names: list[str]) -> None:
        """Define the order agents should process state."""
        # Validate all agents exist
        for name in agent_names:
            if name not in self.agents:
                raise ValueError(f"Agent '{name}' not registered")
        self.pipeline = agent_names

    def process(
        self,
        input_text: str,
        input_type: str = "text",
        custom_pipeline: Optional[list[str]] = None,
    ) -> UnifiedState:
        """Execute agents in sequence through the pipeline."""
        import uuid
        from datetime import datetime

        # Initialize state
        state: UnifiedState = {
            "raw_input": input_text,
            "input_type": input_type,
            "agent_chain": [],
            "timestamp": datetime.now().isoformat(),
            "request_id": str(uuid.uuid4()),
            "confidence": 1.0,
            "memory_updates": [],
        }

        # Use custom pipeline or default
        pipeline = custom_pipeline or self.pipeline
        if not pipeline:
            raise ValueError("No pipeline defined. Call set_pipeline() first.")

        # Execute agents in sequence
        for agent_name in pipeline:
            agent = self.agents[agent_name]
            state = agent.process(state)

            # Check for errors
            if state.get("error"):
                break

        return state

    def get_agent_status(self) -> dict:
        """Get status of all registered agents."""
        return {
            name: {
                "name": agent.name,
                "type": agent.__class__.__name__,
            }
            for name, agent in self.agents.items()
        }
