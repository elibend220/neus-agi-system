import json
import os
import shutil

from src.autonomy import (
    AgentConfig, AutonomousAgent, GatedImprover, GoalStack, PersistentMemory, default_tools, extract_json, safe_calc,
)
from src.core import LLMProvider, MemoryManager


class ScriptedLLM(LLMProvider):
    """Replies from a queue; the last reply repeats."""

    def __init__(self, replies):
        self.replies, self.calls = list(replies), 0

    def generate(self, prompt, **kwargs):
        self.calls += 1
        return self.replies.pop(0) if len(self.replies) > 1 else self.replies[0]

    def generate_structured(self, prompt, schema, **kwargs):
        return extract_json(self.generate(prompt)) or {}

    def embedding(self, text):
        return [0.0]


def act(tool, **args):
    return json.dumps({"thought": "t", "tool": tool, "args": args})


VERDICT_OK = json.dumps({"ok": True, "critique": ""})


def build(tmp_path, replies, **cfg):
    mem = PersistentMemory(MemoryManager(), str(tmp_path / "mem.jsonl"))
    goals = GoalStack(str(tmp_path / "goals.json"))
    llm = ScriptedLLM(replies)
    agent = AutonomousAgent(llm, default_tools(str(tmp_path / "ws"), mem), goals, mem, AgentConfig(**cfg))
    return agent, goals, mem


def test_extract_json_handles_fences_and_noise():
    assert extract_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert extract_json("sure! {\"a\": 2} done") == {"a": 2}
    assert extract_json("nope") is None


def test_calculator_rejects_code():
    assert safe_calc("2 + 3 * 4") == 14
    for bad in ("__import__('os')", "2 ** 9999", "open('x')"):
        try:
            safe_calc(bad)
        except Exception:
            continue
        raise AssertionError(bad)


def test_workspace_escape_is_blocked(tmp_path):
    tools = default_tools(str(tmp_path / "ws"))
    assert tools.call("read_file", {"path": "../../etc/passwd"}).startswith("ERROR")
    assert "wrote" in tools.call("write_file", {"path": "a/b.txt", "content": "hi"})


def test_goal_completed_with_tool_use_and_verification(tmp_path):
    agent, goals, mem = build(tmp_path, [act("calculator", expression="6*7"), act("finish", answer="42"), VERDICT_OK])
    goal = goals.add("compute 6*7")
    report = agent.run()
    assert report.stop_reason == "no_active_goals"
    assert report.answers[goal.id] == "42"
    assert any("compute 6*7" in m.content for m in mem.manager.long_term_memory.values())


def test_critic_rejection_retries_then_fails(tmp_path):
    reject = json.dumps({"ok": False, "critique": "unsupported"})
    agent, goals, _ = build(tmp_path, [act("finish", answer="guess"), reject, act("finish", answer="guess2"), reject], max_attempts_per_goal=2)
    goal = goals.add("hard")
    agent.run()
    assert goals.goals[goal.id].status == "failed"
    assert goals.goals[goal.id].attempts == 2


def test_repeated_action_detected(tmp_path):
    agent, goals, _ = build(tmp_path, [act("calculator", expression="1+1")], max_repeat_actions=3)
    goal = goals.add("loop forever")
    report = agent.run()
    assert goals.goals[goal.id].status == "failed"
    assert report.steps < 10


def test_step_budget_stops_run(tmp_path):
    replies = [act("calculator", expression=f"{i}+1") for i in range(100)]
    agent, goals, _ = build(tmp_path, replies, max_total_steps=3, max_steps_per_goal=50)
    goals.add("endless")
    assert agent.run().stop_reason == "step_budget"


def test_subgoal_runs_before_parent_and_depth_is_capped(tmp_path):
    replies = [
        act("add_subgoal", description="child", priority=5),
        act("finish", answer="child done"), VERDICT_OK,
        act("finish", answer="parent done"), VERDICT_OK,
    ]
    agent, goals, _ = build(tmp_path, replies)
    parent = goals.add("parent")
    agent.run()
    assert [g.status for g in goals.goals.values()] == ["done", "done"]
    assert len(goals.goals) == 2 and goals.goals[parent.id].result == "parent done"


def test_invalid_model_output_fails_goal_without_crash(tmp_path):
    agent, goals, _ = build(tmp_path, ["not json at all"])
    goal = goals.add("x")
    agent.run()
    assert goals.goals[goal.id].status == "failed"


def test_state_persists_across_runs(tmp_path):
    agent, goals, mem = build(tmp_path, [act("finish", answer="ok"), VERDICT_OK])
    goals.add("remember me please")
    agent.run()
    reloaded_goals = GoalStack(str(tmp_path / "goals.json"))
    reloaded_mem = PersistentMemory(MemoryManager(), str(tmp_path / "mem.jsonl"))
    assert reloaded_goals.summary()["done"] == 1
    assert reloaded_mem.recall("remember please")


# ---- gated improver --------------------------------------------------------
def make_repo(tmp_path, body="VALUE = 1\n", test="from src.mod import VALUE\n\ndef test_v():\n    assert VALUE >= 1\n"):
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "tests").mkdir()
    (repo / "src" / "__init__.py").write_text("")
    (repo / "src" / "mod.py").write_text(body)
    (repo / "tests" / "test_mod.py").write_text(test)
    return GatedImprover(root=str(repo), timeout=60), repo


def test_improver_accepts_passing_patch_and_rolls_back(tmp_path):
    imp, repo = make_repo(tmp_path)
    result = imp.apply({"src/mod.py": "VALUE = 2\n"})
    assert result.accepted and (repo / "src" / "mod.py").read_text() == "VALUE = 2\n"
    imp.rollback(result)
    assert (repo / "src" / "mod.py").read_text() == "VALUE = 1\n"


def test_improver_rejects_patch_that_breaks_tests(tmp_path):
    imp, repo = make_repo(tmp_path)
    result = imp.apply({"src/mod.py": "VALUE = 0\n"})
    assert not result.accepted and "failed" in result.reason
    assert (repo / "src" / "mod.py").read_text() == "VALUE = 1\n"


def test_improver_rejects_syntax_errors_and_forbidden_paths(tmp_path):
    imp, repo = make_repo(tmp_path)
    assert "syntax" in imp.apply({"src/mod.py": "def (:\n"}).reason
    for bad in ("tests/test_mod.py", "src/autonomy/improver.py", "../evil.py", "/etc/x.py", "setup.sh", "other/x.py"):
        assert not imp.apply({bad: "x = 1\n"}).accepted
