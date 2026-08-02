import os
import json
import logging
from typing import Any, Dict

log = logging.getLogger("SimpleMemory")

class SimpleMemory:
    def __init__(self, cache_dir: str = "./cache", filename: str = "memory.json", persist: bool = True):
        self.cache_dir = cache_dir
        self.filename = filename
        self.persist = persist
        self._store: Dict[str, Any] = {}
        os.makedirs(self.cache_dir, exist_ok=True)
        if self.persist:
            self.load()

    @property
    def path(self) -> str:
        return os.path.join(self.cache_dir, self.filename)

    def set(self, key: str, value: Any) -> None:
        self._store[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def get_all(self) -> Dict[str, Any]:
        return dict(self._store)

    def save(self) -> None:
        if not self.persist:
            return
        try:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self._store, f, ensure_ascii=False, indent=2)
        except Exception as e:
            log.warning("Failed to save memory: %s", e)

    def load(self) -> None:
        if not self.persist:
            return
        try:
            if os.path.exists(self.path):
                with open(self.path, "r", encoding="utf-8") as f:
                    self._store = json.load(f)
        except Exception as e:
            log.warning("Failed to load memory: %s", e)
            self._store = {}
