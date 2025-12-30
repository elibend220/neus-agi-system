# agents/agent_v2_5.py
from time import sleep
from agents.agent_base import AgentBase

class AgentV2_5:
    """Lightweight periodic runner using the core dispatcher via CoreManager."""
    def __init__(self, core):
        self.core = core

    def run(self, interval: int = 60):
        # Run a single step then return (non-daemon) to keep CLI responsive
        prompt = "Write a concise hello world function in Python"
        out = self.core.process(prompt)
        print(out)
        # Optional wait to mimic periodic behavior
        if interval and interval > 0:
            sleep(0.1)
