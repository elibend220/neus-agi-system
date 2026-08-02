"""Tests for AGI system components."""
import pytest
from src.core import LLMProvider, MemoryManager, Memory, UnifiedState
from src.agents import NLPAgent
from src.coordinator import AgentCoordinator


class FakeLLM(LLMProvider):
    """Fake LLM for deterministic testing."""

    def __init__(self, responses: dict = None):
        self.responses = responses or {}
        self.call_count = 0

    def generate(self, prompt: str, **kwargs) -> str:
        self.call_count += 1
        for key in self.responses:
            if key.lower() in prompt.lower():
                return self.responses[key]
        return "INTENT: default\nENTITIES: test\nSUMMARY: test response"

    def generate_structured(self, prompt: str, schema: dict, **kwargs) -> dict:
        return {"test": "structured"}

    def embedding(self, text: str) -> list[float]:
        return [0.1] * 768


def test_memory_manager():
    """Test memory management."""
    memory = MemoryManager(max_working_memory=2)

    # Add to working memory
    mem1 = Memory(id="1", content="first", memory_type="fact")
    mem2 = Memory(id="2", content="second", memory_type="fact")
    mem3 = Memory(id="3", content="third", memory_type="fact")

    memory.add_working_memory(mem1)
    memory.add_working_memory(mem2)
    assert len(memory.working_memory) == 2

    # Adding more should move oldest to long-term
    memory.add_working_memory(mem3)
    assert len(memory.working_memory) == 2
    assert "1" in memory.long_term_memory
    assert len(memory.long_term_memory) == 1


def test_nlp_agent():
    """Test NLP agent processing."""
    llm = FakeLLM(
        {
            "test": "INTENT: analyze text\nENTITIES: entity1, entity2\nSUMMARY: This is a test"
        }
    )
    memory = MemoryManager()
    agent = NLPAgent(name="NLP", llm=llm, memory=memory)

    state: UnifiedState = {"raw_input": "Test input text"}
    result = agent.process(state)

    assert result.get("parsed_intent") == "analyze text"
    assert "entity1" in result.get("entities", [])
    assert result.get("current_stage").value == "nlp_processing"


def test_coordinator_pipeline():
    """Test multi-agent coordination."""
    llm = FakeLLM()
    memory = MemoryManager()
    nlp_agent = NLPAgent(name="NLP", llm=llm, memory=memory)

    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)
    coordinator.set_pipeline(["NLP"])

    result = coordinator.process("Test input")

    assert result.get("raw_input") == "Test input"
    assert "NLP" in result.get("agent_chain", [])
    assert "parsed_intent" in result


def test_state_preservation():
    """Test that state is properly preserved through pipeline."""
    llm = FakeLLM()
    memory = MemoryManager()
    nlp_agent = NLPAgent(name="NLP", llm=llm, memory=memory)

    coordinator = AgentCoordinator(llm=llm, memory=memory)
    coordinator.register_agent(nlp_agent)
    coordinator.set_pipeline(["NLP"])

    initial_state: UnifiedState = {
        "raw_input": "Test",
        "input_type": "text",
    }

    result = coordinator.process(initial_state.get("raw_input", ""))

    # Original input should be preserved
    assert result.get("raw_input") == "Test"
    assert result.get("input_type") == "text"
    # New fields should be added
    assert "parsed_intent" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
