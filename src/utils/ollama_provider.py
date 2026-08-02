"""Ollama LLM provider implementation."""
from src.core import LLMProvider
from typing import Optional


class OllamaProvider(LLMProvider):
    """Ollama local LLM implementation."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url
        try:
            from langchain_ollama.llms import OllamaLLM

            self.client = OllamaLLM(model=model, base_url=base_url)
        except ImportError:
            raise ImportError(
                "langchain-ollama not installed. "
                "Install with: pip install langchain-ollama"
            )

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        response = self.client.invoke(prompt, **kwargs)
        return response.strip() if response else ""

    def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict:
        """Generate structured output (simplified - Ollama doesn't support schemas natively)."""
        # For now, just return raw generation
        # In production, use response parsing libraries
        output = self.generate(prompt, **kwargs)
        return {"output": output, "raw": output}

    def embedding(self, text: str) -> list[float]:
        """Generate embeddings (not supported by all Ollama models)."""
        # This requires embed-specific models or endpoints
        # Simplified implementation
        raise NotImplementedError(
            "Ollama embedding requires embed-specific models. "
            "Use embedding-specialized providers instead."
        )
