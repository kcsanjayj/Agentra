"""
Pydantic models and schemas for the Autonomous Multi-Agent Executor.

This module contains all the data models used throughout the application,
including request/response models, database schemas, and internal data structures.
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import uuid

class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(str, Enum):
    """Task priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class ExecutionStrategy(str, Enum):
    """Task execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"

class AgentType(str, Enum):
    """Available agent types."""
    PLANNER = "planner"
    RESEARCHER = "researcher"
    WRITER = "writer"
    CODER = "coder"
    VERIFIER = "verifier"

# Request Models
class TaskRequest(BaseModel):
    """Request model for submitting a new task."""
    task_type: str = Field(..., description="Type of task to execute")
    description: str = Field(..., description="Detailed description of the task")
    requirements: List[str] = Field(default_factory=list, description="List of requirements")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Task priority")
    execution_strategy: ExecutionStrategy = Field(default=ExecutionStrategy.SEQUENTIAL, description="Execution strategy")
    acceptance_criteria: Dict[str, Any] = Field(default_factory=dict, description="Acceptance criteria")
    include_verification: bool = Field(default=True, description="Whether to include verification step")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('description')
    def description_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    class Config:
        use_enum_values = True

class AgentTaskRequest(BaseModel):
    """Request model for agent-specific tasks."""
    agent_type: AgentType = Field(..., description="Type of agent to execute the task")
    task_data: Dict[str, Any] = Field(..., description="Task-specific data")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Context from previous steps")
    timeout: Optional[int] = Field(default=300, description="Timeout in seconds")

# Response Models
class TaskResponse(BaseModel):
    """Response model for task status and results."""
    task_id: str = Field(..., description="Unique task identifier")
    status: TaskStatus = Field(..., description="Current task status")
    message: str = Field(default="", description="Status message")
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    execution_plan: Optional['ExecutionPlan'] = Field(default=None, description="Execution plan details")
    results: Optional[Dict[str, Any]] = Field(default=None, description="Task execution results")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    
    class Config:
        use_enum_values = True

class AgentResponse(BaseModel):
    """Response model for agent execution results."""
    agent_type: AgentType = Field(..., description="Type of agent that executed the task")
    success: bool = Field(..., description="Whether the agent execution was successful")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Agent execution data")
    error: Optional[str] = Field(default=None, description="Error message if execution failed")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    execution_time: Optional[float] = Field(default=None, description="Execution time in seconds")
    
    class Config:
        use_enum_values = True

# Execution Plan Models
class ExecutionStep(BaseModel):
    """Single step in an execution plan."""
    id: str = Field(..., description="Step identifier")
    agent: AgentType = Field(..., description="Agent type to execute this step")
    task: str = Field(..., description="Task description for this step")
    dependencies: List[str] = Field(default_factory=list, description="List of step dependencies")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Step status")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Step execution result")
    error: Optional[str] = Field(default=None, description="Error message if step failed")
    started_at: Optional[datetime] = Field(default=None, description="Step start time")
    completed_at: Optional[datetime] = Field(default=None, description="Step completion time")
    
    class Config:
        use_enum_values = True

class ExecutionPlan(BaseModel):
    """Execution plan for a task."""
    task_id: str = Field(..., description="Associated task ID")
    steps: List[ExecutionStep] = Field(..., description="List of execution steps")
    strategy: ExecutionStrategy = Field(..., description="Execution strategy")
    estimated_complexity: str = Field(..., description="Estimated complexity level")
    created_at: datetime = Field(..., description="Plan creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    
    @validator('steps')
    def steps_must_have_valid_dependencies(cls, v, values):
        step_ids = {step.id for step in v}
        for step in v:
            for dep in step.dependencies:
                if dep not in step_ids:
                    raise ValueError(f"Step '{step.id}' has invalid dependency '{dep}'")
        return v
    
    class Config:
        use_enum_values = True

# Agent Models
class AgentCapability(BaseModel):
    """Agent capability description."""
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    supported_tasks: List[str] = Field(default_factory=list, description="List of supported task types")
    required_fields: List[str] = Field(default_factory=list, description="Required input fields")

class AgentInfo(BaseModel):
    """Agent information and status."""
    name: str = Field(..., description="Agent name")
    type: AgentType = Field(..., description="Agent type")
    status: str = Field(..., description="Current agent status")
    capabilities: List[AgentCapability] = Field(default_factory=list, description="Agent capabilities")
    config: Dict[str, Any] = Field(default_factory=dict, description="Agent configuration")
    last_activity: Optional[datetime] = Field(default=None, description="Last activity timestamp")
    
    class Config:
        use_enum_values = True

# System Models
class SystemStatus(BaseModel):
    """System status information."""
    total_agents: int = Field(..., description="Total number of agents")
    active_agents: int = Field(..., description="Number of active agents")
    running_tasks: int = Field(..., description="Number of currently running tasks")
    queued_tasks: int = Field(..., description="Number of queued tasks")
    completed_tasks: int = Field(..., description="Number of completed tasks")
    failed_tasks: int = Field(..., description="Number of failed tasks")
    system_uptime: float = Field(..., description="System uptime in seconds")
    memory_usage: Optional[float] = Field(default=None, description="Memory usage percentage")
    cpu_usage: Optional[float] = Field(default=None, description="CPU usage percentage")

class HealthCheck(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Health status")
    timestamp: datetime = Field(default_factory=datetime.now, description="Check timestamp")
    version: str = Field(..., description="Application version")
    components: Dict[str, str] = Field(default_factory=dict, description="Component status")
    uptime: float = Field(..., description="System uptime in seconds")

# Configuration Models
class AgentConfig(BaseModel):
    """Agent configuration."""
    agent_type: AgentType = Field(..., description="Agent type")
    enabled: bool = Field(default=True, description="Whether the agent is enabled")
    max_concurrent_tasks: int = Field(default=1, description="Maximum concurrent tasks")
    timeout: int = Field(default=300, description="Default timeout in seconds")
    retry_attempts: int = Field(default=3, description="Number of retry attempts")
    custom_settings: Dict[str, Any] = Field(default_factory=dict, description="Custom settings")
    
    class Config:
        use_enum_values = True

class SystemConfig(BaseModel):
    """System configuration."""
    max_concurrent_tasks: int = Field(default=10, description="Maximum concurrent tasks")
    default_timeout: int = Field(default=300, description="Default timeout in seconds")
    task_retention_days: int = Field(default=30, description="Task retention period in days")
    log_level: str = Field(default="INFO", description="Logging level")
    enable_metrics: bool = Field(default=True, description="Whether to enable metrics collection")
    agents: List[AgentConfig] = Field(default_factory=list, description="Agent configurations")
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level. Must be one of: {valid_levels}')
        return v.upper()

# Database Models (for future database integration)
class TaskRecord(BaseModel):
    """Database record for a task."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    task_id: str = Field(..., description="Task identifier")
    task_type: str = Field(..., description="Task type")
    description: str = Field(..., description="Task description")
    status: TaskStatus = Field(..., description="Task status")
    priority: TaskPriority = Field(..., description="Task priority")
    execution_plan: Optional[Dict[str, Any]] = Field(default=None, description="Execution plan")
    results: Optional[Dict[str, Any]] = Field(default=None, description="Task results")
    error: Optional[str] = Field(default=None, description="Error message")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Update timestamp")
    completed_at: Optional[datetime] = Field(default=None, description="Completion timestamp")
    
    class Config:
        use_enum_values = True

class AgentExecutionRecord(BaseModel):
    """Database record for agent execution."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique identifier")
    task_id: str = Field(..., description="Associated task ID")
    agent_type: AgentType = Field(..., description="Agent type")
    step_id: str = Field(..., description="Execution step ID")
    task_data: Dict[str, Any] = Field(..., description="Task data provided to agent")
    result: Optional[Dict[str, Any]] = Field(default=None, description="Execution result")
    success: bool = Field(..., description="Whether execution was successful")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: float = Field(..., description="Execution time in seconds")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    class Config:
        use_enum_values = True

# Utility Models
class PaginationParams(BaseModel):
    """Pagination parameters."""
    page: int = Field(default=1, ge=1, description="Page number")
    size: int = Field(default=20, ge=1, le=100, description="Page size")
    
    @property
    def offset(self) -> int:
        """Calculate offset from page and size."""
        return (self.page - 1) * self.size

class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any] = Field(..., description="List of items")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    size: int = Field(..., description="Page size")
    pages: int = Field(..., description="Total number of pages")

class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    timestamp: datetime = Field(default_factory=datetime.now, description="Error timestamp")

# Forward references for circular imports
TaskResponse.update_forward_refs()
ExecutionPlan.update_forward_refs()
