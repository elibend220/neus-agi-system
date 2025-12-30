# agents/agent_base.py

class AgentBase:
    """
    Base class for any NEUS-AGI agent.
    """

    def __init__(self, adapter):
        self.adapter = adapter

    def ask(self, prompt: str) -> str:
        response = self.adapter.send(prompt)
        return response

    def info(self):
        return f"Agent using adapter: {self.adapter.name()}"
