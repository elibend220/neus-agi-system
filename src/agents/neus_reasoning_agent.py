"""Reasoning Agent - Wraps Neus reasoning modules."""
from src.agents.base_agent import BaseAgent
from src.core import UnifiedState, ProcessingStage


class NeusReasoningAgent(BaseAgent):
    """Reasoning Agent using Neus reasoning modules.

    Integrates multiple reasoning types:
    - Causal reasoning & intervention
    - Abstract pattern recognition
    - Logical inference & validation
    - Probabilistic reasoning
    - Common-sense reasoning
    """

    def __init__(self, *args, neus_core=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.neus_core = neus_core
        self.reasoning_types = [
            "causal",
            "abstract",
            "logical",
            "probabilistic",
            "common_sense"
        ]
        self.system_prompt = """You are the Reasoning Agent with multi-modal reasoning.
Your role is to:
1. Identify causal relationships
2. Apply abstract pattern recognition
3. Perform logical inference
4. Consider probabilistic outcomes
5. Apply common-sense reasoning

Return your analysis in this format:
CAUSAL: <causal analysis>
PATTERNS: <identified patterns>
LOGICAL: <logical conclusions>
PROBABILITY: <probabilistic assessment (0-100)>
COMMON_SENSE: <common-sense judgment>
REASONING_PATH: <step-by-step reasoning>"""

    def process(self, state: UnifiedState) -> UnifiedState:
        """Process through multi-modal reasoning pipeline."""
        intent = state.get("parsed_intent", "")
        entities = state.get("entities", [])
        knowledge = state.get("knowledge_context", "")

        if not intent:
            state["error"] = "No intent for reasoning"
            return state

        # Build comprehensive reasoning prompt
        prompt = self._make_prompt(
            f"""Apply multi-modal reasoning to this task:
Intent: {intent}
Entities: {', '.join(entities) if entities else 'none'}
Context: {knowledge[:300]}...

Provide causal, logical, probabilistic, and common-sense analysis."""
        )

        response = self.llm.generate(prompt)
        reasoning_result = self._parse_reasoning(response)

        # Log interaction
        self.log_interaction(intent, response)

        # Update state with reasoning
        state.update({
            "reasoning": reasoning_result,
            "causal_analysis": reasoning_result.get("causal", ""),
            "patterns": reasoning_result.get("patterns", ""),
            "logical_conclusions": reasoning_result.get("logical", ""),
            "probabilistic_score": reasoning_result.get("probability", 50),
            "common_sense": reasoning_result.get("common_sense", ""),
            "reasoning_path": reasoning_result.get("reasoning_path", ""),
            "current_stage": ProcessingStage.REASONING,
            "agent_chain": state.get("agent_chain", []) + [self.name],
        })

        return state

    def _parse_reasoning(self, response: str) -> dict:
        """Parse multi-modal reasoning response."""
        result = {
            "causal": "",
            "patterns": "",
            "logical": "",
            "probability": 50,
            "common_sense": "",
            "reasoning_path": ""
        }

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("CAUSAL:"):
                result["causal"] = line.split(":", 1)[1].strip()
            elif line.startswith("PATTERNS:"):
                result["patterns"] = line.split(":", 1)[1].strip()
            elif line.startswith("LOGICAL:"):
                result["logical"] = line.split(":", 1)[1].strip()
            elif line.startswith("PROBABILITY:"):
                try:
                    result["probability"] = int(line.split(":", 1)[1].strip().rstrip("%"))
                except (ValueError, IndexError):
                    result["probability"] = 50
            elif line.startswith("COMMON_SENSE:"):
                result["common_sense"] = line.split(":", 1)[1].strip()
            elif line.startswith("REASONING_PATH:"):
                result["reasoning_path"] = line.split(":", 1)[1].strip()

        return result

    def get_reasoning_stats(self) -> dict:
        """Get statistics about reasoning quality."""
        return {
            "reasoning_types": self.reasoning_types,
            "status": "multi-modal reasoning enabled"
        }
