"""Knowledge base for storing and retrieving facts."""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class KnowledgeSource(str, Enum):
    """Source of knowledge."""
    USER_INPUT = "user_input"
    EXTERNAL_API = "external_api"
    REASONING = "reasoning"
    EXPERIENCE = "experience"
    DOCUMENT = "document"


@dataclass
class Fact:
    """Single fact in the knowledge base."""

    id: str
    content: str
    topic: str  # e.g., "renewable_energy", "ai_models"
    source: KnowledgeSource
    confidence: float = 1.0  # 0-1 scale
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)
    related_facts: List[str] = field(default_factory=list)  # IDs of related facts
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "topic": self.topic,
            "source": self.source.value,
            "confidence": self.confidence,
            "tags": self.tags,
        }


class KnowledgeBase:
    """Persistent knowledge base for facts and relationships."""

    def __init__(self):
        self.facts: dict[str, Fact] = {}
        self.topic_index: dict[str, List[str]] = {}  # topic -> fact IDs
        self.tag_index: dict[str, List[str]] = {}    # tag -> fact IDs
        self.source_index: dict[KnowledgeSource, List[str]] = {
            source: [] for source in KnowledgeSource
        }

    def add_fact(self, fact: Fact) -> None:
        """Add a fact to the knowledge base."""
        self.facts[fact.id] = fact

        # Index by topic
        if fact.topic not in self.topic_index:
            self.topic_index[fact.topic] = []
        self.topic_index[fact.topic].append(fact.id)

        # Index by tags
        for tag in fact.tags:
            if tag not in self.tag_index:
                self.tag_index[tag] = []
            self.tag_index[tag].append(fact.id)

        # Index by source
        self.source_index[fact.source].append(fact.id)

    def get_fact(self, fact_id: str) -> Optional[Fact]:
        """Retrieve a fact by ID."""
        return self.facts.get(fact_id)

    def query_by_topic(self, topic: str, limit: int = 10) -> List[Fact]:
        """Get all facts for a topic."""
        fact_ids = self.topic_index.get(topic, [])
        return [self.facts[fid] for fid in fact_ids[:limit]]

    def query_by_tag(self, tag: str, limit: int = 10) -> List[Fact]:
        """Get all facts with a tag."""
        fact_ids = self.tag_index.get(tag, [])
        return [self.facts[fid] for fid in fact_ids[:limit]]

    def query_by_source(self, source: KnowledgeSource, limit: int = 10) -> List[Fact]:
        """Get all facts from a source."""
        fact_ids = self.source_index[source]
        return [self.facts[fid] for fid in fact_ids[:limit]]

    def search_by_content(self, query: str, limit: int = 10) -> List[Fact]:
        """Simple substring search (use semantic search for better results)."""
        results = []
        query_lower = query.lower()

        for fact in self.facts.values():
            if query_lower in fact.content.lower():
                results.append(fact)

        # Sort by confidence
        results.sort(key=lambda f: f.confidence, reverse=True)
        return results[:limit]

    def get_related_facts(self, fact_id: str, limit: int = 5) -> List[Fact]:
        """Get facts related to a given fact."""
        fact = self.get_fact(fact_id)
        if not fact:
            return []

        related = []
        for rid in fact.related_facts[:limit]:
            related_fact = self.get_fact(rid)
            if related_fact:
                related.append(related_fact)

        return related

    def update_confidence(self, fact_id: str, confidence: float) -> None:
        """Update confidence score of a fact."""
        if fact_id in self.facts:
            self.facts[fact_id].confidence = max(0.0, min(1.0, confidence))
            self.facts[fact_id].updated_at = datetime.now()

    def link_facts(self, fact_id1: str, fact_id2: str) -> None:
        """Create bidirectional link between two facts."""
        fact1 = self.get_fact(fact_id1)
        fact2 = self.get_fact(fact_id2)

        if fact1 and fact2:
            if fact_id2 not in fact1.related_facts:
                fact1.related_facts.append(fact_id2)
            if fact_id1 not in fact2.related_facts:
                fact2.related_facts.append(fact_id1)

    def get_statistics(self) -> dict:
        """Get statistics about the knowledge base."""
        return {
            "total_facts": len(self.facts),
            "topics": len(self.topic_index),
            "tags": len(self.tag_index),
            "avg_confidence": (
                sum(f.confidence for f in self.facts.values()) / len(self.facts)
                if self.facts else 0.0
            ),
        }

    def consolidate(self) -> None:
        """Remove facts with very low confidence or update relationships."""
        # Remove facts with confidence < 0.1
        to_remove = [fid for fid, fact in self.facts.items() if fact.confidence < 0.1]

        for fid in to_remove:
            fact = self.facts.pop(fid)
            # Clean up indices
            if fact.topic in self.topic_index:
                self.topic_index[fact.topic].remove(fid)
            for tag in fact.tags:
                if tag in self.tag_index:
                    self.tag_index[tag].remove(fid)
            self.source_index[fact.source].remove(fid)
