#!/usr/bin/env python3
"""
AGI System - Integrated Neus + AGI Framework.

Demonstrates:
1. Initialize LLM providers
2. Set up memory and knowledge management
3. Create and register all agent types (AGI + Neus)
4. Configure multi-agent coordination
5. Run the full integrated pipeline

Architecture:
Phase 1: NLP Processing (AGI Framework)
Phase 2: Knowledge Retrieval (AGI Framework)
Phase 3: Consciousness/Metacognition (Neus)
Phase 3: Multi-modal Reasoning (Neus)
Phase 3: Creative Solutions (Neus)
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
from src.graph import GraphBuilder
from src.knowledge import KnowledgeBase
from src.utils import OllamaProvider, AnthropicProvider


def setup_agi_with_ollama(article_text: str, include_knowledge: bool = True):
    """Set up AGI pipeline using Ollama (local) with optional Knowledge Agent."""
    print("🚀 Initializing AGI with Ollama...\n")

    # 1. Initialize LLM provider (Ollama)
    try:
        llm = OllamaProvider(model="llama3.1")
    except Exception as e:
        print(f"❌ Ollama provider error: {e}")
        print("Make sure Ollama is running: ollama serve")
        return None

    # 2. Initialize memory manager and knowledge base
    memory = MemoryManager(max_working_memory=10)
    knowledge_base = KnowledgeBase()

    # Pre-populate knowledge base with some facts
    _populate_knowledge_base(knowledge_base)

    # 3. Create agents
    nlp_agent = NLPAgent(name="NLP_Agent", llm=llm, memory=memory)
    knowledge_agent = KnowledgeAgent(
        name="Knowledge_Agent", llm=llm, memory=memory, knowledge_base=knowledge_base
    ) if include_knowledge else None

    # 4. Set up coordinator
    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)

    if knowledge_agent:
        coordinator.register_agent(knowledge_agent)
        coordinator.set_pipeline(["NLP_Agent", "Knowledge_Agent"])
    else:
        coordinator.set_pipeline(["NLP_Agent"])

    # 5. Process input
    print(f"📝 Processing: {article_text[:100]}...\n")
    state = coordinator.process(article_text, input_type="text")

    print("\n✅ Processing complete!")
    print(f"Intent: {state.get('parsed_intent', 'N/A')}")
    print(f"Entities: {state.get('entities', [])}")
    print(f"Summary: {state.get('summary', 'N/A')}")

    if include_knowledge and knowledge_agent:
        print(f"\n📚 Knowledge Retrieved:")
        print(f"  - Context: {state.get('knowledge_synthesis', 'N/A')}")
        print(f"  - Confidence: {state.get('knowledge_confidence', 0)}%")
        print(f"  - Facts Found: {len(state.get('relevant_facts', []))}")
        print(f"  - Gaps: {state.get('knowledge_gaps', 'N/A')}")

    print(f"\nAgent Chain: {' -> '.join(state.get('agent_chain', []))}")
    print(f"Knowledge Stats: {knowledge_agent.get_knowledge_stats() if knowledge_agent else 'N/A'}")

    return state


def setup_agi_with_anthropic(article_text: str, include_knowledge: bool = True):
    """Set up AGI pipeline using Anthropic Claude."""
    print("🚀 Initializing AGI with Claude (Anthropic)...\n")

    # 1. Initialize LLM provider (Anthropic)
    try:
        llm = AnthropicProvider(model="claude-opus-5")
    except Exception as e:
        print(f"❌ Anthropic provider error: {e}")
        print("Make sure ANTHROPIC_API_KEY is set")
        return None

    # 2. Initialize memory manager and knowledge base
    memory = MemoryManager(max_working_memory=10)
    knowledge_base = KnowledgeBase()

    # Pre-populate knowledge base
    _populate_knowledge_base(knowledge_base)

    # 3. Create agents
    nlp_agent = NLPAgent(name="NLP_Agent", llm=llm, memory=memory)
    knowledge_agent = KnowledgeAgent(
        name="Knowledge_Agent", llm=llm, memory=memory, knowledge_base=knowledge_base
    ) if include_knowledge else None

    # 4. Set up coordinator
    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)

    if knowledge_agent:
        coordinator.register_agent(knowledge_agent)
        coordinator.set_pipeline(["NLP_Agent", "Knowledge_Agent"])
    else:
        coordinator.set_pipeline(["NLP_Agent"])

    # 5. Process input
    print(f"📝 Processing: {article_text[:100]}...\n")
    state = coordinator.process(article_text, input_type="text")

    print("\n✅ Processing complete!")
    print(f"Intent: {state.get('parsed_intent', 'N/A')}")
    print(f"Entities: {state.get('entities', [])}")
    print(f"Summary: {state.get('summary', 'N/A')}")

    if include_knowledge and knowledge_agent:
        print(f"\n📚 Knowledge Retrieved:")
        print(f"  - Context: {state.get('knowledge_synthesis', 'N/A')}")
        print(f"  - Confidence: {state.get('knowledge_confidence', 0)}%")
        print(f"  - Facts Found: {len(state.get('relevant_facts', []))}")
        print(f"  - Gaps: {state.get('knowledge_gaps', 'N/A')}")

    print(f"\nAgent Chain: {' -> '.join(state.get('agent_chain', []))}")
    print(f"Knowledge Stats: {knowledge_agent.get_knowledge_stats() if knowledge_agent else 'N/A'}")

    return state


def _populate_knowledge_base(kb: KnowledgeBase) -> None:
    """Pre-populate knowledge base with sample facts."""
    from src.knowledge import Fact, KnowledgeSource

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
            content="Solar panels convert sunlight directly into electricity through the photovoltaic effect.",
            topic="solar_energy",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.95,
            tags=["solar", "renewable", "energy"]
        ),
        Fact(
            id="f3",
            content="Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            topic="machine_learning",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.93,
            tags=["ai", "ml", "technology"]
        ),
        Fact(
            id="f4",
            content="Deep learning uses artificial neural networks with multiple layers for complex pattern recognition.",
            topic="deep_learning",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.92,
            tags=["ai", "neural_networks", "technology"]
        ),
        Fact(
            id="f5",
            content="Natural language processing enables computers to understand and generate human language.",
            topic="nlp",
            source=KnowledgeSource.DOCUMENT,
            confidence=0.91,
            tags=["ai", "nlp", "language"]
        ),
    ]

    for fact in facts:
        kb.add_fact(fact)


def demo_langgraph_integration():
    """Demonstrate LangGraph integration with Knowledge Agent."""
    print("\n" + "=" * 60)
    print("🔗 LangGraph Integration Demo (Phase 1 + 2)")
    print("=" * 60 + "\n")

    llm = OllamaProvider(model="llama3.1")
    memory = MemoryManager()
    knowledge_base = KnowledgeBase()
    _populate_knowledge_base(knowledge_base)

    nlp_agent = NLPAgent(name="NLP_Agent", llm=llm, memory=memory)
    knowledge_agent = KnowledgeAgent(
        name="Knowledge_Agent", llm=llm, memory=memory, knowledge_base=knowledge_base
    )

    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)
    coordinator.register_agent(knowledge_agent)
    coordinator.set_pipeline(["NLP_Agent", "Knowledge_Agent"])

    # Build LangGraph
    graph_builder = GraphBuilder(coordinator)
    graph = graph_builder.build_multi_stage()

    # Execute through LangGraph
    initial_state: UnifiedState = {
        "raw_input": "What are the benefits of renewable energy?",
        "input_type": "text",
    }

    result = graph.invoke(initial_state)
    print(f"🎯 Intent: {result.get('parsed_intent', 'N/A')}")
    print(f"📚 Knowledge Context: {result.get('knowledge_synthesis', 'N/A')}")


if __name__ == "__main__":
    article = """
    Renewable energy is becoming increasingly important as the world transitions
    away from fossil fuels. Solar, wind, and hydroelectric power are the most
    widely deployed renewable sources. These technologies help reduce carbon
    emissions and combat climate change while creating new job opportunities
    in the green energy sector.
    """

    if len(sys.argv) > 1 and sys.argv[1] == "--claude":
        setup_agi_with_anthropic(article, include_knowledge=True)
    elif len(sys.argv) > 1 and sys.argv[1] == "--no-knowledge":
        setup_agi_with_ollama(article, include_knowledge=False)
    else:
        setup_agi_with_ollama(article, include_knowledge=True)
