"""Consciousness Agent - Wraps Neus consciousness modules."""
from src.agents.base_agent import BaseAgent
from src.core import UnifiedState, ProcessingStage
from typing import Optional


class NeusConsciousnessAgent(BaseAgent):
    """Consciousness Agent using Neus consciousness modules.

    Integrates:
    - Attention & focus control
    - Metacognition & self-monitoring
    - Self-model & introspection
    """

    def __init__(self, *args, neus_core=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.neus_core = neus_core
        self.system_prompt = """You are the Consciousness Agent.
Your role is to:
1. Monitor system attention and focus
2. Perform metacognitive reflection
3. Maintain self-model of capabilities
4. Evaluate decision quality

Return your analysis in this format:
ATTENTION_FOCUS: <current focus area>
METACOGNITION: <reflection on reasoning process>
SELF_MODEL: <assessment of system capabilities>
CONFIDENCE: <0-100 confidence in self-assessment>"""

    def process(self, state: UnifiedState) -> UnifiedState:
        """Process through consciousness pipeline."""
        # Get current context
        current_intent = state.get("parsed_intent", "")
        knowledge_context = state.get("knowledge_context", "")

        if not current_intent:
            state["error"] = "No intent to process"
            return state

        # Build prompt for consciousness evaluation
        prompt = self._make_prompt(
            f"""Evaluate this processing request:
Intent: {current_intent}
Context: {knowledge_context[:200]}...

Assess the system's attention, metacognitive state, and self-model."""
        )

        response = self.llm.generate(prompt)
        attention, metacognition, self_model, confidence = self._parse_response(response)

        # Log interaction
        self.log_interaction(current_intent, response)

        # Update state with consciousness data
        state.update({
            "attention_focus": attention,
            "metacognition": metacognition,
            "self_model": self_model,
            "consciousness_confidence": confidence,
            "current_stage": ProcessingStage.REASONING,
            "agent_chain": state.get("agent_chain", []) + [self.name],
        })

        return state

    def _parse_response(self, response: str) -> tuple[str, str, str, int]:
        """Parse consciousness evaluation response."""
        attention = ""
        metacognition = ""
        self_model = ""
        confidence = 50

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("ATTENTION_FOCUS:"):
                attention = line.split(":", 1)[1].strip()
            elif line.startswith("METACOGNITION:"):
                metacognition = line.split(":", 1)[1].strip()
            elif line.startswith("SELF_MODEL:"):
                self_model = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = int(line.split(":", 1)[1].strip().rstrip("%"))
                except (ValueError, IndexError):
                    confidence = 50

        return attention, metacognition, self_model, confidence

    def get_consciousness_state(self) -> dict:
        """Get current consciousness state snapshot."""
        return {
            "type": "consciousness",
            "status": "active",
            "description": "System is conscious of its own reasoning"
        }
