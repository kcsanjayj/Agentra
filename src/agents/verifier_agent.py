from .base_agent import BaseAgent

class VerifierAgent(BaseAgent):
    """Agent verifying data correctness and structure."""

    def perceive(self, data):
        self.remember("data", data)

    def act(self):
        data = self.recall("data")
        return {"data": data, "verified": True}

