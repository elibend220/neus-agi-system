import logging
import sys

class Logger:
    def __init__(self, level: str = "INFO") -> None:
        lvl = getattr(logging, level.upper(), logging.INFO)
        logging.basicConfig(level=lvl, format="%(asctime)s | %(levelname)s | %(name)s | %(message)s")
        self._log = logging.getLogger("NEUS-AGI")

    def log(self, msg: str) -> None:
        try:
            self._log.info(str(msg))
        except Exception:
            # Always stay non-crashing
            print(str(msg), file=sys.stderr)
