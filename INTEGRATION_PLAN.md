# Integration Plan: Neus Legacy + AGI Framework

## Current State

### Neus Legacy Code (Original)
```
core/
├── consciousness/     ← Attention, Metacognition, Self-model
├── reasoning/        ← Causal, Abstract, Logical, Probabilistic
├── learning/         ← Continual, Few-shot, Meta, Transfer
├── memory/          ← Episodic, Semantic, Procedural, Working
├── understanding/   ← Language, Concepts, Context, Multimodal
├── creativity/      ← Generative, Analogical, Conceptual
├── emotion/        ← Recognition, Generation, Integration
├── social/         ← Theory of Mind, Communication, Cooperation
├── repair_core.py   ← Self-repair & improvement structure
└── self_builder.py  ← Autonomous self-improvement engine
```

### AGI Framework (Phase 1+2)
```
src/
├── core/            ← LLM Provider, Memory Manager, State
├── agents/          ← BaseAgent, NLPAgent, KnowledgeAgent
├── coordinator/     ← Multi-agent orchestration
├── graph/          ← LangGraph integration
├── knowledge/      ← Knowledge base, semantic retrieval
└── utils/          ← LLM providers (Ollama, Claude)
```

## Integration Strategy

### 1. **Keep Neus modules** (the deep research)
- Consciousness, Reasoning, Learning modules stay as-is
- These are domain-specific implementations
- Will be accessed via new agent types

### 2. **Upgrade to AGI Framework** (Phase 1+2 infrastructure)
- Core → Use new LLM Provider + Memory + State system
- Agents → Use BaseAgent for compatibility
- All Neus modules become agents in the framework

### 3. **Create Bridge Layer**
- New agent types that wrap Neus modules
- Unified state flow through both systems
- Single coordinator for all agents

## New Architecture

```
┌─────────────────────────────────────────────────────┐
│           AGI Coordinator (Unified)                 │
│     Manages all agents through state flow           │
└──────────┬──────────────────────────┬───────────────┘
           │                          │
    ┌──────▼──────┐           ┌──────▼──────┐
    │ AGI Agents  │           │ Neus Agents │
    │             │           │             │
    ├─ NLPAgent   │           ├─ Consciousness
    ├─ Knowledge  │           ├─ Reasoning
    └─ (Phase 3)  │           ├─ Learning
                  │           ├─ Creativity
                  │           └─ Emotion/Social
    ┌─────────────┴───────────┴─────────────┐
    │     Unified Core Foundation           │
    │  (LLM Provider, Memory, State)        │
    └───────────────────────────────────────┘
```

## Implementation Steps

### Phase A: Wrap Neus Modules
1. Create `src/agents/neus_consciousness_agent.py`
2. Create `src/agents/neus_reasoning_agent.py`
3. Create `src/agents/neus_creativity_agent.py`
4. etc.

### Phase B: Unified Memory
1. Bridge `MemoryManager` with Neus memory systems
2. Consolidate episodic, semantic, procedural memories
3. Working memory as unified state

### Phase C: Self-Improvement Integration
1. Integrate `self_builder.py` with AgentCoordinator
2. Allow agents to self-improve autonomously
3. Repair_core becomes part of state management

## File Organization (Final)

```
neus-agi-system/
├── src/                          ← AGI Framework (Phase 1-4)
│   ├── core/                     ← LLM, Memory, State
│   ├── agents/                   ← All agent types (both systems)
│   │   ├── nLP_agent.py
│   │   ├── knowledge_agent.py
│   │   ├── neus_consciousness_agent.py  (NEW)
│   │   ├── neus_reasoning_agent.py      (NEW)
│   │   └── neus_creativity_agent.py     (NEW)
│   ├── coordinator/              ← Unified orchestration
│   ├── knowledge/               ← Knowledge base
│   └── utils/
│
├── neus/                         ← Neus Legacy (Preserved)
│   └── core/                     ← Original Neus modules
│       ├── consciousness/
│       ├── reasoning/
│       ├── learning/
│       ├── memory/
│       ├── creativity/
│       ├── emotion/
│       ├── social/
│       ├── repair_core.py
│       └── self_builder.py
│
├── tests/
├── main_agi.py
└── ARCHITECTURE.md
```

## Benefits

✅ **Preserve Neus Research** - All deep modules intact
✅ **Unified Framework** - Single state, coordinator, LLM provider
✅ **Scalability** - New agents easily added via BaseAgent
✅ **Self-Improvement** - SelfBuilder integrated into agent system
✅ **Best of Both Worlds** - Research depth + Engineering scalability

## Timeline

- Week 1: Move Neus modules to `neus/core/`
- Week 2: Create bridge agents (Consciousness, Reasoning, Creativity)
- Week 3: Unified memory integration
- Week 4: Self-improvement + repair core integration
- Week 5: Testing & validation

---

**This makes neus-agi-system a true hybrid: research-grade AGI components + production-grade orchestration framework** 🚀
