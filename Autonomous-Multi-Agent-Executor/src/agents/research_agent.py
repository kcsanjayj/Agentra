from .base_agent import BaseAgent

class ResearcherAgent(BaseAgent):
    """Agent that performs research-like reasoning."""

    def perceive(self, topic: str):
        self.remember("topic", topic)

    def act(self):
        topic = self.recall("topic")
        insights = f"Research insights about '{topic}': Climate patterns, causes, solutions, datasets."
        return insights
