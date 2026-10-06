"""Gated self-modification: patches are applied only if they survive an isolated test run.

Contract:
  1. Paths must be relative .py files under an allowlisted prefix.
  2. Protected paths (this safety gate, tests, CI) can never be modified by the agent.
  3. Patches are applied to a temporary copy of the repo; baseline and patched test
     suites must both pass there before anything touches the real tree.
  4. Originals are backed up so every accepted change can be rolled back.
"""
from __future__ import annotations

import os
import py_compile
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from typing import Optional

_IGNORE = shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".neus_backups", "logs", ".pytest_cache", "venv", ".venv")


@dataclass
class ImproveResult:
    accepted: bool
    reason: str
    applied: list[str] = field(default_factory=list)
    backup_dir: Optional[str] = None
    test_output: str = ""


class GatedImprover:
    def __init__(
        self,
        root: str = ".",
        allowed_prefixes: tuple[str, ...] = ("src/",),
        protected: tuple[str, ...] = ("src/autonomy/improver.py", "tests/", ".github/"),
        test_cmd: tuple[str, ...] = (sys.executable, "-m", "pytest", "-q", "-x"),
        timeout: int = 300,
    ):
        self.root = os.path.realpath(root)
        self.allowed_prefixes = allowed_prefixes
        self.protected = protected
        self.test_cmd = test_cmd
        self.timeout = timeout
        self.backup_root = os.path.join(self.root, ".neus_backups")

    def _check_path(self, path: str) -> Optional[str]:
        norm = os.path.normpath(path).replace(os.sep, "/")
        if os.path.isabs(path) or norm.startswith(".."):
            return f"path escapes repository: {path}"
        if not norm.endswith(".py"):
            return f"only .py files may be modified: {path}"
        if any(norm == p or norm.startswith(p) for p in self.protected):
            return f"protected path: {path}"
        if not any(norm.startswith(p) for p in self.allowed_prefixes):
            return f"outside allowlist: {path}"
        return None

    def _run_tests(self, cwd: str) -> tuple[bool, str]:
        try:
            proc = subprocess.run(self.test_cmd, cwd=cwd, capture_output=True, text=True, timeout=self.timeout)
        except subprocess.TimeoutExpired:
            return False, "test run timed out"
        return proc.returncode == 0, (proc.stdout + proc.stderr)[-2000:]

    def apply(self, patches: dict[str, str]) -> ImproveResult:
        """Validate and apply {relative_path: full_new_content}."""
        if not patches:
            return ImproveResult(False, "no patches supplied")
        for path in patches:
            problem = self._check_path(path)
            if problem:
                return ImproveResult(False, problem)

        with tempfile.TemporaryDirectory(prefix="neus_gate_") as tmp:
            sandbox = os.path.join(tmp, "repo")
            shutil.copytree(self.root, sandbox, ignore=_IGNORE)

            ok, out = self._run_tests(sandbox)
            if not ok:
                return ImproveResult(False, "baseline tests already failing; refusing to self-modify", test_output=out)

            for path, content in patches.items():
                target = os.path.join(sandbox, path)
                os.makedirs(os.path.dirname(target), exist_ok=True)
                with open(target, "w", encoding="utf-8") as f:
                    f.write(content)
                try:
                    py_compile.compile(target, doraise=True)
                except py_compile.PyCompileError as exc:
                    return ImproveResult(False, f"syntax error in {path}: {exc.msg}")

            ok, out = self._run_tests(sandbox)
            if not ok:
                return ImproveResult(False, "patched test suite failed", test_output=out)

        backup = os.path.join(self.backup_root, time.strftime("%Y%m%d_%H%M%S"))
        applied = []
        for path, content in patches.items():
            target = os.path.join(self.root, path)
            if os.path.exists(target):
                dest = os.path.join(backup, path)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(target, dest)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with open(target, "w", encoding="utf-8") as f:
                f.write(content)
            applied.append(path)
        return ImproveResult(True, "all gates passed", applied=applied, backup_dir=backup, test_output=out)

    def rollback(self, result: ImproveResult) -> None:
        """Restore backed-up originals; files that did not exist before are removed."""
        for path in result.applied:
            saved = os.path.join(result.backup_dir or "", path)
            target = os.path.join(self.root, path)
            if os.path.exists(saved):
                shutil.copy2(saved, target)
            elif os.path.exists(target):
                os.remove(target)
