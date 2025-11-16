import logging
from typing import Optional
from core.adapters.mock_adapters import MockTextAdapter
from core.adapters.real_adapters import LMStudioAdapter

log = logging.getLogger("TaskDispatcher")

try:
    from core.modules.adaptive_module_creator import AdaptiveModuleCreator
    _ADAPTIVE_AVAILABLE = True
except Exception as e:
    log.debug("AdaptiveModuleCreator not available: %s", e)
    _ADAPTIVE_AVAILABLE = False
    AdaptiveModuleCreator = None  # type: ignore


class TaskDispatcher:
    def __init__(self, core) -> None:
        self.core = core
        self._adaptive = AdaptiveModuleCreator() if _ADAPTIVE_AVAILABLE else None
        if getattr(core, "use_real_ai", False):
            self._adapter = LMStudioAdapter()
            log.info("Dispatcher using LMStudioAdapter")
        else:
            self._adapter = MockTextAdapter()
            log.info("Dispatcher using MockTextAdapter")

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
