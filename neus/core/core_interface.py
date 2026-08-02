import logging
logger = logging.getLogger(__name__)

class CoreInterface:
    def __init__(self, core_manager):
        self.core = core_manager

    def request_data(self):
        return self.core.get_latest_data()

    def report_performance(self, agent_name: str, score: float):
        self.core.record_performance(score, agent_name)
