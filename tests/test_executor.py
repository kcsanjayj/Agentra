"""
Tests for the executor module.

This module contains unit tests and integration tests for the orchestrator
and task execution components.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any

from app.executor.orchestrator import AgentOrchestrator, TaskPriority, TaskStatus
from app.models.schemas import TaskRequest, TaskResponse, ExecutionPlan, ExecutionStrategy
from app.agents.base import BaseAgent, AgentResponse


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, name: str, response_data: Dict[str, Any] = None, should_fail: bool = False):
        super().__init__(name)
        self.response_data = response_data or {"result": f"mock result from {name}"}
        self.should_fail = should_fail
        self.setup_called = False
        self.cleanup_called = False
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """Mock execution."""
        await asyncio.sleep(0.1)  # Simulate work
        
        if self.should_fail:
            return AgentResponse(
                success=False,
                error=f"Mock agent {self.name} failed"
            )
        
        return AgentResponse(
            success=True,
            data=self.response_data
        )
    
    def get_capabilities(self) -> list:
        """Mock capabilities."""
        return ["mock_capability"]
    
    async def setup(self):
        """Mock setup."""
        self.setup_called = True
    
    async def cleanup(self):
        """Mock cleanup."""
        self.cleanup_called = True


class TestAgentOrchestrator:
    """Test cases for AgentOrchestrator class."""
    
    @pytest.fixture
    async def orchestrator(self):
        """Create an orchestrator instance for testing."""
        orchestrator = AgentOrchestrator()
        
        # Replace real agents with mock agents
        mock_agents = {
            "planner": MockAgent("planner", {"plan": [{"step": 1, "agent": "mock", "task": "test"}]}),
            "researcher": MockAgent("researcher", {"findings": ["test finding"]}),
            "writer": MockAgent("writer", {"content": "test content"}),
            "coder": MockAgent("coder", {"code": "test code"}),
            "verifier": MockAgent("verifier", {"verification": "passed"})
        }
        
        orchestrator.agents = mock_agents
        await orchestrator.setup()
        
        yield orchestrator
        
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_orchestrator_initialization(self):
        """Test orchestrator initialization."""
        orchestrator = AgentOrchestrator()
        
        # Test initial state
        assert len(orchestrator.agents) == 0
        assert len(orchestrator.active_tasks) == 0
        assert len(orchestrator.task_queue) == 0
        assert orchestrator.max_concurrent_tasks == 5
    
    @pytest.mark.asyncio
    async def test_orchestrator_setup(self):
        """Test orchestrator setup with real agents."""
        orchestrator = AgentOrchestrator()
        await orchestrator.setup()
        
        # Should have all agents initialized
        assert len(orchestrator.agents) == 5
        assert "planner" in orchestrator.agents
        assert "researcher" in orchestrator.agents
        assert "writer" in orchestrator.agents
        assert "coder" in orchestrator.agents
        assert "verifier" in orchestrator.agents
        
        await orchestrator.cleanup()
    
    @pytest.mark.asyncio
    async def test_submit_task_success(self, orchestrator):
        """Test successful task submission."""
        task_request = TaskRequest(
            task_type="test_task",
            description="Test task for orchestrator",
            requirements=["requirement1", "requirement2"],
            priority=TaskPriority.HIGH,
            execution_strategy=ExecutionStrategy.SEQUENTIAL
        )
        
        response = await orchestrator.submit_task(task_request)
        
        assert response.status == TaskStatus.PENDING
        assert response.task_id is not None
        assert response.message == "Task submitted successfully"
        assert response.created_at is not None
        
        # Task should be in active tasks
        assert response.task_id in orchestrator.active_tasks
        
        # Task should be in queue
        assert len(orchestrator.task_queue) > 0
    
    @pytest.mark.asyncio
    async def test_submit_task_invalid_request(self, orchestrator):
        """Test task submission with invalid request."""
        # Create invalid task request (empty description)
        with pytest.raises(Exception):
            task_request = TaskRequest(
                task_type="test_task",
                description="",  # Empty description should fail validation
                requirements=[]
            )
            await orchestrator.submit_task(task_request)
    
    @pytest.mark.asyncio
    async def test_get_task_status_success(self, orchestrator):
        """Test getting task status successfully."""
        # Submit a task first
        task_request = TaskRequest(
            task_type="test_task",
            description="Test task for status check"
        )
        submit_response = await orchestrator.submit_task(task_request)
        
        # Get task status
        status_response = await orchestrator.get_task_status(submit_response.task_id)
        
        assert status_response is not None
        assert status_response.task_id == submit_response.task_id
        assert status_response.status in [TaskStatus.PENDING, TaskStatus.RUNNING, TaskStatus.COMPLETED]
    
    @pytest.mark.asyncio
    async def test_get_task_status_not_found(self, orchestrator):
        """Test getting status of non-existent task."""
        response = await orchestrator.get_task_status("non_existent_task_id")
        assert response is None
    
    @pytest.mark.asyncio
    async def test_cancel_task_success(self, orchestrator):
        """Test successful task cancellation."""
        # Submit a task first
        task_request = TaskRequest(
            task_type="test_task",
            description="Test task for cancellation"
        )
        submit_response = await orchestrator.submit_task(task_request)
        
        # Cancel the task
        cancel_success = await orchestrator.cancel_task(submit_response.task_id)
        assert cancel_success == True
        
        # Check task status
        status_response = await orchestrator.get_task_status(submit_response.task_id)
        assert status_response.status == TaskStatus.CANCELLED
    
    @pytest.mark.asyncio
    async def test_cancel_task_not_found(self, orchestrator):
        """Test cancelling non-existent task."""
        cancel_success = await orchestrator.cancel_task("non_existent_task_id")
        assert cancel_success == False
    
    @pytest.mark.asyncio
    async def test_cancel_completed_task(self, orchestrator):
        """Test cancelling already completed task."""
        # Submit and wait for task to complete
        task_request = TaskRequest(
            task_type="test_task",
            description="Test task for completion"
        )
        submit_response = await orchestrator.submit_task(task_request)
        
        # Wait for task to complete
        await asyncio.sleep(1)
        
        # Try to cancel completed task
        cancel_success = await orchestrator.cancel_task(submit_response.task_id)
        assert cancel_success == False
    
    @pytest.mark.asyncio
    async def test_task_execution_workflow(self, orchestrator):
        """Test complete task execution workflow."""
        task_request = TaskRequest(
            task_type="research_and_write",
            description="Research AI trends and write an article",
            requirements=["research", "writing", "verification"],
            priority=TaskPriority.MEDIUM,
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            include_verification=True
        )
        
        # Submit task
        submit_response = await orchestrator.submit_task(task_request)
        task_id = submit_response.task_id
        
        # Wait for task to complete
        max_wait_time = 10  # seconds
        wait_interval = 0.5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            status_response = await orchestrator.get_task_status(task_id)
            if status_response.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        # Check final status
        final_status = await orchestrator.get_task_status(task_id)
        assert final_status.status == TaskStatus.COMPLETED
        assert final_status.results is not None
        assert "steps" in final_status.results
        assert "summary" in final_status.results
        assert "verification" in final_status.results
    
    @pytest.mark.asyncio
    async def test_task_execution_with_failure(self, orchestrator):
        """Test task execution when an agent fails."""
        # Replace an agent with a failing mock
        failing_agent = MockAgent("researcher", should_fail=True)
        orchestrator.agents["researcher"] = failing_agent
        
        task_request = TaskRequest(
            task_type="failing_task",
            description="Task that should fail during execution",
            requirements=["research"]
        )
        
        # Submit task
        submit_response = await orchestrator.submit_task(task_request)
        task_id = submit_response.task_id
        
        # Wait for task to complete (should fail)
        max_wait_time = 10
        wait_interval = 0.5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            status_response = await orchestrator.get_task_status(task_id)
            if status_response.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        # Check final status
        final_status = await orchestrator.get_task_status(task_id)
        assert final_status.status == TaskStatus.FAILED
        assert final_status.error is not None
    
    @pytest.mark.asyncio
    async def test_concurrent_task_execution(self, orchestrator):
        """Test execution of multiple concurrent tasks."""
        # Submit multiple tasks
        task_requests = [
            TaskRequest(
                task_type=f"concurrent_task_{i}",
                description=f"Concurrent task {i}",
                priority=TaskPriority.MEDIUM
            )
            for i in range(3)
        ]
        
        submit_responses = []
        for task_request in task_requests:
            response = await orchestrator.submit_task(task_request)
            submit_responses.append(response)
        
        # Wait for all tasks to complete
        max_wait_time = 15
        wait_interval = 0.5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            all_completed = True
            for response in submit_responses:
                status = await orchestrator.get_task_status(response.task_id)
                if status.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    all_completed = False
                    break
            
            if all_completed:
                break
            
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        # Check all tasks completed
        for response in submit_responses:
            final_status = await orchestrator.get_task_status(response.task_id)
            assert final_status.status == TaskStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_task_priority_ordering(self, orchestrator):
        """Test that tasks are executed in priority order."""
        # Submit tasks with different priorities
        low_priority_task = TaskRequest(
            task_type="low_priority",
            description="Low priority task",
            priority=TaskPriority.LOW
        )
        
        high_priority_task = TaskRequest(
            task_type="high_priority",
            description="High priority task",
            priority=TaskPriority.HIGH
        )
        
        # Submit low priority first
        low_response = await orchestrator.submit_task(low_priority_task)
        
        # Submit high priority second
        high_response = await orchestrator.submit_task(high_priority_task)
        
        # Check that high priority task is processed first
        # (This is a simplified test - in reality, timing might vary)
        assert len(orchestrator.task_queue) >= 2
        
        # Find tasks in queue
        low_task = next((t for t in orchestrator.task_queue if t["id"] == low_response.task_id), None)
        high_task = next((t for t in orchestrator.task_queue if t["id"] == high_response.task_id), None)
        
        assert low_task is not None
        assert high_task is not None
        assert low_task["priority"] == TaskPriority.LOW
        assert high_task["priority"] == TaskPriority.HIGH
    
    @pytest.mark.asyncio
    async def test_execution_plan_creation(self, orchestrator):
        """Test execution plan creation."""
        task_request = TaskRequest(
            task_type="test_planning",
            description="Test task for planning",
            execution_strategy=ExecutionStrategy.PARALLEL
        )
        
        # Create execution plan directly
        execution_plan = await orchestrator._create_execution_plan(task_request)
        
        assert execution_plan is not None
        assert execution_plan.task_id is not None
        assert len(execution_plan.steps) > 0
        assert execution_plan.strategy == ExecutionStrategy.PARALLEL
        assert execution_plan.estimated_complexity in ["low", "medium", "high"]
        assert execution_plan.created_at is not None
    
    @pytest.mark.asyncio
    async def test_agent_status(self, orchestrator):
        """Test getting agent status."""
        status = orchestrator.get_agent_status()
        
        assert "total_agents" in status
        assert "agent_names" in status
        assert "active_tasks" in status
        assert "queued_tasks" in status
        assert "completed_tasks" in status
        
        assert status["total_agents"] == 5
        assert len(status["agent_names"]) == 5
        assert all(name in status["agent_names"] for name in 
                  ["planner", "researcher", "writer", "coder", "verifier"])
    
    @pytest.mark.asyncio
    async def test_max_concurrent_tasks_limit(self, orchestrator):
        """Test that concurrent task limit is respected."""
        # Set a low limit for testing
        original_limit = orchestrator.max_concurrent_tasks
        orchestrator.max_concurrent_tasks = 2
        
        # Submit more tasks than the limit
        task_requests = [
            TaskRequest(
                task_type=f"limit_test_{i}",
                description=f"Task {i} for limit testing"
            )
            for i in range(5)
        ]
        
        # Submit all tasks quickly
        submit_responses = []
        for task_request in task_requests:
            response = await orchestrator.submit_task(task_request)
            submit_responses.append(response)
        
        # Check that only 2 tasks are running at most
        running_tasks = sum(
            1 for task in orchestrator.active_tasks.values()
            if task["status"] == TaskStatus.RUNNING
        )
        
        assert running_tasks <= 2
        
        # Restore original limit
        orchestrator.max_concurrent_tasks = original_limit
    
    @pytest.mark.asyncio
    async def test_task_dependencies(self, orchestrator):
        """Test task dependency handling."""
        # Create a custom execution plan with dependencies
        execution_plan = ExecutionPlan(
            task_id="test_deps",
            steps=[
                {
                    "id": "step_1",
                    "agent": "planner",
                    "task": "Plan the work",
                    "dependencies": [],
                    "status": TaskStatus.PENDING
                },
                {
                    "id": "step_2", 
                    "agent": "researcher",
                    "task": "Research the topic",
                    "dependencies": ["step_1"],
                    "status": TaskStatus.PENDING
                },
                {
                    "id": "step_3",
                    "agent": "writer",
                    "task": "Write the content",
                    "dependencies": ["step_2"],
                    "status": TaskStatus.PENDING
                }
            ],
            strategy=ExecutionStrategy.SEQUENTIAL,
            estimated_complexity="medium",
            created_at=datetime.now()
        )
        
        # Test dependency checking
        assert orchestrator._check_dependencies(execution_plan.steps[0], {}) == True
        assert orchestrator._check_dependencies(execution_plan.steps[1], {}) == False
        assert orchestrator._check_dependencies(execution_plan.steps[1], {"step_1": {}}) == True
        assert orchestrator._check_dependencies(execution_plan.steps[2], {"step_1": {}}) == False
        assert orchestrator._check_dependencies(execution_plan.steps[2], {"step_1": {}, "step_2": {}}) == True


# Integration Tests
@pytest.mark.asyncio
async def test_full_system_integration():
    """Test full system integration with real agents."""
    orchestrator = AgentOrchestrator()
    await orchestrator.setup()
    
    try:
        # Create a comprehensive task
        task_request = TaskRequest(
            task_type="comprehensive_research",
            description="Research and write about the impact of AI on healthcare",
            requirements=["research", "analysis", "writing", "verification"],
            priority=TaskPriority.HIGH,
            execution_strategy=ExecutionStrategy.SEQUENTIAL,
            include_verification=True,
            acceptance_criteria={
                "min_content_length": 500,
                "must_include_sources": True,
                "grammar_check": True
            }
        )
        
        # Submit task
        response = await orchestrator.submit_task(task_request)
        task_id = response.task_id
        
        # Wait for completion
        max_wait_time = 30
        wait_interval = 1
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            status = await orchestrator.get_task_status(task_id)
            if status.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        # Verify completion
        final_status = await orchestrator.get_task_status(task_id)
        assert final_status.status == TaskStatus.COMPLETED
        assert final_status.results is not None
        
        # Check results structure
        results = final_status.results
        assert "steps" in results
        assert "summary" in results
        assert "verification" in results
        
        # Check execution plan
        execution_plan = final_status.execution_plan
        assert execution_plan is not None
        assert len(execution_plan.steps) > 0
        
        print(f"Integration test completed successfully in {elapsed_time} seconds")
        
    finally:
        await orchestrator.cleanup()


@pytest.mark.asyncio
async def test_error_handling_and_recovery():
    """Test error handling and recovery mechanisms."""
    orchestrator = AgentOrchestrator()
    await orchestrator.setup()
    
    try:
        # Create a task that might fail
        task_request = TaskRequest(
            task_type="error_test",
            description="Task to test error handling",
            requirements=["invalid_requirement"]  # This might cause issues
        )
        
        # Submit task
        response = await orchestrator.submit_task(task_request)
        task_id = response.task_id
        
        # Wait for completion or failure
        max_wait_time = 15
        wait_interval = 0.5
        elapsed_time = 0
        
        while elapsed_time < max_wait_time:
            status = await orchestrator.get_task_status(task_id)
            if status.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                break
            await asyncio.sleep(wait_interval)
            elapsed_time += wait_interval
        
        # Check final status (might succeed or fail, both are valid outcomes)
        final_status = await orchestrator.get_task_status(task_id)
        assert final_status.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
        
        if final_status.status == TaskStatus.FAILED:
            assert final_status.error is not None
            print(f"Task failed as expected: {final_status.error}")
        
    finally:
        await orchestrator.cleanup()


if __name__ == "__main__":
    pytest.main([__file__])
