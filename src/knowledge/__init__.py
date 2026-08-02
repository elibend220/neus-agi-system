"""Knowledge management system for AGI."""
from .knowledge_base import KnowledgeBase, Fact, KnowledgeSource
from .retrieval import SemanticRetriever

__all__ = ["KnowledgeBase", "Fact", "KnowledgeSource", "SemanticRetriever"]
