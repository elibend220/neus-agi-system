"""Long-term and short-term memory management for AGI."""
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime
import json


@dataclass
class Memory:
    """Single memory entry with metadata."""

    id: str
    content: str
    memory_type: str  # "fact", "experience", "knowledge", "relationship"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    relevance_score: float = 1.0
    source: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "type": self.memory_type,
            "created_at": self.created_at.isoformat(),
            "relevance": self.relevance_score,
            "source": self.source,
        }


class MemoryManager:
    """Manages both short-term (working) and long-term memory."""

    def __init__(self, max_working_memory: int = 10):
        self.working_memory: list[Memory] = []
        self.long_term_memory: dict[str, Memory] = {}
        self.max_working_memory = max_working_memory
        self.memory_index: dict[str, list[str]] = {}

    def add_working_memory(self, memory: Memory) -> None:
        """Add to short-term working memory."""
        self.working_memory.append(memory)
        if len(self.working_memory) > self.max_working_memory:
            # Move oldest to long-term
            old = self.working_memory.pop(0)
            self.add_long_term_memory(old)

    def add_long_term_memory(self, memory: Memory) -> None:
        """Add to persistent long-term memory."""
        self.long_term_memory[memory.id] = memory
        # Index by type for faster retrieval
        if memory.memory_type not in self.memory_index:
            self.memory_index[memory.memory_type] = []
        self.memory_index[memory.memory_type].append(memory.id)

    def recall(self, query: str, memory_type: Optional[str] = None) -> list[Memory]:
        """Retrieve relevant memories (simplified - use embeddings in production)."""
        results = []
        memories = (
            self.long_term_memory.values()
            if not memory_type
            else [
                self.long_term_memory[mid]
                for mid in self.memory_index.get(memory_type, [])
            ]
        )
        for mem in memories:
            if query.lower() in mem.content.lower():
                results.append(mem)
        return sorted(results, key=lambda m: m.relevance_score, reverse=True)

    def get_working_context(self) -> list[dict]:
        """Get current working memory as context."""
        return [m.to_dict() for m in self.working_memory]

    def clear_working_memory(self) -> None:
        """Clear short-term memory (after consolidation)."""
        self.working_memory.clear()
