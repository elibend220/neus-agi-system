import os
import logging
from core.adapters.base_adapter import BaseAdapter

logger = logging.getLogger(__name__)

class RealClaudeAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, model: str = "claude-3-sonnet-20240229"):
        super().__init__(name="Claude", model=model)
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            logger.warning("No Anthropic API key found. Adapter disabled.")
            self.enabled = False

    def generate_response(self, prompt: str, **kwargs) -> str:
        if not self.enabled:
            return "[Claude Disabled] No API key configured"
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model,
                max_tokens=kwargs.get('max_tokens', 1000),
                messages=[{"role": "user", "content": prompt}]
            )
            result = response.content[0].text
            self._record_call(True)
            return result
        except Exception as e:
            self._record_call(False)
            return f"[Claude Error] {str(e)}"

class RealGPTAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, model: str = "gpt-4-turbo-preview"):
        super().__init__(name="GPT", model=model)
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            logger.warning("No OpenAI API key found. Adapter disabled.")
            self.enabled = False

    def generate_response(self, prompt: str, **kwargs) -> str:
        if not self.enabled:
            return "[GPT Disabled] No API key configured"
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 1000)
            )
            result = response.choices[0].message.content
            self._record_call(True)
            return result
        except Exception as e:
            self._record_call(False)
            return f"[GPT Error] {str(e)}"

class RealGeminiAdapter(BaseAdapter):
    def __init__(self, api_key: str = None, model: str = "gemini-pro"):
        super().__init__(name="Gemini", model=model)
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            logger.warning("No Google API key found. Adapter disabled.")
            self.enabled = False

    def generate_response(self, prompt: str, **kwargs) -> str:
        if not self.enabled:
            return "[Gemini Disabled] No API key configured"
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            result = response.text
            self._record_call(True)
            return result
        except Exception as e:
            self._record_call(False)
            return f"[Gemini Error] {str(e)}"

def create_real_adapters(api_keys: dict = None):
    api_keys = api_keys or {}
    adapters = []
    if api_keys.get('anthropic') or os.getenv('ANTHROPIC_API_KEY'):
        adapters.append(RealClaudeAdapter(api_key=api_keys.get('anthropic')))
    if api_keys.get('openai') or os.getenv('OPENAI_API_KEY'):
        adapters.append(RealGPTAdapter(api_key=api_keys.get('openai')))
    if api_keys.get('google') or os.getenv('GOOGLE_API_KEY'):
        adapters.append(RealGeminiAdapter(api_key=api_keys.get('google')))
    if not adapters:
        logger.warning("No API keys found. No real adapters created.")
    return adapters
