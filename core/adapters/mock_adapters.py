from core.adapters.base_adapter import BaseAdapter

class MockGPTAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="MockGPT", model="gpt-4-turbo-mock")

    def generate_response(self, prompt: str, **kwargs) -> str:
        self._record_call(True)
        return f"[GPT-Style Response] Processed: '{prompt[:50]}...'"

class MockClaudeAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="MockClaude", model="claude-3-sonnet-mock")

    def generate_response(self, prompt: str, **kwargs) -> str:
        self._record_call(True)
        return f"[Claude-Style Response] Thoughtful: '{prompt[:50]}...'"

class MockGeminiAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="MockGemini", model="gemini-pro-mock")

    def generate_response(self, prompt: str, **kwargs) -> str:
        self._record_call(True)
        return f"[Gemini-Style Response] Strategic: '{prompt[:50]}...'"

class MockLlamaAdapter(BaseAdapter):
    def __init__(self):
        super().__init__(name="MockLlama", model="llama-3-mock")

    def generate_response(self, prompt: str, **kwargs) -> str:
        self._record_call(True)
        return f"[Llama-Style Response] Practical: '{prompt[:50]}...'"

def create_mock_adapters():
    return [
        MockGPTAdapter(),
        MockClaudeAdapter(),
        MockGeminiAdapter(),
        MockLlamaAdapter()
    ]
