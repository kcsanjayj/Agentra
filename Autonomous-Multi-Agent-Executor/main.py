import logging

from src.agents.planner_agent import PlannerAgent
from src.agents.research_agent import ResearcherAgent
from src.agents.writer_agent import WriterAgent
from src.agents.coder_agent import CoderAgent
from src.agents.verifier_agent import VerifierAgent
from src.executor.agent_executor import AgentExecutor  # Fixed import

logging.basicConfig(level=logging.INFO)

def main():
    agents = {
        "planner": PlannerAgent("Planner"),
        "research": ResearcherAgent("Researcher"),
        "writer": WriterAgent("Writer"),
        "coder": CoderAgent("Coder"),
        "verifier": VerifierAgent("Verifier")
    }

    executor = AgentExecutor(agents)

    tasks = [
        {"type": "research", "description": "Study climate change"},
        {"type": "writer", "description": "Write a scientific report"},
        {"type": "coder", "description": "print('Hello from agent!')"},
        {"type": "verifier", "description": "Verify dataset integrity"}
    ]

    for t in tasks:
        logging.info(f"Processing task: {t}")
        output = executor.process(t)
        logging.info(f"Output: {output}\n")

if __name__ == "__main__":
    main()