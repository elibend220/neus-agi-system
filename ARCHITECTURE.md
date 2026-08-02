# AGI System Architecture (2026)

## Overview

This is a next-generation AGI architecture designed to scale from simple NLP tasks to complex multi-domain reasoning. The system follows these principles:

1. **NLP-First** - Natural language is the universal interface
2. **Modular** - Each domain is a pluggable agent
3. **Memory-Centric** - Long-term and working memory drive learning
4. **LLM-Agnostic** - Provider abstraction allows any backend
5. **State-Driven** - Unified state flows through all agents

## Core Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  INPUT (Text/Image/Audio)               │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│          Stage 1: NLP Processing                        │
│  • Parse intent                                         │
│  • Extract entities                                     │
│  • Summarize input                                      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│       Stage 2: Knowledge Retrieval (Future)             │
│  • Query long-term memory                              │
│  • Retrieve relevant facts                             │
│  • Build context window                                │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│       Stage 3: Reasoning & Planning (Future)            │
│  • Analyze problem                                      │
│  • Generate plan                                        │
│  • Estimate complexity                                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│       Stage 4: Execution (Future)                       │
│  • Execute actions                                      │
│  • Interact with tools/robotics                         │
│  • Monitor results                                      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              OUTPUT + Memory Updates                    │
└─────────────────────────────────────────────────────────┘
```

## Component Breakdown

### 1. Core (`src/core/`)

#### `llm.py` - LLMProvider (Abstract Interface)
- Decouples graph logic from LLM implementations
- Methods: `generate()`, `generate_structured()`, `embedding()`
- Implementations: OllamaProvider, AnthropicProvider (extensible)

#### `memory.py` - MemoryManager
- **Working Memory** - Short-term context (max 10 items)
- **Long-term Memory** - Persistent knowledge base
- **Memory Indexing** - Fast retrieval by type
- Supports: facts, experiences, knowledge, relationships

#### `state.py` - UnifiedState & StateManager
- Typed dictionary passed through all agents
- Tracks processing stage from input → output
- Includes agent chain history
- Supports checkpointing and rollback

### 2. Agents (`src/agents/`)

#### `base_agent.py` - BaseAgent (Abstract)
- All agents inherit from this
- Methods: `process(state)`, `log_interaction()`
- Encapsulates LLM, memory, and system prompt
- Callable interface (compatible with LangGraph nodes)

#### `nLP_agent.py` - NLPAgent (Concrete)
- First processing stage
- Extracts: intent, entities, summary
- Used in Stage 1 of pipeline
- Extensible for multi-language support

**Future Agents:**
- `knowledge_agent.py` - Knowledge retrieval & management
- `reasoning_agent.py` - Complex reasoning & planning
- `execution_agent.py` - Action execution & tool use
- `vision_agent.py` - Image understanding
- `audio_agent.py` - Speech processing

### 3. Coordinator (`src/coordinator/`)

#### `coordinator.py` - AgentCoordinator
- Orchestrates multiple agents
- Maintains agent registry
- Manages pipeline execution
- State flows through registered agents in sequence
- Returns final unified state with all processing history

### 4. Graph (`src/graph/`)

#### `builder.py` - GraphBuilder
- Bridges AGI system → LangGraph
- Two build modes:
  - **Simple** - Single "process" node
  - **Multi-stage** - One node per agent (more introspection)

### 5. Providers (`src/utils/`)

#### `ollama_provider.py`
- Local LLM via Ollama
- No API keys required
- Requires: `ollama pull llama3.1 && ollama serve`

#### `anthropic_provider.py`
- Claude via Anthropic API
- Structured output support
- Requires: `ANTHROPIC_API_KEY` environment variable

## State Flow Example

```
Input: "Summarize the benefits of renewable energy"

UnifiedState {
  raw_input: "Summarize...",
  input_type: "text",
  current_stage: "input"
}
  │
  ├─> NLP_Agent.process()
  │   output: {
  │     parsed_intent: "Summarize benefits",
  │     entities: ["renewable energy", "benefits"],
  │     summary: "User wants overview of renewable energy advantages"
  │   }
  │
  ├─> Knowledge_Agent.process() [future]
  │   retrieves: relevant facts about renewables
  │
  ├─> Reasoning_Agent.process() [future]
  │   generates: structured response plan
  │
  └─> Final State {
      output: "Renewable energy provides...",
      confidence: 0.92,
      agent_chain: ["NLP_Agent", "Knowledge_Agent", "Reasoning_Agent"]
    }
```

## How to Extend

### Add a New Agent

```python
from src.agents import BaseAgent
from src.core import UnifiedState

class MyAgent(BaseAgent):
    def process(self, state: UnifiedState) -> UnifiedState:
        # Process state
        result = self.llm.generate(prompt)
        return {"my_output": result}
```

### Register & Use

```python
coordinator = AgentCoordinator(llm, memory)
coordinator.register_agent(MyAgent(...))
coordinator.set_pipeline(["NLP_Agent", "MyAgent"])
result = coordinator.process("input text")
```

## Processing Stages (enum)

1. `INPUT` - Raw input received
2. `NLP_PROCESSING` - Text understanding
3. `KNOWLEDGE_RETRIEVAL` - Memory lookup
4. `REASONING` - Analysis & planning
5. `PLANNING` - Action sequence generation
6. `EXECUTION` - Action execution
7. `OUTPUT` - Response generation

## Next Phases

### Phase 2 (Q3 2026)
- Knowledge_Agent with semantic search
- Reasoning_Agent with multi-step planning
- Long-term memory persistence (vector DB)

### Phase 3 (Q4 2026)
- Multimodal input (images, audio)
- Tool use & API integration
- Dynamic agent creation

### Phase 4 (2027+)
- Robotics integration
- Real-world embodiment
- Continuous learning from interactions

## Design Decisions

**Why LLM Injection?**
- Decouples business logic from LLM provider
- Enables testing with fake LLMs
- Supports multiple LLM backends simultaneously

**Why Memory Manager?**
- AGI needs persistent knowledge
- Working memory ↔ long-term consolidation
- Mimics human memory systems

**Why UnifiedState?**
- All agents see the same context
- Prevents information loss between stages
- Enables debugging and introspection

**Why Agents over Functions?**
- Agents can have state and learning
- Extensible to autonomous operation
- Mirrors human cognitive specialization

## Configuration

### Using Ollama (Local)
```bash
ollama pull llama3.1
ollama serve  # In one terminal
python main_agi.py  # In another
```

### Using Claude (Anthropic)
```bash
export ANTHROPIC_API_KEY="sk-..."
python main_agi.py --claude
```

## Testing

```bash
pip install -r requirements.txt
pytest tests/ -v
```

Each agent should have deterministic tests with fake LLMs.

---

**Built for the future of AGI** 🚀
