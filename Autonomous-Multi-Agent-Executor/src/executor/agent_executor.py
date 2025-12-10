class AgentExecutor:
    """Executes tasks by routing them to the appropriate agent."""

    def __init__(self, agents: dict):
        self.agents = agents

    def process(self, task: dict):
        agent_type = task["type"]
        description = task["description"]

        if agent_type not in self.agents:
            return {"error": f"Unknown agent type: {agent_type}"}

        agent = self.agents[agent_type]

        agent.perceive(description)
        return agent.act()
