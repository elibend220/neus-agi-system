#!/usr/bin/env python3
"""
Integrated Neus + AGI Framework Demo.

Shows full pipeline:
NLP → Knowledge → Consciousness → Reasoning → Creativity
"""

import sys
from src.core import MemoryManager, UnifiedState
from src.agents import (
    NLPAgent,
    KnowledgeAgent,
    NeusConsciousnessAgent,
    NeusReasoningAgent,
    NeusCreativityAgent,
)
from src.coordinator import AgentCoordinator
from src.knowledge import KnowledgeBase, Fact, KnowledgeSource
from src.utils import OllamaProvider, AnthropicProvider


def demo_integrated_pipeline(use_claude=False):
    """Demonstrate full integrated Neus + AGI pipeline."""
    print("=" * 70)
    print("🚀 INTEGRATED NEUS + AGI FRAMEWORK DEMO")
    print("=" * 70)
    print()

    # Initialize LLM
    try:
        if use_claude:
            llm = AnthropicProvider(model="claude-opus-5")
            print("📡 Using Claude (Anthropic)")
        else:
            llm = OllamaProvider(model="llama3.1")
            print("📡 Using Ollama (Local)")
    except Exception as e:
        print(f"❌ LLM Error: {e}")
        return

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

    # Set pipeline: Phase 1 → Phase 2 → Phase 3
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
    print(f"  Context: {state.get('knowledge_synthesis', 'N/A')}")
    print(f"  Confidence: {state.get('knowledge_confidence', 0)}%")
    print(f"  Facts Found: {len(state.get('relevant_facts', []))}")
    print()

    # Phase 3a: Consciousness
    print("🧠 Phase 3a: Consciousness")
    print(f"  Attention Focus: {state.get('attention_focus', 'N/A')}")
    print(f"  Metacognition: {state.get('metacognition', 'N/A')}")
    print(f"  Self-Model: {state.get('self_model', 'N/A')}")
    print()

    # Phase 3b: Reasoning
    print("🤔 Phase 3b: Multi-Modal Reasoning")
    print(f"  Causal: {state.get('causal_analysis', 'N/A')[:100]}...")
    print(f"  Logical: {state.get('logical_conclusions', 'N/A')[:100]}...")
    print(f"  Probability: {state.get('probabilistic_score', 50)}%")
    print()

    # Phase 3c: Creativity
    print("💡 Phase 3c: Creative Solutions")
    ideas = state.get('creative_ideas', [])
    if ideas:
        for i, idea in enumerate(ideas[:3], 1):
            print(f"  Idea {i}: {idea}")
    print(f"  Novelty Score: {state.get('novelty_score', 50)}/100")
    print()

    # Agent Chain
    print("🔗 Agent Chain:")
    print(f"  {' → '.join(state.get('agent_chain', []))}")
    print()

    # Stats
    print("📈 System Statistics:")
    print(f"  Total Agents: {len(agents)}")
    print(f"  Knowledge Base Size: {knowledge_base.get_statistics()['total_facts']}")
    print(f"  Processing Stages: {state.get('current_stage', 'unknown')}")
    print()

    print("=" * 70)
    print("✅ INTEGRATED PIPELINE COMPLETE")
    print("=" * 70)


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
            content="Solar energy converts sunlight directly into electricity, reducing carbon emissions.",
            topic="solar_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.94,
            tags=["solar", "renewable", "carbon_neutral"]
        ),
        Fact(
            id="f3",
            content="Wind energy is one of the fastest-growing renewable energy sources globally.",
            topic="wind_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.93,
            tags=["wind", "renewable", "growth"]
        ),
        Fact(
            id="f4",
            content="Renewable energy reduces reliance on fossil fuels and mitigates climate change.",
            topic="sustainability",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.96,
            tags=["sustainability", "climate", "environment"]
        ),
    ]

    for fact in facts:
        kb.add_fact(fact)


if __name__ == "__main__":
    use_claude = len(sys.argv) > 1 and sys.argv[1] == "--claude"
    demo_integrated_pipeline(use_claude=use_claude)
