"""NLP-first agent for text processing and understanding."""
from src.agents.base_agent import BaseAgent
from src.core import UnifiedState, ProcessingStage


class NLPAgent(BaseAgent):
    """Core NLP processing agent - first stop for all text."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.system_prompt = """You are the NLP Processing Agent.
Your role is to:
1. Understand user intent from raw input
2. Extract key entities and concepts
3. Summarize and clarify the request
4. Prepare context for downstream agents

Return your analysis in this format:
INTENT: <what the user wants>
ENTITIES: <comma-separated key concepts>
SUMMARY: <1-2 sentence summary>"""

    def process(self, state: UnifiedState) -> UnifiedState:
        """Process raw input through NLP pipeline."""
        raw_input = state.get("raw_input", "")

        if not raw_input:
            state["error"] = "No input provided"
            return state

        # Call LLM for NLP analysis
        prompt = self._make_prompt(raw_input)
        response = self.llm.generate(prompt)

        # Parse response
        intent, entities, summary = self._parse_nlp_response(response)

        # Log interaction
        self.log_interaction(raw_input, response)

        # Update state (preserve existing fields)
        state.update({
            "processed_text": raw_input,
            "parsed_intent": intent,
            "entities": entities,
            "summary": summary,
            "current_stage": ProcessingStage.NLP_PROCESSING,
            "agent_chain": state.get("agent_chain", []) + [self.name],
        })
        return state

    def _parse_nlp_response(self, response: str) -> tuple[str, list[str], str]:
        """Parse LLM NLP analysis response."""
        intent = ""
        entities = []
        summary = ""

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("INTENT:"):
                intent = line.split(":", 1)[1].strip()
            elif line.startswith("ENTITIES:"):
                entities = [e.strip() for e in line.split(":", 1)[1].split(",")]
            elif line.startswith("SUMMARY:"):
                summary = line.split(":", 1)[1].strip()

        return intent, entities, summary
