from .base_agent import BaseAgent
from ..tools.python_executor import execute_python_code

class CoderAgent(BaseAgent):
    """Agent that writes and executes Python code."""

    def perceive(self, code: str):
        self.remember("code", code)

    def act(self):
        code = self.recall("code")
        stdout, stderr = execute_python_code(code)
        return {"stdout": stdout, "stderr": stderr}
