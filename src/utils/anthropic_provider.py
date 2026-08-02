"""Anthropic Claude LLM provider implementation."""
from src.core import LLMProvider
from typing import Optional
import json


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API implementation."""

    def __init__(self, model: str = "claude-opus-5", api_key: Optional[str] = None):
        self.model = model
        try:
            from anthropic import Anthropic

            self.client = Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError(
                "anthropic not installed. Install with: pip install anthropic"
            )

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text from prompt."""
        message = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get("max_tokens", 1024),
            messages=[{"role": "user", "content": prompt}],
        )
        if message.content:
            return message.content[0].text.strip()
        return ""

    def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict:
        """Generate structured output matching schema."""
        structured_prompt = f"""{prompt}

Please respond in valid JSON format matching this schema:
{json.dumps(schema, indent=2)}"""

        response = self.generate(structured_prompt, **kwargs)
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"output": response, "raw": response, "parse_error": True}

    def embedding(self, text: str) -> list[float]:
        """Generate embeddings using Claude's models."""
        # Claude's embedding models via API
        raise NotImplementedError(
            "Use a dedicated embedding model instead. "
            "Consider: sentence-transformers, OpenAI embeddings, etc."
        )
