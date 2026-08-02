"""Base agent class - all agents inherit from this."""
from abc import ABC, abstractmethod
from typing import Optional
from src.core import LLMProvider, MemoryManager, UnifiedState


class BaseAgent(ABC):
    """Foundation for all AGI agents."""

    def __init__(
        self,
        name: str,
        llm: LLMProvider,
        memory: MemoryManager,
        system_prompt: Optional[str] = None,
    ):
        self.name = name
        self.llm = llm
        self.memory = memory
        self.system_prompt = system_prompt or f"You are {name}, a specialized AI agent."

    @abstractmethod
    def process(self, state: UnifiedState) -> UnifiedState:
        """Process state and return updated state."""
        pass

    def _make_prompt(self, user_input: str) -> str:
        """Combine system prompt with user input."""
        return f"{self.system_prompt}\n\nUser: {user_input}"

    def log_interaction(self, input_text: str, output_text: str) -> None:
        """Log agent interaction to memory."""
        from src.core import Memory
        from datetime import datetime
        import uuid

        memory = Memory(
            id=f"{self.name}_{uuid.uuid4().hex[:8]}",
            content=f"Input: {input_text}\nOutput: {output_text}",
            memory_type="experience",
            source=self.name,
        )
        self.memory.add_working_memory(memory)

    def __call__(self, state: UnifiedState) -> UnifiedState:
        """Make agent callable like a LangGraph node."""
        return self.process(state)
