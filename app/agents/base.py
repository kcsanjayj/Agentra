"""
Base agent class for the Autonomous Multi-Agent Executor.

This module defines the abstract base class that all agents should inherit from.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

class AgentResponse(BaseModel):
    """Response model for agent actions."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the agent."""
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"agent.{name}")
        
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute a task.
        
        Args:
            task: Dictionary containing task details and parameters
            
        Returns:
            AgentResponse containing the execution result
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this agent provides.
        
        Returns:
            List of capability names
        """
        pass
    
    def validate_task(self, task: Dict[str, Any]) -> bool:
        """
        Validate if the task can be handled by this agent.
        
        Args:
            task: Task to validate
            
        Returns:
            True if task is valid for this agent, False otherwise
        """
        required_fields = self.get_required_fields()
        return all(field in task for field in required_fields)
    
    def get_required_fields(self) -> List[str]:
        """
        Get the list of required fields for tasks.
        
        Returns:
            List of required field names
        """
        return ["type", "description"]
    
    async def setup(self) -> None:
        """Setup the agent (called before first execution)."""
        self.logger.info(f"Setting up agent: {self.name}")
    
    async def cleanup(self) -> None:
        """Cleanup the agent (called when shutting down)."""
        self.logger.info(f"Cleaning up agent: {self.name}")
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}')"
    
    def __repr__(self) -> str:
        return self.__str__()
