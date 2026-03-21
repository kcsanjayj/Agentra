"""
API module for the Autonomous Multi-Agent Executor.

This package contains REST API endpoints and routes for interacting
with the multi-agent system.
"""

from .routes import router

__all__ = ["router"]
