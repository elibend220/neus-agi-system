import os
import logging
from typing import Optional, Dict, Any
import requests

log = logging.getLogger("TaskDispatcher")

try:
    from core.modules.adaptive_module_creator import AdaptiveModuleCreator
    _ADAPTIVE_AVAILABLE = True
except Exception as e:
    log.debug("AdaptiveModuleCreator not available: %s", e)
    _ADAPTIVE_AVAILABLE = False
    AdaptiveModuleCreator = None  # type: ignore


class _SimpleMockAdapter:
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        sys_note = f"[sys:{system}] " if system else ""
        return f"{sys_note}[mock] {prompt}"


class _LMStudioAdapter:
    def __init__(self, base_url: Optional[str] = None, model: Optional[str] = None, timeout_secs: int = 60):
        self.base_url = base_url or os.getenv("LM_STUDIO_BASE_URL", "http://localhost:1234/v1")
        self.model = model or os.getenv("LM_STUDIO_MODEL", "mistralai/mistral-7b-instruct-v0.3")
        self.timeout_secs = timeout_secs

    def _payload(self, messages: list[Dict[str, str]]) -> Dict[str, Any]:
        return {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 256,
            "stream": False,
        }

    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        messages = []
        if system:
            messages.append({"role": "user", "content": f"System: {system}"})
        messages.append({"role": "user", "content": prompt})
        try:
            url = f"{self.base_url}/chat/completions"
            resp = requests.post(url, json=self._payload(messages), timeout=self.timeout_secs, headers={"Content-Type":"application/json"})
            if resp.status_code != 200:
                log.warning("LM Studio non-200: %s %s", resp.status_code, resp.text[:400])
                return _SimpleMockAdapter().generate(prompt, system)
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content")
            if not content:
                return _SimpleMockAdapter().generate(prompt, system)
            return content
        except Exception as e:
            log.warning("LM Studio error: %s", e)
            return _SimpleMockAdapter().generate(prompt, system)


class TaskDispatcher:
    def __init__(self, core) -> None:
        self.core = core
        self._adaptive = AdaptiveModuleCreator() if _ADAPTIVE_AVAILABLE else None
        if getattr(core, "use_real_ai", False):
            self._adapter = _LMStudioAdapter()
            log.info("Dispatcher using LM Studio adapter")
        else:
            self._adapter = _SimpleMockAdapter()
            log.info("Dispatcher using mock adapter")

    def dispatch(self, instruction: str) -> str:
        prompt = instruction
        if self._adaptive:
            try:
                prompt = self._adaptive.prepare_prompt(prompt)
            except Exception as e:
                log.warning("Adaptive prepare_prompt failed: %s", e)
        try:
            return self._adapter.generate(prompt)
        except Exception as e:
            log.error("Adapter generate() failed: %s", e)
            return f"[error] adapter failure: {e}"
