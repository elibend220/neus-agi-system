"""Autonomy layer: bounded goal-driven loop with persistence and gated self-improvement."""
from .agent import AgentConfig, AutonomousAgent, PersistentMemory, RunReport, extract_json
from .goals import Goal, GoalStack
from .improver import GatedImprover, ImproveResult
from .tools import ToolRegistry, default_tools, safe_calc

__all__ = [
    "AgentConfig", "AutonomousAgent", "PersistentMemory", "RunReport", "extract_json",
    "Goal", "GoalStack", "GatedImprover", "ImproveResult", "ToolRegistry", "default_tools", "safe_calc",
]
