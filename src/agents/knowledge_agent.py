"""Knowledge retrieval and management agent."""
from src.agents.base_agent import BaseAgent
from src.core import UnifiedState, ProcessingStage
from src.knowledge import KnowledgeBase, Fact, KnowledgeSource, SemanticRetriever
import uuid


class KnowledgeAgent(BaseAgent):
    """Knowledge retrieval agent - retrieves and manages contextual information."""

    def __init__(self, *args, knowledge_base: KnowledgeBase = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.knowledge_base = knowledge_base or KnowledgeBase()
        self.retriever = SemanticRetriever(self.knowledge_base)
        self.system_prompt = """You are the Knowledge Agent.
Your role is to:
1. Evaluate relevance of retrieved facts
2. Generate comprehensive context synthesis
3. Identify knowledge gaps
4. Suggest follow-up queries

Return your analysis in this format:
RELEVANT_FACTS: <number of useful facts retrieved>
CONTEXT_SUMMARY: <1-2 sentences synthesizing the knowledge>
KNOWLEDGE_GAPS: <what information is missing>
CONFIDENCE: <0-100 confidence in the context>"""

    def process(self, state: UnifiedState) -> UnifiedState:
        """Process state through knowledge retrieval pipeline."""
        intent = state.get("parsed_intent", "")
        entities = state.get("entities", [])
        raw_input = state.get("raw_input", "")

        if not intent and not entities and not raw_input:
            state["error"] = "No input to process"
            return state

        # Retrieve relevant facts using semantic search
        context = self.retriever.retrieve_context(
            query=raw_input,
            intent=intent,
            entities=entities,
            limit=10
        )

        # Format retrieved facts as context
        knowledge_context = self._format_context(context)

        # Ask LLM to evaluate and synthesize knowledge
        if knowledge_context:
            prompt = self._make_prompt(
                f"Evaluate this retrieved context for: {intent}\n\n{knowledge_context}"
            )
            evaluation = self.llm.generate(prompt)
            relevance, summary, gaps, confidence = self._parse_evaluation(evaluation)
        else:
            relevance = 0
            summary = "No relevant knowledge found"
            gaps = f"No knowledge about {entities or intent}"
            confidence = 0

        # Add new facts from the input to knowledge base
        self._add_input_as_fact(raw_input, intent, entities)

        # Log interaction
        self.log_interaction(raw_input, f"Retrieved {relevance} facts")

        # Update state
        state.update({
            "knowledge_context": knowledge_context,
            "relevant_facts": [f.to_dict() for f in context["combined"]],
            "knowledge_sources": list(set(
                f.source.value for f in context["combined"]
            )),
            "knowledge_synthesis": summary,
            "knowledge_gaps": gaps,
            "knowledge_confidence": confidence,
            "current_stage": ProcessingStage.KNOWLEDGE_RETRIEVAL,
            "agent_chain": state.get("agent_chain", []) + [self.name],
        })

        return state

    def _format_context(self, context: dict) -> str:
        """Format retrieved facts as readable context."""
        if not context["combined"]:
            return ""

        lines = ["## Retrieved Knowledge Context\n"]

        for fact in context["combined"][:5]:  # Top 5 facts
            lines.append(f"- **{fact.topic}** ({fact.source.value}): {fact.content}")

        return "\n".join(lines)

    def _parse_evaluation(self, response: str) -> tuple[int, str, str, int]:
        """Parse LLM evaluation response."""
        relevant = 0
        summary = ""
        gaps = ""
        confidence = 50

        for line in response.splitlines():
            line = line.strip()
            if line.startswith("RELEVANT_FACTS:"):
                try:
                    relevant = int(line.split(":", 1)[1].strip().split()[0])
                except (ValueError, IndexError):
                    relevant = 0
            elif line.startswith("CONTEXT_SUMMARY:"):
                summary = line.split(":", 1)[1].strip()
            elif line.startswith("KNOWLEDGE_GAPS:"):
                gaps = line.split(":", 1)[1].strip()
            elif line.startswith("CONFIDENCE:"):
                try:
                    confidence = int(line.split(":", 1)[1].strip().rstrip("%"))
                except (ValueError, IndexError):
                    confidence = 50

        return relevant, summary, gaps, confidence

    def _add_input_as_fact(
        self, content: str, topic: str, entities: list
    ) -> None:
        """Add input information as a new fact to knowledge base."""
        if not content or not topic:
            return

        fact_id = f"input_{uuid.uuid4().hex[:8]}"
        fact = Fact(
            id=fact_id,
            content=content,
            topic=topic or "general",
            source=KnowledgeSource.USER_INPUT,
            confidence=0.8,
            tags=entities or [],
        )

        self.knowledge_base.add_fact(fact)

    def add_fact(
        self,
        content: str,
        topic: str,
        source: KnowledgeSource = KnowledgeSource.DOCUMENT,
        confidence: float = 1.0,
        tags: list = None,
    ) -> str:
        """Manually add a fact to the knowledge base."""
        fact_id = f"fact_{uuid.uuid4().hex[:8]}"
        fact = Fact(
            id=fact_id,
            content=content,
            topic=topic,
            source=source,
            confidence=confidence,
            tags=tags or [],
        )

        self.knowledge_base.add_fact(fact)
        return fact_id

    def get_knowledge_stats(self) -> dict:
        """Get statistics about the knowledge base."""
        return self.knowledge_base.get_statistics()
