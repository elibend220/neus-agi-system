"""AGI Agents - specialized processing units.

Phase 1-2 Agents (AGI Framework):
- NLPAgent: Natural language processing
- KnowledgeAgent: Knowledge retrieval & synthesis

Neus Integration Agents (Research Components):
- NeusConsciousnessAgent: Attention, metacognition, self-model
- NeusReasoningAgent: Multi-modal reasoning
- NeusCreativityAgent: Ideation and creative solutions
"""
from .base_agent import BaseAgent
from .nLP_agent import NLPAgent
from .knowledge_agent import KnowledgeAgent
from .neus_consciousness_agent import NeusConsciousnessAgent
from .neus_reasoning_agent import NeusReasoningAgent
from .neus_creativity_agent import NeusCreativityAgent

__all__ = [
    "BaseAgent",
    "NLPAgent",
    "KnowledgeAgent",
    "NeusConsciousnessAgent",
    "NeusReasoningAgent",
    "NeusCreativityAgent",
]
