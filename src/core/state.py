"""Unified state management across all agents."""
from typing import TypedDict, Optional, Any, Dict
from dataclasses import dataclass, field
from enum import Enum


class ProcessingStage(str, Enum):
    """Stages of AGI processing pipeline."""

    INPUT = "input"
    NLP_PROCESSING = "nlp_processing"
    KNOWLEDGE_RETRIEVAL = "knowledge_retrieval"
    REASONING = "reasoning"
    PLANNING = "planning"
    EXECUTION = "execution"
    OUTPUT = "output"


class UnifiedState(TypedDict, total=False):
    """Unified state passed through all agents and nodes."""

    # Input
    raw_input: str
    input_type: str  # "text", "image", "audio", "command"

    # NLP Processing
    processed_text: str
    parsed_intent: str
    entities: list[str]
    summary: str

    # Knowledge
    knowledge_context: str
    relevant_facts: list[str]
    knowledge_sources: list[str]

    # Reasoning & Planning
    reasoning: str
    plan: list[str]
    estimated_complexity: int

    # Execution
    actions_taken: list[str]
    current_stage: ProcessingStage
    error: Optional[str]

    # Output & Metadata
    output: str
    confidence: float
    memory_updates: list[Dict[str, Any]]

    # System
    agent_chain: list[str]  # Which agents processed this
    timestamp: str
    request_id: str


@dataclass
class StateManager:
    """Manages state flow through the AGI pipeline."""

    state: UnifiedState = field(default_factory=dict)
    history: list[UnifiedState] = field(default_factory=list)

    def update(self, updates: dict) -> None:
        """Merge updates into current state."""
        self.state.update(updates)

    def checkpoint(self) -> None:
        """Save current state to history."""
        self.history.append(dict(self.state))

    def rollback(self) -> None:
        """Restore previous state."""
        if self.history:
            self.state = self.history.pop()

    def get_state_for_agent(self, agent_name: str) -> UnifiedState:
        """Get a snapshot of current state."""
        return dict(self.state)

    def mark_stage(self, stage: ProcessingStage) -> None:
        """Mark current processing stage."""
        self.state["current_stage"] = stage
