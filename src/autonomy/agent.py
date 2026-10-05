"""Autonomous agent loop: plan, act, observe, verify, learn.

The loop is bounded (step, per-goal and wall-clock budgets), persists goals and
lessons across runs, verifies its own answers with a critic pass, and detects
repetition so it cannot spin forever on a single failing action.
"""
from __future__ import annotations

import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from src.core import LLMProvider, Memory, MemoryManager

from .goals import FAILED, Goal, GoalStack
from .tools import ToolRegistry

_JSON_BLOCK = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(text: str) -> Optional[dict]:
    """Pull the first JSON object out of model output (handles code fences and chatter)."""
    if not text:
        return None
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass
    match = _JSON_BLOCK.search(text)
    if match:
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else None
        except json.JSONDecodeError:
            return None
    return None


@dataclass
class AgentConfig:
    max_total_steps: int = 40
    max_steps_per_goal: int = 12
    max_attempts_per_goal: int = 2
    max_seconds: float = 300.0
    max_repeat_actions: int = 3
    max_parse_retries: int = 2
    max_subgoal_depth: int = 2
    max_goals: int = 20
    context_window: int = 6


@dataclass
class RunReport:
    steps: int = 0
    stop_reason: str = ""
    goals: dict = field(default_factory=dict)
    answers: dict = field(default_factory=dict)


class PersistentMemory:
    """MemoryManager wrapper that journals long-term memories to JSONL and reloads them."""

    def __init__(self, manager: MemoryManager, path: Optional[str] = None):
        self.manager = manager
        self.path = path
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        raw = json.loads(line)
                        self.manager.add_long_term_memory(
                            Memory(id=raw["id"], content=raw["content"], memory_type=raw["type"], source=raw.get("source"))
                        )
                    except (json.JSONDecodeError, KeyError):
                        continue

    def remember(self, content: str, memory_type: str = "experience", source: str = "autonomy") -> None:
        mem = Memory(id=uuid.uuid4().hex[:10], content=content, memory_type=memory_type, source=source)
        self.manager.add_long_term_memory(mem)
        if self.path:
            os.makedirs(os.path.dirname(os.path.abspath(self.path)), exist_ok=True)
            with open(self.path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"id": mem.id, "content": content, "type": memory_type, "source": source}, ensure_ascii=False) + "\n")

    def recall(self, query: str) -> list[Memory]:
        words = [w for w in re.findall(r"\w{4,}", query.lower())][:6]
        seen, out = set(), []
        for w in words:
            for m in self.manager.recall(w):
                if m.id not in seen:
                    seen.add(m.id)
                    out.append(m)
        return out[:5]


class AutonomousAgent:
    """Pursues goals without a human in the loop, inside hard budgets."""

    def __init__(
        self,
        llm: LLMProvider,
        tools: ToolRegistry,
        goals: GoalStack,
        memory: PersistentMemory,
        config: Optional[AgentConfig] = None,
    ):
        self.llm, self.tools, self.goals, self.memory = llm, tools, goals, memory
        self.config = config or AgentConfig()
        self.trace: list[dict] = []

    # ---- model I/O -----------------------------------------------------
    def _ask_json(self, prompt: str) -> Optional[dict]:
        for attempt in range(self.config.max_parse_retries + 1):
            parsed = extract_json(self.llm.generate(prompt))
            if parsed is not None:
                return parsed
            prompt += "\n\nYour previous reply was not valid JSON. Reply with one JSON object only."
        return None

    def _depth(self, goal: Goal) -> int:
        depth, cur = 0, goal
        while cur.parent_id and cur.parent_id in self.goals.goals:
            depth, cur = depth + 1, self.goals.goals[cur.parent_id]
        return depth

    def _plan_prompt(self, goal: Goal, history: list[dict], warning: str) -> str:
        recalled = "\n".join(f"- {m.content[:200]}" for m in self.memory.recall(goal.description)) or "- none"
        recent = "\n".join(
            f"[{h['tool']}({json.dumps(h['args'], ensure_ascii=False)[:200]})] -> {h['observation'][:400]}"
            for h in history[-self.config.context_window:]
        ) or "(no actions yet)"
        critique = f"\nPrevious attempt was rejected: {goal.critique}" if goal.critique else ""
        return (
            "You are an autonomous agent. Decide the single next action.\n"
            f"GOAL: {goal.description}{critique}\n"
            f"LESSONS FROM MEMORY:\n{recalled}\n"
            f"TOOLS:\n{self.tools.describe()}\n"
            "- finish: args {\"answer\": str}. Use when the goal is achieved.\n"
            "- add_subgoal: args {\"description\": str, \"priority\": int}. Decompose a hard goal.\n"
            f"RECENT ACTIONS:\n{recent}\n{warning}\n"
            'Reply with JSON only: {"thought": str, "tool": str, "args": object}'
        )

    # ---- verification & learning ---------------------------------------
    def _verify(self, goal: Goal, answer: str, history: list[dict]) -> tuple[bool, str]:
        evidence = "\n".join(f"{h['tool']} -> {h['observation'][:200]}" for h in history[-self.config.context_window:])
        verdict = self._ask_json(
            "You are a strict critic. Judge whether the answer fully achieves the goal and is supported by the evidence.\n"
            f"GOAL: {goal.description}\nANSWER: {answer}\nEVIDENCE:\n{evidence}\n"
            'Reply with JSON only: {"ok": bool, "critique": str}'
        )
        if verdict is None:
            return False, "critic returned no parseable verdict"
        return bool(verdict.get("ok")), str(verdict.get("critique", ""))

    def _learn(self, goal: Goal, outcome: str, history: list[dict]) -> None:
        tools_used = ", ".join(dict.fromkeys(h["tool"] for h in history)) or "none"
        self.memory.remember(
            f"Goal '{goal.description}' ended {outcome} after {goal.steps} steps using [{tools_used}]. "
            f"Result: {str(goal.result)[:200]}"
        )

    # ---- main loop -----------------------------------------------------
    def run(self) -> RunReport:
        cfg, start = self.config, time.monotonic()
        report = RunReport()
        history: dict[str, list[dict]] = {}
        repeats: dict[str, dict[str, int]] = {}

        while True:
            if report.steps >= cfg.max_total_steps:
                report.stop_reason = "step_budget"
                break
            if time.monotonic() - start > cfg.max_seconds:
                report.stop_reason = "time_budget"
                break
            goal = self.goals.next_goal()
            if goal is None:
                report.stop_reason = "no_active_goals"
                break
            if goal.steps >= cfg.max_steps_per_goal:
                self.goals.fail(goal, "per-goal step budget exhausted")
                self._learn(goal, FAILED, history.get(goal.id, []))
                continue

            hist = history.setdefault(goal.id, [])
            seen = repeats.setdefault(goal.id, {})
            report.steps += 1
            goal.steps += 1

            decision = self._ask_json(self._plan_prompt(goal, hist, ""))
            if decision is None or "tool" not in decision:
                self.goals.fail(goal, "model produced no valid action")
                self._learn(goal, FAILED, hist)
                continue

            tool, args = str(decision["tool"]), decision.get("args") or {}
            if not isinstance(args, dict):
                args = {}
            self.trace.append({"goal": goal.id, "step": goal.steps, "tool": tool, "args": args})

            if tool == "finish":
                answer = str(args.get("answer", ""))
                ok, critique = self._verify(goal, answer, hist)
                if ok:
                    self.goals.complete(goal, answer)
                    report.answers[goal.id] = answer
                    self._learn(goal, "done", hist)
                else:
                    goal.attempts += 1
                    goal.critique = critique
                    if goal.attempts >= cfg.max_attempts_per_goal:
                        self.goals.fail(goal, f"rejected by critic: {critique}")
                        self._learn(goal, FAILED, hist)
                    else:
                        self.goals.save()
                continue

            if tool == "add_subgoal":
                desc = str(args.get("description", "")).strip()
                if desc and self._depth(goal) < cfg.max_subgoal_depth and len(self.goals.goals) < cfg.max_goals:
                    child = self.goals.add(desc, int(args.get("priority", goal.priority)), parent_id=goal.id)
                    hist.append({"tool": tool, "args": args, "observation": f"created subgoal {child.id}"})
                else:
                    hist.append({"tool": tool, "args": args, "observation": "ERROR: subgoal refused (empty, too deep or goal cap reached)"})
                continue

            signature = f"{tool}:{json.dumps(args, sort_keys=True, ensure_ascii=False)}"
            seen[signature] = seen.get(signature, 0) + 1
            if seen[signature] >= cfg.max_repeat_actions:
                self.goals.fail(goal, f"stuck repeating {tool}")
                self._learn(goal, FAILED, hist)
                continue

            hist.append({"tool": tool, "args": args, "observation": self.tools.call(tool, args)})

        report.goals = self.goals.summary()
        return report
