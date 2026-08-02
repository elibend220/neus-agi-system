# core/self_builder.py
import os
import json
import time
import importlib
from typing import List, Dict, Tuple

class SelfBuilder:
    """Autonomous self-improvement engine for NEUS-AGI.

    Workflow:
      1. Scan repository Python sources.
      2. Build context bundle (recent memory + performance metrics + active agent name).
      3. Ask adapter to produce patch blocks in defined format.
      4. Parse patch blocks and apply to files.
      5. Validate by re-importing core modules.
      6. Log result in logs/self_build.log.

    Patch Format (strict):
      === FILE: relative/path/to/file.py ===\n
      <full new file content>\n
      === END FILE ===\n
    Multiple files may appear sequentially.
    If model output is malformed, no changes applied, error logged.
    """

    PATCH_BEGIN = "=== FILE:"
    PATCH_END = "=== END FILE ==="

    def __init__(self, root: str = ".", log_path: str = "logs/self_build.log"):
        self.root = root
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def _log(self, data: Dict):
        line = json.dumps({"ts": time.time(), **data}, ensure_ascii=False)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(line + "\n")

    def _scan_files(self) -> List[str]:
        files = []
        for base, _dirs, names in os.walk(self.root):
            if any(seg in base for seg in ("venv", "__pycache__", "logs")):
                continue
            for n in names:
                if n.endswith(".py"):
                    rel = os.path.relpath(os.path.join(base, n), self.root)
                    files.append(rel)
        return sorted(files)

    def _read_sources(self, files: List[str]) -> Dict[str, str]:
        out = {}
        for f in files:
            try:
                with open(os.path.join(self.root, f), "r", encoding="utf-8") as h:
                    out[f] = h.read()
            except Exception:
                out[f] = ""
        return out

    def _build_prompt(self, adapter, context: Dict) -> str:
        files = context["files"]
        sources = context["sources"]
        perf = context.get("performance", [])
        recent = context.get("recent_memory", {})
        agent = context.get("agent", "unknown")

        summary = [
            "You are upgrading NEUS-AGI. Produce improved full file contents only for files needing enhancement.",
            "Return strictly in patch blocks using the specified format.",
            "Focus: robustness, JSON structured agent outputs, retry logic, clear docstrings, no placeholders.",
            "Avoid changing unrelated code.",
            "Performance metrics (last tasks): " + json.dumps(perf)[:400],
            "Recent memory: " + json.dumps(recent)[:400],
            f"Active agent: {agent}",
            "Begin sources:"\n,
        ]
        for f in files:
            summary.append(f"# FILE: {f}\n" + sources[f][:800])  # truncate per file for prompt size
        summary.append("END SOURCES. Now output patch blocks.")
        return "\n".join(summary)

    def _parse_patches(self, text: str) -> List[Tuple[str, str]]:
        lines = text.splitlines()
        patches = []
        current_file = None
        buffer = []
        for ln in lines:
            if ln.startswith(self.PATCH_BEGIN):
                if current_file is not None:
                    # invalid nesting
                    return []
                # format: === FILE: path ===
                try:
                    path = ln[len(self.PATCH_BEGIN):].strip()
                    if path.endswith("==="):
                        path = path[:-3].strip()
                    current_file = path
                    buffer = []
                except Exception:
                    return []
            elif ln.strip() == self.PATCH_END:
                if current_file is None:
                    return []
                patches.append((current_file, "\n".join(buffer)))
                current_file = None
                buffer = []
            else:
                if current_file is not None:
                    buffer.append(ln)
        if current_file is not None:
            # unclosed block
            return []
        return patches

    def run(self, adapter, agent_name: str, recent_memory: Dict, performance: List[Dict]) -> Dict:
        start = time.time()
        files = self._scan_files()
        sources = self._read_sources(files)
        prompt = self._build_prompt(adapter, {
            "files": files,
            "sources": sources,
            "performance": performance,
            "recent_memory": recent_memory,
            "agent": agent_name,
        })
        raw = adapter.generate(prompt, system="SELF_IMPROVE")
        patches = self._parse_patches(raw)
        applied = []
        if patches:
            for path, content in patches:
                target = os.path.join(self.root, path)
                # safety: only overwrite existing .py under root
                if not target.startswith(os.path.abspath(self.root)):
                    continue
                if not target.endswith('.py'):
                    continue
                abs_t = os.path.abspath(target)
                if os.path.exists(abs_t):
                    with open(abs_t, "w", encoding="utf-8") as f:
                        f.write(content)
                    applied.append(path)
        # validation step
        valid = True
        try:
            importlib.invalidate_caches()
            importlib.import_module("core.core_manager")
        except Exception as e:
            valid = False
            self._log({"event": "validation_error", "error": str(e)})
        duration = time.time() - start
        result = {
            "applied_files": applied,
            "patch_count": len(patches),
            "valid": valid,
            "duration": duration,
        }
        self._log({"event": "self_build", **result})
        return result
