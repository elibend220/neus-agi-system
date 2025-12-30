from agents.base_agent import BaseAgent

class AgentV2_5(BaseAgent):
    def __init__(self, core, builder=None):
        super().__init__(core)
        self.builder = builder

    def run(self, interval=60):
        print("NEUS Agent v2.5 (Adaptive Mode) Running...")
        while True:
            user_input = input("Instruction (or 'exit'): ")
            if user_input.lower() == "exit":
                break
            result = self.core.process(user_input)
            print(result)
