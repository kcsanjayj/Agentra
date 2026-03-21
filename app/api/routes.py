"""
API routes for the Autonomous Multi-Agent Executor.

This module contains all REST API endpoints for interacting with the multi-agent system.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.models.schemas import (
    TaskRequest, TaskResponse, AgentResponse, ExecutionPlan,
    TaskStatus, TaskPriority, ExecutionStrategy, AgentType,
    SystemStatus, HealthCheck, PaginationParams, PaginatedResponse,
    ErrorResponse
)
from app.executor.orchestrator import AgentOrchestrator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global orchestrator instance (will be initialized in main.py)
orchestrator: Optional[AgentOrchestrator] = None

def get_orchestrator() -> AgentOrchestrator:
    """Dependency to get the orchestrator instance."""
    global orchestrator
    if orchestrator is None:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")
    return orchestrator

# Task Management Endpoints
@router.post("/tasks", response_model=TaskResponse, status_code=201)
async def submit_task(
    task_request: TaskRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> TaskResponse:
    """
    Submit a new task for execution.
    
    Args:
        task_request: Task details and requirements
        orchestrator: Agent orchestrator instance
        
    Returns:
        TaskResponse with task ID and initial status
    """
    try:
        logger.info(f"Submitting task: {task_request.task_type}")
        response = await orchestrator.submit_task(task_request)
        return response
    except Exception as e:
        logger.error(f"Failed to submit task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> TaskResponse:
    """
    Get the current status of a task.
    
    Args:
        task_id: Unique task identifier
        orchestrator: Agent orchestrator instance
        
    Returns:
        TaskResponse with current status and results
    """
    try:
        response = await orchestrator.get_task_status(task_id)
        if response is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}", status_code=200)
async def cancel_task(
    task_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Cancel a running or queued task.
    
    Args:
        task_id: Unique task identifier
        orchestrator: Agent orchestrator instance
        
    Returns:
        Cancellation result
    """
    try:
        success = await orchestrator.cancel_task(task_id)
        if not success:
            raise HTTPException(status_code=404, detail="Task not found or cannot be cancelled")
        return {"message": "Task cancelled successfully", "task_id": task_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks", response_model=PaginatedResponse)
async def list_tasks(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status"),
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> PaginatedResponse:
    """
    List tasks with pagination and filtering.
    
    Args:
        page: Page number
        size: Page size
        status: Optional status filter
        orchestrator: Agent orchestrator instance
        
    Returns:
        Paginated list of tasks
    """
    try:
        # Get all tasks from orchestrator
        all_tasks = list(orchestrator.active_tasks.values())
        
        # Apply status filter if provided
        if status:
            all_tasks = [task for task in all_tasks if task["status"] == status]
        
        # Sort by creation time (newest first)
        all_tasks.sort(key=lambda t: t["created_at"], reverse=True)
        
        # Calculate pagination
        total = len(all_tasks)
        offset = (page - 1) * size
        paginated_tasks = all_tasks[offset:offset + size]
        pages = (total + size - 1) // size
        
        # Convert to TaskResponse models
        task_responses = []
        for task in paginated_tasks:
            task_response = TaskResponse(
                task_id=task["id"],
                status=task["status"],
                message=orchestrator._get_status_message(task),
                created_at=task["created_at"],
                updated_at=task["updated_at"],
                execution_plan=task["execution_plan"],
                results=task["results"]
            )
            task_responses.append(task_response)
        
        return PaginatedResponse(
            items=task_responses,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        logger.error(f"Failed to list tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Agent Management Endpoints
@router.get("/agents", response_model=List[Dict[str, Any]])
async def list_agents(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> List[Dict[str, Any]]:
    """
    List all available agents and their capabilities.
    
    Args:
        orchestrator: Agent orchestrator instance
        
    Returns:
        List of agent information
    """
    try:
        agents_info = []
        for agent_name, agent in orchestrator.agents.items():
            agent_info = {
                "name": agent_name,
                "type": agent_name,
                "capabilities": agent.get_capabilities(),
                "status": "active"
            }
            agents_info.append(agent_info)
        
        return agents_info
        
    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/agents/{agent_type}", response_model=Dict[str, Any])
async def get_agent_info(
    agent_type: AgentType,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Get detailed information about a specific agent.
    
    Args:
        agent_type: Type of agent
        orchestrator: Agent orchestrator instance
        
    Returns:
        Agent information and capabilities
    """
    try:
        agent = orchestrator.agents.get(agent_type.value)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "name": agent.name,
            "type": agent_type.value,
            "capabilities": agent.get_capabilities(),
            "required_fields": agent.get_required_fields(),
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get agent info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# System Status Endpoints
@router.get("/system/status", response_model=SystemStatus)
async def get_system_status(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> SystemStatus:
    """
    Get system status and statistics.
    
    Args:
        orchestrator: Agent orchestrator instance
        
    Returns:
        System status information
    """
    try:
        status_info = orchestrator.get_agent_status()
        
        return SystemStatus(
            total_agents=status_info["total_agents"],
            active_agents=status_info["total_agents"],  # All agents are active in this simple implementation
            running_tasks=status_info["active_tasks"],
            queued_tasks=status_info["queued_tasks"],
            completed_tasks=status_info["completed_tasks"],
            failed_tasks=0,  # Could be tracked separately
            system_uptime=0.0,  # Could be tracked from start time
            memory_usage=None,  # Could be implemented with psutil
            cpu_usage=None  # Could be implemented with psutil
        )
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health", response_model=HealthCheck)
async def health_check(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> HealthCheck:
    """
    Perform a health check on the system.
    
    Args:
        orchestrator: Agent orchestrator instance
        
    Returns:
        Health check result
    """
    try:
        # Check orchestrator status
        orchestrator_status = "healthy" if orchestrator.agents else "unhealthy"
        
        # Check individual agents
        component_status = {}
        for agent_name, agent in orchestrator.agents.items():
            component_status[agent_name] = "healthy"
        
        overall_status = "healthy" if all(status == "healthy" for status in component_status.values()) else "degraded"
        
        return HealthCheck(
            status=overall_status,
            timestamp=datetime.now(),
            version="0.1.0",
            components=component_status,
            uptime=0.0  # Could be tracked from start time
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheck(
            status="unhealthy",
            timestamp=datetime.now(),
            version="0.1.0",
            components={"orchestrator": "unhealthy"},
            uptime=0.0
        )

# Utility Endpoints
@router.post("/agents/{agent_type}/execute", response_model=AgentResponse)
async def execute_agent_task(
    agent_type: AgentType,
    task_data: Dict[str, Any],
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> AgentResponse:
    """
    Execute a task directly on a specific agent.
    
    Args:
        agent_type: Type of agent to execute the task
        task_data: Task-specific data
        orchestrator: Agent orchestrator instance
        
    Returns:
        Agent execution result
    """
    try:
        agent = orchestrator.agents.get(agent_type.value)
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        # Prepare task for agent
        agent_task = {
            "type": agent_type.value,
            **task_data
        }
        
        # Execute task
        import time
        start_time = time.time()
        response = await agent.execute(agent_task)
        execution_time = time.time() - start_time
        
        return AgentResponse(
            agent_type=agent_type,
            success=response.success,
            data=response.data,
            error=response.error,
            metadata=response.metadata,
            execution_time=execution_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to execute agent task: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system/config", response_model=Dict[str, Any])
async def get_system_config(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Get system configuration.
    
    Args:
        orchestrator: Agent orchestrator instance
        
    Returns:
        System configuration
    """
    try:
        return {
            "max_concurrent_tasks": orchestrator.max_concurrent_tasks,
            "available_agents": list(orchestrator.agents.keys()),
            "supported_strategies": [strategy.value for strategy in ExecutionStrategy],
            "supported_priorities": [priority.value for priority in TaskPriority],
            "version": "0.1.0"
        }
        
    except Exception as e:
        logger.error(f"Failed to get system config: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error Handlers
@router.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            code=f"HTTP_{exc.status_code}",
            timestamp=datetime.now()
        ).dict()
    )

@router.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            code="INTERNAL_ERROR",
            details={"original_error": str(exc)},
            timestamp=datetime.now()
        ).dict()
    )
