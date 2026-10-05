"""Sandboxed tool registry. No shell, no network, filesystem confined to a workspace."""
from __future__ import annotations

import ast
import operator
import os
from dataclasses import dataclass
from typing import Any, Callable

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.Pow: operator.pow, ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv, ast.USub: operator.neg, ast.UAdd: operator.pos,
}


def safe_calc(expression: str) -> float:
    """Evaluate an arithmetic expression without eval()."""

    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            left, right = walk(node.left), walk(node.right)
            if isinstance(node.op, ast.Pow) and abs(right) > 64:
                raise ValueError("exponent too large")
            return _OPS[type(node.op)](left, right)
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](walk(node.operand))
        raise ValueError("unsupported expression")

    return walk(ast.parse(expression, mode="eval"))


@dataclass
class Tool:
    name: str
    description: str
    fn: Callable[..., Any]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, name: str, description: str, fn: Callable[..., Any]) -> None:
        self._tools[name] = Tool(name, description, fn)

    def describe(self) -> str:
        return "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())

    def __contains__(self, name: str) -> bool:
        return name in self._tools

    def call(self, name: str, args: dict) -> str:
        """Run a tool; failures are returned as observations, never raised."""
        if name not in self._tools:
            return f"ERROR: unknown tool '{name}'. Available: {', '.join(self._tools)}"
        try:
            return str(self._tools[name].fn(**(args or {})))[:4000]
        except Exception as exc:  # observation, not crash
            return f"ERROR: {type(exc).__name__}: {exc}"


def default_tools(workspace: str, memory=None) -> ToolRegistry:
    """Calculator, workspace file IO and memory recall."""
    root = os.path.realpath(workspace)
    os.makedirs(root, exist_ok=True)

    def resolve(path: str) -> str:
        full = os.path.realpath(os.path.join(root, path))
        if os.path.commonpath([root, full]) != root:
            raise PermissionError("path escapes workspace")
        return full

    def read_file(path: str) -> str:
        with open(resolve(path), "r", encoding="utf-8") as f:
            return f.read()

    def write_file(path: str, content: str) -> str:
        full = resolve(path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        return f"wrote {len(content)} chars to {path}"

    def list_files(path: str = ".") -> str:
        return "\n".join(sorted(os.listdir(resolve(path)))) or "(empty)"

    tools = ToolRegistry()
    tools.register("calculator", 'args {"expression": str}. Arithmetic only.', lambda expression: safe_calc(expression))
    tools.register("read_file", 'args {"path": str}. Read a file in the workspace.', read_file)
    tools.register("write_file", 'args {"path": str, "content": str}. Write a file in the workspace.', write_file)
    tools.register("list_files", 'args {"path": str}. List a workspace directory.', list_files)
    if memory is not None:
        def recall(query: str) -> str:
            hits = memory.recall(query)[:5]
            return "\n".join(m.content[:300] for m in hits) or "no matching memories"

        tools.register("recall", 'args {"query": str}. Search long-term memory.', recall)
    return tools
