"""
Planner agent for breaking down complex tasks into executable steps.
"""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentResponse
import logging

logger = logging.getLogger(__name__)

class PlannerAgent(BaseAgent):
    """Agent responsible for planning and task decomposition."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("planner", config)
        self.planning_strategies = {
            "sequential": self._sequential_planning,
            "parallel": self._parallel_planning,
            "hierarchical": self._hierarchical_planning
        }
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute planning task to break down complex tasks.
        
        Args:
            task: Dictionary containing task description and requirements
            
        Returns:
            AgentResponse with execution plan
        """
        try:
            if not self.validate_task(task):
                return AgentResponse(
                    success=False,
                    error="Invalid task format for planner agent"
                )
            
            task_description = task.get("description", "")
            requirements = task.get("requirements", [])
            strategy = task.get("strategy", "sequential")
            
            self.logger.info(f"Planning task: {task_description[:100]}...")
            
            # Choose planning strategy
            planning_func = self.planning_strategies.get(
                strategy, self._sequential_planning
            )
            
            # Generate execution plan
            plan = await planning_func(task_description, requirements)
            
            return AgentResponse(
                success=True,
                data={
                    "plan": plan,
                    "strategy": strategy,
                    "estimated_steps": len(plan),
                    "complexity": self._assess_complexity(plan)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in planner agent: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Planning failed: {str(e)}"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return list of planner capabilities."""
        return [
            "task_decomposition",
            "sequential_planning",
            "parallel_planning",
            "hierarchical_planning",
            "dependency_analysis",
            "resource_estimation"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for planning tasks."""
        return ["description"]
    
    async def _sequential_planning(self, description: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate sequential execution plan."""
        # This would typically use an LLM to generate the plan
        # For now, return a basic structure
        return [
            {
                "step": 1,
                "agent": "researcher",
                "task": "Research requirements and gather information",
                "dependencies": []
            },
            {
                "step": 2,
                "agent": "writer", 
                "task": "Create initial draft based on research",
                "dependencies": [1]
            },
            {
                "step": 3,
                "agent": "verifier",
                "task": "Review and verify the output",
                "dependencies": [2]
            }
        ]
    
    async def _parallel_planning(self, description: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate parallel execution plan."""
        return [
            {
                "step": 1,
                "agent": "researcher",
                "task": "Research requirements and gather information",
                "dependencies": []
            },
            {
                "step": 2,
                "agent": "writer",
                "task": "Create initial draft based on research", 
                "dependencies": [1]
            },
            {
                "step": 2,
                "agent": "coder",
                "task": "Implement code components",
                "dependencies": [1]
            }
        ]
    
    async def _hierarchical_planning(self, description: str, requirements: List[str]) -> List[Dict[str, Any]]:
        """Generate hierarchical execution plan."""
        return [
            {
                "step": 1,
                "agent": "planner",
                "task": "Create detailed sub-plans",
                "dependencies": [],
                "subtasks": [
                    {"agent": "researcher", "task": "Research phase"},
                    {"agent": "writer", "task": "Writing phase"},
                    {"agent": "coder", "task": "Implementation phase"}
                ]
            }
        ]
    
    def _assess_complexity(self, plan: List[Dict[str, Any]]) -> str:
        """Assess the complexity of the generated plan."""
        step_count = len(plan)
        if step_count <= 3:
            return "low"
        elif step_count <= 6:
            return "medium"
        else:
            return "high"
