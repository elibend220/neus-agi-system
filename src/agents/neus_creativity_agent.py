"""Creativity Agent - Wraps Neus creativity modules."""
from src.agents.base_agent import BaseAgent
from src.core import UnifiedState, ProcessingStage


class NeusCreativityAgent(BaseAgent):
    """Creativity Agent using Neus creativity modules.

    Integrates:
    - Generative ideation
    - Analogical reasoning & transfer
    - Conceptual blending
    """

    def __init__(self, *args, neus_core=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.neus_core = neus_core
        self.system_prompt = """You are the Creativity Agent.
Your role is to:
1. Generate novel ideas and approaches
2. Find analogies and transfer concepts
3. Blend concepts creatively
4. Suggest creative solutions

Return your analysis in this format:
CREATIVE_IDEAS: <3-5 novel approaches>
ANALOGIES: <similar problems and solutions>
CONCEPTUAL_BLEND: <merged concepts>
NOVELTY_SCORE: <0-100 novelty assessment>
FEASIBILITY: <practical assessment>"""

    def process(self, state: UnifiedState) -> UnifiedState:
        """Process through creativity pipeline."""
        intent = state.get("parsed_intent", "")
        reasoning = state.get("reasoning", {})

        if not intent:
            state["error"] = "No intent for creativity"
            return state

        # Build prompt for creative thinking
        reasoning_context = reasoning.get("reasoning_path", "") if reasoning else ""

        prompt = self._make_prompt(
            f"""Apply creative thinking to this task:
Intent: {intent}
Current reasoning: {reasoning_context[:200]}...

Generate creative ideas, analogies, and novel approaches."""
        )

        response = self.llm.generate(prompt)
        creative_result = self._parse_creativity(response)

        # Log interaction
        self.log_interaction(intent, response)

        # Update state with creative insights
        state.update({
            "creative_ideas": creative_result.get("ideas", []),
            "analogies": creative_result.get("analogies", []),
            "conceptual_blend": creative_result.get("blend", ""),
            "novelty_score": creative_result.get("novelty", 50),
            "feasibility": creative_result.get("feasibility", ""),
            "current_stage": ProcessingStage.REASONING,
            "agent_chain": state.get("agent_chain", []) + [self.name],
        })

        return state

    def _parse_creativity(self, response: str) -> dict:
        """Parse creativity response."""
        result = {
            "ideas": [],
            "analogies": [],
            "blend": "",
            "novelty": 50,
            "feasibility": ""
        }

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("CREATIVE_IDEAS:"):
                ideas_text = line.split(":", 1)[1].strip()
                result["ideas"] = [i.strip() for i in ideas_text.split(",") if i.strip()]
            elif line.startswith("ANALOGIES:"):
                analogies_text = line.split(":", 1)[1].strip()
                result["analogies"] = [a.strip() for a in analogies_text.split(",") if a.strip()]
            elif line.startswith("CONCEPTUAL_BLEND:"):
                result["blend"] = line.split(":", 1)[1].strip()
            elif line.startswith("NOVELTY_SCORE:"):
                try:
                    result["novelty"] = int(line.split(":", 1)[1].strip().rstrip("%"))
                except (ValueError, IndexError):
                    result["novelty"] = 50
            elif line.startswith("FEASIBILITY:"):
                result["feasibility"] = line.split(":", 1)[1].strip()

        return result
