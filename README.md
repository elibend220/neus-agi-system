![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License: MIT](https://img.shields.io/badge/license-MIT-green)
![GitHub stars](https://img.shields.io/github/stars/elibend220/neus-agi-system)

# neus-agi-system

A production-ready AGI framework for consciousness, reasoning, and multi-domain reasoning. Built with modular agents, unified state management, and LLM-agnostic architecture.

**Status**: Phase 1 (NLP Foundation) ✅ | Phase 2-4 in development

## Quick Start

### Setup
```bash
pip install -r requirements.txt
```

### Using Ollama (Local)
```bash
# Terminal 1: Start Ollama
ollama pull llama3.1
ollama serve

# Terminal 2: Run AGI
python main_agi.py
```

### Using Claude (Anthropic)
```bash
export ANTHROPIC_API_KEY="sk-..."
python main_agi.py --claude
```

## Architecture Overview

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed architecture documentation.

```
┌─────────────────────────────────────────────┐
│         AGI Input (Text/Image/Audio)        │
└────────────────────┬────────────────────────┘
                     │
         ┌───────────▼───────────┐
         │   NLP Processing      │ ← Current Phase
         │  (Intent + Entities)  │
         └───────────┬───────────┘
                     │
         ┌───────────▼──────────────┐
         │ Knowledge Retrieval      │ ← Phase 2
         │ (Semantic Search)        │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │ Reasoning & Planning     │ ← Phase 3
         │ (Multi-step Analysis)    │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │ Execution                │ ← Phase 4
         │ (Tools, Robotics)        │
         └───────────┬──────────────┘
                     │
         ┌───────────▼──────────────┐
         │     AGI Output           │
         │  + Memory Updates        │
         └──────────────────────────┘
```

## Core Principles

1. **NLP-First** - Natural language as universal interface
2. **Modular** - Agents are pluggable, domain-specific processors
3. **State-Driven** - Unified `UnifiedState` flows through all stages
4. **Memory-Centric** - Persistent learning via working + long-term memory
5. **LLM-Agnostic** - Abstract `LLMProvider` supports any backend

## Project Structure

```
src/
├── core/              # Foundation (LLM, Memory, State)
├── agents/            # Specialized processors (NLP, Knowledge, Reasoning, etc.)
├── coordinator/       # Multi-agent orchestration
└── graph/            # LangGraph integration
tests/                # Test suite with fake LLMs
main_agi.py           # Main entry point demo
```

## Phase 1: NLP Foundation (Current)

✅ **Completed:**
- Abstract LLMProvider interface
- Memory management (working + long-term)
- Unified state management
- Base agent class
- NLP agent (intent + entities extraction)
- Multi-agent coordinator
- LangGraph integration
- Ollama support
- Anthropic Claude support

## Phase 2: Knowledge Integration (Q3 2026)

📋 **Planned:**
- Knowledge Agent with semantic search
- Vector database integration
- Fact retrieval and consolidation
- Knowledge graph construction

## Phase 3: Reasoning & Planning (Q4 2026)

📋 **Planned:**
- Reasoning Agent (multi-step analysis)
- Planning Agent (action sequence generation)
- Tree-of-thought reasoning
- Constraint satisfaction

## Phase 4: Execution & Embodiment (2027)

📋 **Planned:**
- Tool use and API integration
- Robotics framework
- Real-world execution
- Continuous learning

## Example Usage

### Simple NLP Processing
```python
from src.utils import OllamaProvider
from src.core import MemoryManager
from src.agents import NLPAgent
from src.coordinator import AgentCoordinator

# Initialize
llm = OllamaProvider("llama3.1")
memory = MemoryManager()
nlp_agent = NLPAgent("NLP", llm=llm, memory=memory)

# Coordinate
coordinator = AgentCoordinator(llm, memory)
coordinator.register_agent(nlp_agent)
coordinator.set_pipeline(["NLP"])

# Process
result = coordinator.process("What is artificial intelligence?")
print(result["parsed_intent"])  # "Define artificial intelligence"
print(result["entities"])       # ["AI", "artificial intelligence"]
```

### With LangGraph
```python
from src.graph import GraphBuilder

graph_builder = GraphBuilder(coordinator)
graph = graph_builder.build_multi_stage()

result = graph.invoke({
    "raw_input": "Summarize renewable energy",
    "input_type": "text"
})
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_agi_system.py::test_nlp_agent -v

# With coverage
pytest tests/ --cov=src/
```

Tests use **FakeLLM** for deterministic verification without requiring model servers.

## Design Decisions

**Why Abstract LLMProvider?**
- Decouples business logic from specific LLM backends
- Enables testing with fake implementations
- Supports multiple models in same pipeline

**Why Unified State?**
- Single source of truth through entire pipeline
- Enables introspection and debugging
- Supports non-linear agent graphs (future)

**Why Memory Manager?**
- Mimics human cognition (working + long-term)
- Enables continuous learning
- Supports context window limitations

## Development Roadmap

- [ ] Phase 2: Knowledge Agent + Semantic Search
- [ ] Phase 3: Reasoning Agent + Multi-step Planning
- [ ] Phase 4: Tool Use + Robotics
- [ ] Multi-modal input (images, audio)
- [ ] Persistent storage (vector DB)
- [ ] Continuous learning loop
- [ ] Autonomous agent operation

## Contributing

To add a new agent:

1. Create `src/agents/my_agent.py` inheriting from `BaseAgent`
2. Implement `process(state)` method
3. Add tests to `tests/test_agi_system.py`
4. Register with coordinator: `coordinator.register_agent(MyAgent(...))`

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed extension guide.

## License

See LICENSE file.
