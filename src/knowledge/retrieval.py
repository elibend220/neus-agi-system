"""Semantic retrieval for knowledge base queries."""
from typing import List, Optional
from .knowledge_base import Fact, KnowledgeBase


class SemanticRetriever:
    """Retrieves relevant facts using semantic similarity."""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.embeddings_cache: dict[str, List[float]] = {}

    def _simple_embedding(self, text: str) -> List[float]:
        """Simple embedding using word frequency (production: use real embeddings)."""
        # This is a placeholder - in production use sentence-transformers or embeddings API
        words = text.lower().split()
        # Create a simple 100-dim vector based on word hashing
        embedding = [0.0] * 100

        for word in words:
            idx = hash(word) % 100
            embedding[idx] += 1.0 / len(words)

        # Normalize
        norm = sum(x ** 2 for x in embedding) ** 0.5
        if norm > 0:
            embedding = [x / norm for x in embedding]

        return embedding

    def _cosine_similarity(
        self, vec1: List[float], vec2: List[float]
    ) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        return dot_product  # Already normalized

    def retrieve(
        self, query: str, limit: int = 5, min_similarity: float = 0.1
    ) -> List[Fact]:
        """Retrieve facts most relevant to query using semantic similarity."""
        query_embedding = self._simple_embedding(query)
        scored_facts = []

        for fact in self.kb.facts.values():
            # Get or compute embedding for fact
            if fact.id not in self.embeddings_cache:
                self.embeddings_cache[fact.id] = self._simple_embedding(fact.content)

            fact_embedding = self.embeddings_cache[fact.id]
            similarity = self._cosine_similarity(query_embedding, fact_embedding)

            # Apply confidence weighting
            weighted_score = similarity * fact.confidence

            if weighted_score >= min_similarity:
                scored_facts.append((fact, weighted_score))

        # Sort by score and return top N
        scored_facts.sort(key=lambda x: x[1], reverse=True)
        return [fact for fact, _ in scored_facts[:limit]]

    def retrieve_by_entities(
        self, entities: List[str], limit: int = 10
    ) -> dict[str, List[Fact]]:
        """Retrieve facts for each entity."""
        results = {}

        for entity in entities:
            # Try tag search first
            facts = self.kb.query_by_tag(entity, limit=limit)

            # Fall back to semantic search
            if not facts:
                facts = self.retrieve(entity, limit=limit)

            results[entity] = facts

        return results

    def retrieve_context(
        self, query: str, intent: str, entities: List[str], limit: int = 10
    ) -> dict:
        """Retrieve comprehensive context for a query."""
        # Semantic search on full query
        semantic_results = self.retrieve(query, limit=limit // 2)

        # Entity-based retrieval
        entity_results = self.retrieve_by_entities(entities, limit=limit // 2)

        # Intent-based (if available as topic)
        intent_results = self.kb.query_by_topic(intent, limit=limit // 4)

        # Combine results, avoiding duplicates by ID
        combined_dict = {}
        for fact in semantic_results + intent_results:
            combined_dict[fact.id] = fact
        for facts in entity_results.values():
            for fact in facts:
                combined_dict[fact.id] = fact

        combined = list(combined_dict.values())[:limit]

        return {
            "semantic": semantic_results,
            "entities": entity_results,
            "intent": intent_results,
            "combined": combined,
        }
