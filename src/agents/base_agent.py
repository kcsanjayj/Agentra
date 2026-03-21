class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str):
        self.name = name
        self.memory = {}

    def remember(self, key, value):
        self.memory[key] = value

    def recall(self, key):
        return self.memory.get(key)

    def perceive(self, data):
        raise NotImplementedError

    def act(self):
        raise NotImplementedError

    def __repr__(self):
        return f"<Agent: {self.name}>"
