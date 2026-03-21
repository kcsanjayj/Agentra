from .base_agent import BaseAgent

class PlannerAgent(BaseAgent):
    """Creates plans for tasks."""

    def perceive(self, task: str):
        self.remember("task", task)

    def act(self):
        task = self.recall("task")
        plan = {
            "task": task,
            "steps": [
                f"Research the task: {task}",
                f"Write summary for: {task}",
                f"Code demonstration for: {task}",
                f"Verify output for: {task}"
            ]
        }
        return plan
