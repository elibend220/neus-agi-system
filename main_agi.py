#!/usr/bin/env python3
"""
AGI System - Main entry point demonstrating the new architecture.

This shows how to:
1. Initialize LLM providers
2. Set up memory management
3. Create and register agents
4. Configure multi-agent coordination
5. Run the AGI pipeline
"""

import sys
from src.core import MemoryManager, UnifiedState
from src.agents import NLPAgent
from src.coordinator import AgentCoordinator
from src.graph import GraphBuilder
from src.utils import OllamaProvider, AnthropicProvider


def setup_agi_with_ollama(article_text: str):
    """Set up AGI pipeline using Ollama (local)."""
    print("🚀 Initializing AGI with Ollama...\n")

    # 1. Initialize LLM provider (Ollama)
    try:
        llm = OllamaProvider(model="llama3.1")
    except Exception as e:
        print(f"❌ Ollama provider error: {e}")
        print("Make sure Ollama is running: ollama serve")
        return None

    # 2. Initialize memory manager
    memory = MemoryManager(max_working_memory=10)

    # 3. Create agents
    nlp_agent = NLPAgent(name="NLP_Agent", llm=llm, memory=memory)

    # 4. Set up coordinator
    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)
    coordinator.set_pipeline(["NLP_Agent"])

    # 5. Process input
    print(f"📝 Processing: {article_text[:100]}...\n")
    state = coordinator.process(article_text, input_type="text")

    print("\n✅ Processing complete!")
    print(f"Intent: {state.get('parsed_intent', 'N/A')}")
    print(f"Entities: {state.get('entities', [])}")
    print(f"Summary: {state.get('summary', 'N/A')}")
    print(f"Agent Chain: {' -> '.join(state.get('agent_chain', []))}")

    return state


def setup_agi_with_anthropic(article_text: str):
    """Set up AGI pipeline using Anthropic Claude."""
    print("🚀 Initializing AGI with Claude (Anthropic)...\n")

    # 1. Initialize LLM provider (Anthropic)
    try:
        llm = AnthropicProvider(model="claude-opus-5")
    except Exception as e:
        print(f"❌ Anthropic provider error: {e}")
        print("Make sure ANTHROPIC_API_KEY is set")
        return None

    # 2. Initialize memory manager
    memory = MemoryManager(max_working_memory=10)

    # 3. Create agents
    nlp_agent = NLPAgent(name="NLP_Agent", llm=llm, memory=memory)

    # 4. Set up coordinator
    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)
    coordinator.set_pipeline(["NLP_Agent"])

    # 5. Process input
    print(f"📝 Processing: {article_text[:100]}...\n")
    state = coordinator.process(article_text, input_type="text")

    print("\n✅ Processing complete!")
    print(f"Intent: {state.get('parsed_intent', 'N/A')}")
    print(f"Entities: {state.get('entities', [])}")
    print(f"Summary: {state.get('summary', 'N/A')}")
    print(f"Agent Chain: {' -> '.join(state.get('agent_chain', []))}")

    return state


def demo_langgraph_integration():
    """Demonstrate LangGraph integration."""
    print("\n" + "=" * 60)
    print("🔗 LangGraph Integration Demo")
    print("=" * 60 + "\n")

    llm = OllamaProvider(model="llama3.1")
    memory = MemoryManager()
    nlp_agent = NLPAgent(name="NLP_Agent", llm=llm, memory=memory)

    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)
    coordinator.set_pipeline(["NLP_Agent"])

    # Build LangGraph
    graph_builder = GraphBuilder(coordinator)
    graph = graph_builder.build_multi_stage()

    # Execute through LangGraph
    initial_state: UnifiedState = {
        "raw_input": "Tell me about artificial intelligence",
        "input_type": "text",
    }

    result = graph.invoke(initial_state)
    print(f"LangGraph output: {result.get('parsed_intent', 'N/A')}")


if __name__ == "__main__":
    article = """
    Artificial Intelligence continues to evolve rapidly. Recent advances in
    transformer-based models have enabled machines to understand and generate
    human language with unprecedented accuracy. This opens new possibilities
    for human-computer interaction and automated decision-making systems.
    """

    if len(sys.argv) > 1 and sys.argv[1] == "--claude":
        setup_agi_with_anthropic(article)
    else:
        setup_agi_with_ollama(article)
