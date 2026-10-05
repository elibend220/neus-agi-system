"""Persistent goal stack for the autonomous loop."""
from __future__ import annotations

import json
import os
import uuid
from dataclasses import asdict, dataclass, field
from typing import Optional

ACTIVE, DONE, FAILED = "active", "done", "failed"


@dataclass
class Goal:
    description: str
    priority: int = 5
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    parent_id: Optional[str] = None
    status: str = ACTIVE
    attempts: int = 0
    steps: int = 0
    result: Optional[str] = None
    critique: Optional[str] = None


class GoalStack:
    """Priority-ordered goals with JSON persistence."""

    def __init__(self, path: Optional[str] = None):
        self.path = path
        self.goals: dict[str, Goal] = {}
        if path and os.path.exists(path):
            self._load()

    def add(self, description: str, priority: int = 5, parent_id: Optional[str] = None) -> Goal:
        goal = Goal(description=description.strip(), priority=int(priority), parent_id=parent_id)
        self.goals[goal.id] = goal
        self.save()
        return goal

    def next_goal(self) -> Optional[Goal]:
        """Highest priority active goal; children are served before their parent."""
        active = [g for g in self.goals.values() if g.status == ACTIVE]
        if not active:
            return None
        parents_with_open_children = {g.parent_id for g in active if g.parent_id}
        ready = [g for g in active if g.id not in parents_with_open_children] or active
        return max(ready, key=lambda g: g.priority)

    def complete(self, goal: Goal, result: str) -> None:
        goal.status, goal.result = DONE, result
        self.save()

    def fail(self, goal: Goal, reason: str) -> None:
        goal.status, goal.result = FAILED, reason
        self.save()

    def summary(self) -> dict:
        counts = {ACTIVE: 0, DONE: 0, FAILED: 0}
        for g in self.goals.values():
            counts[g.status] += 1
        return counts

    def save(self) -> None:
        if not self.path:
            return
        os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump([asdict(g) for g in self.goals.values()], f, ensure_ascii=False, indent=2)
        os.replace(tmp, self.path)

    def _load(self) -> None:
        with open(self.path, "r", encoding="utf-8") as f:
            for raw in json.load(f):
                goal = Goal(**raw)
                self.goals[goal.id] = goal
