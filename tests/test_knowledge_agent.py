"""Tests for Knowledge Agent and Knowledge Base."""
import pytest
from src.core import LLMProvider, MemoryManager, UnifiedState
from src.agents import KnowledgeAgent
from src.knowledge import KnowledgeBase, Fact, KnowledgeSource, SemanticRetriever


class FakeLLM(LLMProvider):
    """Fake LLM for deterministic testing."""

    def generate(self, prompt: str, **kwargs) -> str:
        if "knowledge" in prompt.lower():
            return (
                "RELEVANT_FACTS: 3\n"
                "CONTEXT_SUMMARY: Found relevant information about AI and ML.\n"
                "KNOWLEDGE_GAPS: Missing details on specific algorithms.\n"
                "CONFIDENCE: 75"
            )
        return "RELEVANT_FACTS: 0\nCONTEXT_SUMMARY: No context.\nKNOWLEDGE_GAPS: Everything.\nCONFIDENCE: 0"

    def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict:
        return {"test": "structured"}

    def embedding(self, text: str) -> list[float]:
        return [0.1] * 768


def test_knowledge_base_creation():
    """Test creating and managing knowledge base."""
    kb = KnowledgeBase()

    fact = Fact(
        id="fact1",
        content="Artificial Intelligence is transforming technology",
        topic="ai",
        source=KnowledgeSource.DOCUMENT,
        confidence=0.95,
        tags=["ai", "technology"]
    )

    kb.add_fact(fact)
    assert "fact1" in kb.facts
    assert len(kb.query_by_topic("ai")) == 1
    assert len(kb.query_by_tag("ai")) == 1


def test_knowledge_base_retrieval():
    """Test knowledge base retrieval methods."""
    kb = KnowledgeBase()

    # Add multiple facts
    for i in range(5):
        fact = Fact(
            id=f"fact{i}",
            content=f"Information about topic {i}",
            topic=f"topic{i % 2}",
            source=KnowledgeSource.USER_INPUT,
            confidence=0.8 + (i * 0.02),
            tags=[f"tag{i}", "general"]
        )
        kb.add_fact(fact)

    # Test topic retrieval
    topic_facts = kb.query_by_topic("topic0", limit=10)
    assert len(topic_facts) >= 2

    # Test tag retrieval
    tag_facts = kb.query_by_tag("general", limit=10)
    assert len(tag_facts) == 5

    # Test statistics
    stats = kb.get_statistics()
    assert stats["total_facts"] == 5
    assert stats["topics"] == 2


def test_knowledge_base_search():
    """Test content search in knowledge base."""
    kb = KnowledgeBase()

    fact1 = Fact(
        id="fact1",
        content="Machine learning is a subset of AI",
        topic="ml",
        source=KnowledgeSource.DOCUMENT,
        confidence=0.9
    )
    fact2 = Fact(
        id="fact2",
        content="Deep learning uses neural networks",
        topic="dl",
        source=KnowledgeSource.DOCUMENT,
        confidence=0.85
    )

    kb.add_fact(fact1)
    kb.add_fact(fact2)

    # Search for "learning"
    results = kb.search_by_content("learning", limit=10)
    assert len(results) == 2
    assert results[0].id == "fact1"  # Higher confidence first


def test_semantic_retriever():
    """Test semantic retrieval."""
    kb = KnowledgeBase()

    # Add facts
    facts = [
        Fact(
            id="f1",
            content="Renewable energy includes solar, wind, and hydro power",
            topic="renewable",
            source=KnowledgeSource.DOCUMENT,
            tags=["energy", "renewable"]
        ),
        Fact(
            id="f2",
            content="Solar panels convert sunlight into electricity",
            topic="solar",
            source=KnowledgeSource.DOCUMENT,
            tags=["solar", "renewable"]
        ),
    ]

    for fact in facts:
        kb.add_fact(fact)

    retriever = SemanticRetriever(kb)

    # Test retrieval
    results = retriever.retrieve("solar energy", limit=5)
    assert len(results) > 0

    # Test entity-based retrieval
    entity_results = retriever.retrieve_by_entities(["solar", "energy"])
    assert "solar" in entity_results
    assert len(entity_results["solar"]) > 0


def test_knowledge_agent():
    """Test Knowledge Agent processing."""
    llm = FakeLLM()
    memory = MemoryManager()
    kb = KnowledgeBase()

    # Add some facts to knowledge base
    fact = Fact(
        id="test_fact",
        content="Knowledge agents retrieve contextual information",
        topic="knowledge",
        source=KnowledgeSource.DOCUMENT,
        confidence=0.9,
        tags=["knowledge", "agent"]
    )
    kb.add_fact(fact)

    agent = KnowledgeAgent(name="Knowledge", llm=llm, memory=memory, knowledge_base=kb)

    # Test processing
    state: UnifiedState = {
        "raw_input": "Tell me about knowledge management",
        "parsed_intent": "knowledge_retrieval",
        "entities": ["knowledge", "management"],
        "agent_chain": ["NLP"],
    }

    result = agent.process(state)

    assert result.get("parsed_intent") == "knowledge_retrieval"
    assert "knowledge_context" in result
    assert result.get("current_stage").value == "knowledge_retrieval"
    assert "NLP" in result.get("agent_chain", [])
    assert "Knowledge" in result.get("agent_chain", [])


def test_knowledge_agent_fact_addition():
    """Test adding facts through knowledge agent."""
    llm = FakeLLM()
    memory = MemoryManager()
    kb = KnowledgeBase()

    agent = KnowledgeAgent(name="Knowledge", llm=llm, memory=memory, knowledge_base=kb)

    # Add a fact
    fact_id = agent.add_fact(
        content="Test fact content",
        topic="test_topic",
        confidence=0.85,
        tags=["test", "example"]
    )

    assert fact_id in kb.facts
    assert kb.facts[fact_id].content == "Test fact content"
    assert kb.facts[fact_id].confidence == 0.85


def test_knowledge_agent_statistics():
    """Test knowledge agent statistics."""
    llm = FakeLLM()
    memory = MemoryManager()
    kb = KnowledgeBase()

    agent = KnowledgeAgent(name="Knowledge", llm=llm, memory=memory, knowledge_base=kb)

    # Add multiple facts
    for i in range(3):
        agent.add_fact(f"Fact {i}", f"topic{i}", confidence=0.8 + i * 0.05)

    stats = agent.get_knowledge_stats()
    assert stats["total_facts"] == 3
    assert stats["topics"] >= 1


def test_knowledge_base_linking():
    """Test linking related facts."""
    kb = KnowledgeBase()

    fact1 = Fact(
        id="f1",
        content="Fact one",
        topic="topic1",
        source=KnowledgeSource.DOCUMENT
    )
    fact2 = Fact(
        id="f2",
        content="Fact two",
        topic="topic1",
        source=KnowledgeSource.DOCUMENT
    )

    kb.add_fact(fact1)
    kb.add_fact(fact2)

    # Link facts
    kb.link_facts("f1", "f2")

    # Verify linking
    related = kb.get_related_facts("f1")
    assert len(related) == 1
    assert related[0].id == "f2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
