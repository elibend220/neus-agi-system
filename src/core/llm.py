"""Abstract LLM interface - decoupled from any specific provider."""
from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Base interface for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text given a prompt."""
        pass

    @abstractmethod
    def generate_structured(
        self, prompt: str, schema: dict, **kwargs
    ) -> dict:
        """Generate structured output matching a schema."""
        pass

    @abstractmethod
    def embedding(self, text: str) -> list[float]:
        """Generate vector embeddings for text."""
        pass

    def __call__(self, prompt: str) -> str:
        """Make LLMProvider callable like the old interface."""
        return self.generate(prompt)
