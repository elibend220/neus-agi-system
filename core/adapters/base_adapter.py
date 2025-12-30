# core/adapters/base_adapter.py

import abc

class BaseAdapter(abc.ABC):
    """
    Base class for any LLM adapter used by the NEUS-AGI system.
    """

    @abc.abstractmethod
    def send(self, prompt: str) -> str:
        """Send prompt to LLM and return output."""
        pass

    @abc.abstractmethod
    def name(self) -> str:
        """Return adapter name."""
        pass
