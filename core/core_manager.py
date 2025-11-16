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
