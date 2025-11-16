import json
from core.memory import Memory
from core.task_dispatcher import TaskDispatcher
from utils.logger import Logger

class CoreManager:
    def __init__(self, use_real_ai=True):
        self.logger = Logger()
        self.memory = Memory()
        self.use_real_ai = use_real_ai
        self.dispatcher = TaskDispatcher(self)
        self.load_settings()

        if self.use_real_ai:
            self.logger.log("Real AI mode enabled.")
        else:
            self.logger.log("Mock AI mode enabled.")

    def load_settings(self):
        try:
            with open("config/settings.json", "r", encoding="utf-8") as f:
                self.settings = json.load(f)
            self.logger.log("Settings loaded.")
        except FileNotFoundError:
            self.settings = {}
            self.logger.log("Settings file not found. Using defaults.")

    def process(self, instruction):
        self.logger.log(f"Processing instruction: {instruction}")
        return self.dispatcher.dispatch(instruction)
    def auto_improve(self):
        """Trigger self-improvement via SelfBuilder and reload modules."""
        from core.self_builder import SelfBuilder
        self.logger.log("Analyzing")
        perf = self.memory.get("performance_metrics", [])[-10:]
        recent = self.memory.get_all()
        builder = SelfBuilder(root=".")
        self.logger.log("Generating improvements")
        result = builder.run(adapter=self.dispatcher._adapter, agent_name="core_manager", recent_memory=recent, performance=perf)
        self.logger.log("Applying patches")
        # patches already applied by builder
        self.logger.log("Reloading modules")
        import importlib
        importlib.invalidate_caches()
        try:
            importlib.import_module("core.core_manager")
        except Exception as e:
            self.logger.log(f"Reload error: {e}")
        self.logger.log("Self-upgrade complete.")
        self.memory.set("last_self_improve", result)
        return result
