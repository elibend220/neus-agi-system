#!/usr/bin/env python3
"""Run the autonomous agent on one or more goals.

Usage:
  python run_autonomous.py "goal text" [--priority N] [--claude | --ollama]
  python run_autonomous.py --resume          # continue persisted goals
State lives in ./.neus_state (goals.json, memory.jsonl) and the sandbox in ./.neus_workspace.
"""
import argparse

from src.autonomy import AgentConfig, AutonomousAgent, GoalStack, PersistentMemory, default_tools
from src.core import MemoryManager


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("goal", nargs="*")
    parser.add_argument("--priority", type=int, default=5)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--claude", action="store_true")
    parser.add_argument("--max-steps", type=int, default=40)
    parser.add_argument("--max-seconds", type=float, default=300.0)
    args = parser.parse_args()

    if args.claude:
        from src.utils import AnthropicProvider
        llm = AnthropicProvider(model="claude-opus-5-5")
    else:
        from src.utils import OllamaProvider
        llm = OllamaProvider(model="llama3.1")

    memory = PersistentMemory(MemoryManager(), ".neus_state/memory.jsonl")
    goals = GoalStack(".neus_state/goals.json")
    if args.goal:
        goals.add(" ".join(args.goal), priority=args.priority)
    elif not args.resume:
        parser.error("provide a goal or --resume")

    agent = AutonomousAgent(
        llm, default_tools(".neus_workspace", memory), goals, memory,
        AgentConfig(max_total_steps=args.max_steps, max_seconds=args.max_seconds),
    )
    report = agent.run()
    print(f"stop={report.stop_reason} steps={report.steps} goals={report.goals}")
    for gid, answer in report.answers.items():
        print(f"[{gid}] {answer}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
