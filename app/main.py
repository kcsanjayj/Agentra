"""
Main application entry point for the Autonomous Multi-Agent Executor.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import router
from app.executor.orchestrator import AgentOrchestrator
import uvicorn

app = FastAPI(
    title="Autonomous Multi-Agent Executor",
    description="A framework for orchestrating multiple AI agents",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Initialize orchestrator
orchestrator = AgentOrchestrator()

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    await orchestrator.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown."""
    await orchestrator.cleanup()

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Autonomous Multi-Agent Executor API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
