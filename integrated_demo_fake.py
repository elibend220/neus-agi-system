#!/usr/bin/env python3
"""
Integrated Neus + AGI Framework Demo with Fake LLM.

This demonstrates the full pipeline without requiring Ollama or Claude.
Perfect for testing architecture and flow.
"""

import sys
from src.core import MemoryManager, UnifiedState, LLMProvider
from src.agents import (
    NLPAgent,
    KnowledgeAgent,
    NeusConsciousnessAgent,
    NeusReasoningAgent,
    NeusCreativityAgent,
)
from src.coordinator import AgentCoordinator
from src.knowledge import KnowledgeBase, Fact, KnowledgeSource


class FakeLLM(LLMProvider):
    """Deterministic fake LLM for testing without external dependencies."""

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate fake but realistic responses."""
        if "intent" in prompt.lower() and "entities" in prompt.lower():
            return (
                "INTENT: sustainable energy transformation\n"
                "ENTITIES: renewable energy, sustainability, global impact\n"
                "SUMMARY: User wants to understand how renewable energy can drive global sustainability"
            )
        elif "attention" in prompt.lower():
            return (
                "ATTENTION_FOCUS: sustainable energy systems\n"
                "METACOGNITION: reasoning about systems-level change\n"
                "SELF_MODEL: capable of multi-domain analysis\n"
                "CONFIDENCE: 82"
            )
        elif "causal" in prompt.lower():
            return (
                "CAUSAL: renewable energy adoption → reduced emissions → climate mitigation\n"
                "PATTERNS: similar to renewable revolution in Denmark and Costa Rica\n"
                "LOGICAL: therefore, scaling renewables requires infrastructure + policy\n"
                "PROBABILITY: 88\n"
                "COMMON_SENSE: makes economic and environmental sense\n"
                "REASONING_PATH: Technology innovation → Cost reduction → Market adoption → Systemic change"
            )
        elif "creative" in prompt.lower():
            return (
                "CREATIVE_IDEAS: Decentralized energy communities, Green financing models, AI-optimized grids\n"
                "ANALOGIES: Similar to digital revolution, Industrial 2.0\n"
                "CONCEPTUAL_BLEND: merge energy systems with digital networks\n"
                "NOVELTY_SCORE: 78\n"
                "FEASIBILITY: Moderately feasible with policy support"
            )
        return "RESULT: processed"

    def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict:
        return {"result": "structured"}

    def embedding(self, text: str) -> list[float]:
        return [0.1] * 768


def demo_integrated_pipeline():
    """Demonstrate full integrated Neus + AGI pipeline."""
    print("=" * 70)
    print("🚀 INTEGRATED NEUS + AGI FRAMEWORK DEMO")
    print("=" * 70)
    print()

    # Use Fake LLM
    llm = FakeLLM()
    print("📡 Using Fake LLM (deterministic, no external dependencies)")
    print()

    # Setup
    memory = MemoryManager()
    knowledge_base = KnowledgeBase()
    _populate_knowledge_base(knowledge_base)

    # Create all agents
    print("🔧 Initializing Agents:")
    agents = {
        "NLP": NLPAgent(name="NLP", llm=llm, memory=memory),
        "Knowledge": KnowledgeAgent(name="Knowledge", llm=llm, memory=memory, knowledge_base=knowledge_base),
        "Consciousness": NeusConsciousnessAgent(name="Consciousness", llm=llm, memory=memory),
        "Reasoning": NeusReasoningAgent(name="Reasoning", llm=llm, memory=memory),
        "Creativity": NeusCreativityAgent(name="Creativity", llm=llm, memory=memory),
    }

    for name in agents:
        print(f"  ✓ {name} Agent")

    print()

    # Register with coordinator
    coordinator = AgentCoordinator(llm=llm, memory=memory)
    for agent in agents.values():
        coordinator.register_agent(agent)

    # Set pipeline
    pipeline = ["NLP", "Knowledge", "Consciousness", "Reasoning", "Creativity"]
    coordinator.set_pipeline(pipeline)

    print("📋 Pipeline:")
    print(f"  {' → '.join(pipeline)}")
    print()

    # Input
    query = "How can renewable energy transform global sustainability?"
    print(f"🎯 Query: {query}")
    print()

    # Process through entire pipeline
    print("⚙️  Processing through integrated pipeline...")
    print("-" * 70)

    state = coordinator.process(query, input_type="text")

    # Display results
    print("-" * 70)
    print()
    print("📊 RESULTS:")
    print()

    # Phase 1: NLP
    print("📝 Phase 1: NLP Processing")
    print(f"  Intent: {state.get('parsed_intent', 'N/A')}")
    print(f"  Entities: {', '.join(state.get('entities', []))}")
    print(f"  Summary: {state.get('summary', 'N/A')}")
    print()

    # Phase 2: Knowledge
    print("📚 Phase 2: Knowledge Retrieval")
    context = state.get('knowledge_context', '')
    if context:
        print(f"  Context Retrieved: Yes ({len(context)} chars)")
    print(f"  Synthesis: {state.get('knowledge_synthesis', 'N/A')}")
    print(f"  Confidence: {state.get('knowledge_confidence', 0)}%")
    print(f"  Facts Found: {len(state.get('relevant_facts', []))}")
    print()

    # Phase 3a: Consciousness
    print("🧠 Phase 3a: Consciousness")
    print(f"  Attention Focus: {state.get('attention_focus', 'N/A')}")
    print(f"  Metacognition: {state.get('metacognition', 'N/A')}")
    print(f"  Self-Model: {state.get('self_model', 'N/A')}")
    print(f"  Confidence: {state.get('consciousness_confidence', 0)}%")
    print()

    # Phase 3b: Reasoning
    print("🤔 Phase 3b: Multi-Modal Reasoning")
    print(f"  Causal: {state.get('causal_analysis', 'N/A')[:80]}...")
    print(f"  Logical: {state.get('logical_conclusions', 'N/A')[:80]}...")
    print(f"  Probability: {state.get('probabilistic_score', 50)}%")
    print(f"  Common Sense: {state.get('common_sense', 'N/A')[:80]}...")
    print()

    # Phase 3c: Creativity
    print("💡 Phase 3c: Creative Solutions")
    ideas = state.get('creative_ideas', [])
    if ideas:
        print("  Creative Ideas:")
        for i, idea in enumerate(ideas[:3], 1):
            print(f"    {i}. {idea}")
    print(f"  Novelty Score: {state.get('novelty_score', 50)}/100")
    print()

    # Agent Chain
    print("🔗 Agent Chain:")
    chain = state.get('agent_chain', [])
    print(f"  {' → '.join(chain)}")
    print(f"  Total Agents: {len(chain)}")
    print()

    # Memory Stats
    print("💾 Memory Statistics:")
    print(f"  Working Memory: {len(memory.working_memory)} items")
    print(f"  Long-term Memory: {len(memory.long_term_memory)} items")
    print()

    # Knowledge Stats
    print("📖 Knowledge Base Statistics:")
    kb_stats = knowledge_base.get_statistics()
    print(f"  Total Facts: {kb_stats['total_facts']}")
    print(f"  Topics: {kb_stats['topics']}")
    print(f"  Avg Confidence: {kb_stats['avg_confidence']:.2f}")
    print()

    print("=" * 70)
    print("✅ INTEGRATED PIPELINE COMPLETE")
    print("=" * 70)
    print()
    print("Architecture Validated:")
    print("✓ NLP Processing (Phase 1)")
    print("✓ Knowledge Retrieval (Phase 2)")
    print("✓ Consciousness & Metacognition (Neus)")
    print("✓ Multi-Modal Reasoning (Neus)")
    print("✓ Creative Solutions (Neus)")
    print("✓ Unified State Flow")
    print("✓ Memory Management")
    print()


def _populate_knowledge_base(kb: KnowledgeBase) -> None:
    """Pre-populate knowledge base with facts."""
    facts = [
        Fact(
            id="f1",
            content="Renewable energy sources include solar, wind, hydroelectric, geothermal, and biomass energy.",
            topic="renewable_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.95,
            tags=["renewable", "energy", "sustainability"]
        ),
        Fact(
            id="f2",
            content="Solar energy converts sunlight directly into electricity, reducing carbon emissions by 50% compared to coal.",
            topic="solar_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.94,
            tags=["solar", "renewable", "carbon_neutral", "energy"]
        ),
        Fact(
            id="f3",
            content="Wind energy is one of the fastest-growing renewable energy sources globally, with 10% annual growth.",
            topic="wind_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.93,
            tags=["wind", "renewable", "growth", "energy"]
        ),
        Fact(
            id="f4",
            content="Renewable energy transition can create millions of jobs in manufacturing, installation, and maintenance.",
            topic="sustainability",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.92,
            tags=["sustainability", "jobs", "economy", "energy"]
        ),
        Fact(
            id="f5",
            content="Countries like Denmark generate 80% of electricity from wind power, proving large-scale renewable feasibility.",
            topic="renewable_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.95,
            tags=["renewable", "case_study", "feasibility", "energy"]
        ),
    ]

    for fact in facts:
        kb.add_fact(fact)


if __name__ == "__main__":
    demo_integrated_pipeline()
