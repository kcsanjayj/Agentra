"""
Orchestrator for managing and coordinating multiple agents.

This module contains the main orchestrator that manages agent workflows,
coordinates task execution, and handles communication between agents.
"""

from typing import Dict, Any, List, Optional, Union
import asyncio
import logging
from datetime import datetime
from enum import Enum

from app.agents.base import BaseAgent, AgentResponse
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.coder import CoderAgent
from app.agents.verifier import VerifierAgent
from app.models.schemas import TaskRequest, TaskResponse, ExecutionPlan, TaskStatus

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class AgentOrchestrator:
    """Main orchestrator for managing agent workflows."""
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.agents: Dict[str, BaseAgent] = {}
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.task_queue: List[Dict[str, Any]] = []
        self.max_concurrent_tasks = 5
        self.logger = logging.getLogger("orchestrator")
        
    async def initialize(self) -> None:
        """Initialize all agents."""
        self.logger.info("Initializing agent orchestrator")
        
        # Initialize all agents
        self.agents = {
            "planner": PlannerAgent(),
            "researcher": ResearcherAgent(),
            "writer": WriterAgent(),
            "coder": CoderAgent(),
            "verifier": VerifierAgent()
        }
        
        # Setup all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.setup()
                self.logger.info(f"Initialized agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to initialize agent {agent_name}: {str(e)}")
        
        self.logger.info(f"Orchestrator initialized with {len(self.agents)} agents")
    
    async def cleanup(self) -> None:
        """Cleanup all agents and resources."""
        self.logger.info("Cleaning up orchestrator")
        
        # Cleanup all agents
        for agent_name, agent in self.agents.items():
            try:
                await agent.cleanup()
                self.logger.info(f"Cleaned up agent: {agent_name}")
            except Exception as e:
                self.logger.error(f"Failed to cleanup agent {agent_name}: {str(e)}")
        
        # Clear task queue and active tasks
        self.task_queue.clear()
        self.active_tasks.clear()
        
        self.logger.info("Orchestrator cleanup completed")
    
    async def submit_task(self, task_request: TaskRequest) -> TaskResponse:
        """
        Submit a new task for execution.
        
        Args:
            task_request: Task request containing all necessary information
            
        Returns:
            TaskResponse with task ID and initial status
        """
        try:
            # Generate unique task ID
            task_id = self._generate_task_id()
            
            # Create task record
            task = {
                "id": task_id,
                "request": task_request,
                "status": TaskStatus.PENDING,
                "priority": TaskPriority(task_request.priority),
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "execution_plan": None,
                "results": {},
                "current_step": 0,
                "total_steps": 0,
                "errors": []
            }
            
            # Add to queue
            self.task_queue.append(task)
            self.active_tasks[task_id] = task
            
            self.logger.info(f"Task submitted: {task_id} ({task_request.task_type})")
            
            # Start processing if capacity available
            await self._process_queue()
            
            return TaskResponse(
                task_id=task_id,
                status=TaskStatus.PENDING,
                message="Task submitted successfully",
                created_at=task["created_at"]
            )
            
        except Exception as e:
            self.logger.error(f"Failed to submit task: {str(e)}")
            raise
    
    async def get_task_status(self, task_id: str) -> Optional[TaskResponse]:
        """
        Get the current status of a task.
        
        Args:
            task_id: ID of the task to check
            
        Returns:
            TaskResponse with current status or None if task not found
        """
        task = self.active_tasks.get(task_id)
        if not task:
            return None
        
        return TaskResponse(
            task_id=task_id,
            status=task["status"],
            message=self._get_status_message(task),
            created_at=task["created_at"],
            updated_at=task["updated_at"],
            execution_plan=task["execution_plan"],
            results=task["results"]
        )
    
    async def cancel_task(self, task_id: str) -> bool:
        """
        Cancel a task.
        
        Args:
            task_id: ID of the task to cancel
            
        Returns:
            True if task was cancelled, False if not found or already completed
        """
        task = self.active_tasks.get(task_id)
        if not task:
            return False
        
        if task["status"] in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
            return False
        
        task["status"] = TaskStatus.CANCELLED
        task["updated_at"] = datetime.now()
        
        self.logger.info(f"Task cancelled: {task_id}")
        return True
    
    async def _process_queue(self) -> None:
        """Process the task queue."""
        # Count active running tasks
        running_tasks = sum(
            1 for task in self.active_tasks.values()
            if task["status"] == TaskStatus.RUNNING
        )
        
        # Process tasks if capacity available
        while (running_tasks < self.max_concurrent_tasks and 
               self.task_queue and 
               any(task["status"] == TaskStatus.PENDING for task in self.task_queue)):
            
            # Find next pending task (by priority)
            next_task = self._get_next_pending_task()
            if not next_task:
                break
            
            # Start task execution
            asyncio.create_task(self._execute_task(next_task))
            running_tasks += 1
    
    def _get_next_pending_task(self) -> Optional[Dict[str, Any]]:
        """Get the next pending task based on priority."""
        pending_tasks = [
            task for task in self.task_queue
            if task["status"] == TaskStatus.PENDING
        ]
        
        if not pending_tasks:
            return None
        
        # Sort by priority
        priority_order = {
            TaskPriority.URGENT: 0,
            TaskPriority.HIGH: 1,
            TaskPriority.MEDIUM: 2,
            TaskPriority.LOW: 3
        }
        
        pending_tasks.sort(
            key=lambda t: (priority_order[t["priority"]], t["created_at"])
        )
        
        return pending_tasks[0]
    
    async def _execute_task(self, task: Dict[str, Any]) -> None:
        """Execute a single task."""
        task_id = task["id"]
        task_request = task["request"]
        
        try:
            # Update status to running
            task["status"] = TaskStatus.RUNNING
            task["updated_at"] = datetime.now()
            
            self.logger.info(f"Starting task execution: {task_id}")
            
            # Step 1: Create execution plan
            execution_plan = await self._create_execution_plan(task_request)
            task["execution_plan"] = execution_plan
            task["total_steps"] = len(execution_plan.steps)
            task["updated_at"] = datetime.now()
            
            # Step 2: Execute plan steps
            results = await self._execute_execution_plan(execution_plan, task)
            task["results"] = results
            task["current_step"] = task["total_steps"]
            task["updated_at"] = datetime.now()
            
            # Step 3: Final verification
            if task_request.include_verification:
                verification_result = await self._verify_results(results, task_request)
                task["results"]["verification"] = verification_result
                task["updated_at"] = datetime.now()
            
            # Mark as completed
            task["status"] = TaskStatus.COMPLETED
            task["updated_at"] = datetime.now()
            
            self.logger.info(f"Task completed successfully: {task_id}")
            
        except Exception as e:
            # Mark as failed
            task["status"] = TaskStatus.FAILED
            task["errors"].append(str(e))
            task["updated_at"] = datetime.now()
            
            self.logger.error(f"Task failed: {task_id} - {str(e)}")
        
        finally:
            # Process queue for next task
            await self._process_queue()
    
    async def _create_execution_plan(self, task_request: TaskRequest) -> ExecutionPlan:
        """Create an execution plan for the task."""
        planner_agent = self.agents["planner"]
        
        planner_task = {
            "type": "planning",
            "description": task_request.description,
            "requirements": task_request.requirements,
            "strategy": task_request.execution_strategy
        }
        
        response = await planner_agent.execute(planner_task)
        
        if not response.success:
            raise Exception(f"Failed to create execution plan: {response.error}")
        
        # Create execution plan object
        plan_data = response.data
        steps = []
        
        for i, step_data in enumerate(plan_data["plan"]):
            step = {
                "id": f"step_{i+1}",
                "agent": step_data["agent"],
                "task": step_data["task"],
                "dependencies": step_data.get("dependencies", []),
                "status": "pending",
                "result": None
            }
            steps.append(step)
        
        return ExecutionPlan(
            task_id=self._generate_task_id(),
            steps=steps,
            strategy=plan_data["strategy"],
            estimated_complexity=plan_data["complexity"],
            created_at=datetime.now()
        )
    
    async def _execute_execution_plan(self, execution_plan: ExecutionPlan, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the steps in an execution plan."""
        results = {}
        step_results = {}
        
        for i, step in enumerate(execution_plan.steps):
            # Update current step
            task["current_step"] = i + 1
            task["updated_at"] = datetime.now()
            
            # Check dependencies
            if not self._check_dependencies(step, step_results):
                raise Exception(f"Dependencies not met for step: {step['id']}")
            
            # Execute step
            try:
                step_result = await self._execute_step(step, step_results)
                step_results[step["id"]] = step_result
                step["status"] = "completed"
                step["result"] = step_result
                
                self.logger.info(f"Step completed: {step['id']} ({step['agent']})")
                
            except Exception as e:
                step["status"] = "failed"
                step["result"] = {"error": str(e)}
                raise Exception(f"Step {step['id']} failed: {str(e)}")
        
        results["steps"] = step_results
        results["summary"] = self._generate_execution_summary(execution_plan, step_results)
        
        return results
    
    async def _execute_step(self, step: Dict[str, Any], previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single step."""
        agent_name = step["agent"]
        agent = self.agents.get(agent_name)
        
        if not agent:
            raise Exception(f"Agent not found: {agent_name}")
        
        # Prepare task for agent
        agent_task = {
            "type": agent_name,
            "description": step["task"],
            "context": previous_results,
            "step_id": step["id"]
        }
        
        # Execute agent task
        response = await agent.execute(agent_task)
        
        if not response.success:
            raise Exception(f"Agent {agent_name} failed: {response.error}")
        
        return response.data
    
    def _check_dependencies(self, step: Dict[str, Any], completed_results: Dict[str, Any]) -> bool:
        """Check if all dependencies for a step are satisfied."""
        dependencies = step.get("dependencies", [])
        
        for dep in dependencies:
            if dep not in completed_results:
                return False
        
        return True
    
    async def _verify_results(self, results: Dict[str, Any], task_request: TaskRequest) -> Dict[str, Any]:
        """Verify the execution results."""
        verifier_agent = self.agents["verifier"]
        
        verification_task = {
            "type": "verification",
            "verification_type": "content",
            "content": results,
            "requirements": task_request.requirements,
            "criteria": task_request.acceptance_criteria
        }
        
        response = await verifier_agent.execute(verification_task)
        
        if not response.success:
            return {"error": response.error}
        
        return response.data
    
    def _generate_execution_summary(self, execution_plan: ExecutionPlan, step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the execution."""
        total_steps = len(execution_plan.steps)
        completed_steps = len([s for s in execution_plan.steps if s["status"] == "completed"])
        
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "success_rate": completed_steps / total_steps if total_steps > 0 else 0,
            "strategy": execution_plan.strategy,
            "complexity": execution_plan.estimated_complexity
        }
    
    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _get_status_message(self, task: Dict[str, Any]) -> str:
        """Get a descriptive status message for a task."""
        status = task["status"]
        current_step = task.get("current_step", 0)
        total_steps = task.get("total_steps", 0)
        
        if status == TaskStatus.PENDING:
            return "Task is waiting to be processed"
        elif status == TaskStatus.RUNNING:
            if total_steps > 0:
                return f"Executing step {current_step} of {total_steps}"
            else:
                return "Task is running"
        elif status == TaskStatus.COMPLETED:
            return "Task completed successfully"
        elif status == TaskStatus.FAILED:
            return f"Task failed: {', '.join(task['errors'])}"
        elif status == TaskStatus.CANCELLED:
            return "Task was cancelled"
        else:
            return "Unknown status"
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get the status of all agents."""
        return {
            "total_agents": len(self.agents),
            "agent_names": list(self.agents.keys()),
            "active_tasks": len([t for t in self.active_tasks.values() if t["status"] == TaskStatus.RUNNING]),
            "queued_tasks": len([t for t in self.task_queue if t["status"] == TaskStatus.PENDING]),
            "completed_tasks": len([t for t in self.active_tasks.values() if t["status"] == TaskStatus.COMPLETED])
        }
