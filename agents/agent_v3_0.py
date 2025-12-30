# agents/agent_v3_0.py
from time import sleep

class AgentV3_0:
    """Structured reasoning prompt style over CoreManager dispatcher."""
    def __init__(self, core):
        self.core = core

    def run(self, interval: int = 60):
        prompt = (
            "First list 3 short bullets for a tiny plan, then implement a simple sum(a,b) function in Python."
        )
        out = self.core.process(prompt)
        print(out)
        if interval and interval > 0:
            sleep(0.1)
