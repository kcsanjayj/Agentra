from .base_agent import BaseAgent

class WriterAgent(BaseAgent):
    """Agent that generates structured written content."""

    def perceive(self, content_description: str):
        self.remember("content", content_description)

    def act(self):
        desc = self.recall("content")
        article = f"=== Report ===\nTopic: {desc}\nThis report outlines key insights and findings."
        return article
