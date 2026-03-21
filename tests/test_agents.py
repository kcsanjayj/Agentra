"""
Tests for agent modules.

This module contains unit tests for all agent classes and their functionality.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

from app.agents.base import BaseAgent, AgentResponse
from app.agents.planner import PlannerAgent
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent
from app.agents.coder import CoderAgent
from app.agents.verifier import VerifierAgent


class TestBaseAgent:
    """Test cases for BaseAgent class."""
    
    def test_base_agent_initialization(self):
        """Test BaseAgent initialization."""
        agent = BaseAgent("test_agent", {"key": "value"})
        
        assert agent.name == "test_agent"
        assert agent.config == {"key": "value"}
        assert hasattr(agent, 'logger')
    
    def test_base_agent_get_required_fields(self):
        """Test BaseAgent get_required_fields method."""
        agent = BaseAgent("test_agent")
        required_fields = agent.get_required_fields()
        
        assert isinstance(required_fields, list)
        assert "type" in required_fields
        assert "description" in required_fields
    
    def test_base_agent_validate_task(self):
        """Test BaseAgent validate_task method."""
        agent = BaseAgent("test_agent")
        
        # Valid task
        valid_task = {"type": "test", "description": "test task"}
        assert agent.validate_task(valid_task) == True
        
        # Invalid task (missing required fields)
        invalid_task = {"type": "test"}
        assert agent.validate_task(invalid_task) == False
    
    @pytest.mark.asyncio
    async def test_base_agent_setup_cleanup(self):
        """Test BaseAgent setup and cleanup methods."""
        agent = BaseAgent("test_agent")
        
        # These should not raise exceptions
        await agent.setup()
        await agent.cleanup()
    
    def test_base_agent_str_representation(self):
        """Test BaseAgent string representation."""
        agent = BaseAgent("test_agent")
        str_repr = str(agent)
        
        assert "test_agent" in str_repr
        assert "BaseAgent" in str_repr


class TestPlannerAgent:
    """Test cases for PlannerAgent class."""
    
    def test_planner_agent_initialization(self):
        """Test PlannerAgent initialization."""
        agent = PlannerAgent()
        
        assert agent.name == "planner"
        assert hasattr(agent, 'planning_strategies')
        assert "sequential" in agent.planning_strategies
        assert "parallel" in agent.planning_strategies
        assert "hierarchical" in agent.planning_strategies
    
    def test_planner_agent_get_capabilities(self):
        """Test PlannerAgent get_capabilities method."""
        agent = PlannerAgent()
        capabilities = agent.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert "task_decomposition" in capabilities
        assert "sequential_planning" in capabilities
        assert "parallel_planning" in capabilities
    
    @pytest.mark.asyncio
    async def test_planner_agent_execute_success(self):
        """Test PlannerAgent successful execution."""
        agent = PlannerAgent()
        
        task = {
            "type": "planning",
            "description": "Create a plan for writing a blog post",
            "requirements": ["research", "writing", "review"],
            "strategy": "sequential"
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert "plan" in response.data
        assert "strategy" in response.data
        assert "estimated_steps" in response.data
        assert "complexity" in response.data
        assert response.data["strategy"] == "sequential"
    
    @pytest.mark.asyncio
    async def test_planner_agent_execute_invalid_task(self):
        """Test PlannerAgent execution with invalid task."""
        agent = PlannerAgent()
        
        # Invalid task (missing description)
        invalid_task = {"type": "planning"}
        response = await agent.execute(invalid_task)
        
        assert response.success == False
        assert "Invalid task format" in response.error
    
    @pytest.mark.asyncio
    async def test_planner_agent_parallel_planning(self):
        """Test PlannerAgent parallel planning strategy."""
        agent = PlannerAgent()
        
        task = {
            "type": "planning",
            "description": "Create a parallel execution plan",
            "strategy": "parallel"
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert response.data["strategy"] == "parallel"
        assert isinstance(response.data["plan"], list)
    
    @pytest.mark.asyncio
    async def test_planner_agent_hierarchical_planning(self):
        """Test PlannerAgent hierarchical planning strategy."""
        agent = PlannerAgent()
        
        task = {
            "type": "planning",
            "description": "Create a hierarchical execution plan",
            "strategy": "hierarchical"
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert response.data["strategy"] == "hierarchical"
        assert isinstance(response.data["plan"], list)


class TestResearcherAgent:
    """Test cases for ResearcherAgent class."""
    
    def test_researcher_agent_initialization(self):
        """Test ResearcherAgent initialization."""
        agent = ResearcherAgent()
        
        assert agent.name == "researcher"
        assert hasattr(agent, 'research_sources')
        assert "web_search" in agent.research_sources
        assert "document_analysis" in agent.research_sources
    
    def test_researcher_agent_get_capabilities(self):
        """Test ResearcherAgent get_capabilities method."""
        agent = ResearcherAgent()
        capabilities = agent.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert "web_research" in capabilities
        assert "document_analysis" in capabilities
        assert "information_synthesis" in capabilities
    
    @pytest.mark.asyncio
    async def test_researcher_agent_execute_success(self):
        """Test ResearcherAgent successful execution."""
        agent = ResearcherAgent()
        
        task = {
            "type": "research",
            "query": "artificial intelligence trends 2024",
            "sources": ["web_search"],
            "depth": "medium"
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert "findings" in response.data
        assert "analysis" in response.data
        assert "summary" in response.data
        assert "confidence_score" in response.data
    
    @pytest.mark.asyncio
    async def test_researcher_agent_execute_invalid_task(self):
        """Test ResearcherAgent execution with invalid task."""
        agent = ResearcherAgent()
        
        # Invalid task (missing query)
        invalid_task = {"type": "research"}
        response = await agent.execute(invalid_task)
        
        assert response.success == False
        assert "Invalid task format" in response.error
    
    @pytest.mark.asyncio
    async def test_researcher_agent_multiple_sources(self):
        """Test ResearcherAgent with multiple research sources."""
        agent = ResearcherAgent()
        
        task = {
            "type": "research",
            "query": "machine learning applications",
            "sources": ["web_search", "document_analysis", "data_extraction"],
            "depth": "high"
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        findings = response.data["findings"]
        assert len(findings) == 3  # Three sources
        
        # Check each source was processed
        source_names = [finding["source"] for finding in findings]
        assert "web_search" in source_names
        assert "document_analysis" in source_names
        assert "data_extraction" in source_names


class TestWriterAgent:
    """Test cases for WriterAgent class."""
    
    def test_writer_agent_initialization(self):
        """Test WriterAgent initialization."""
        agent = WriterAgent()
        
        assert agent.name == "writer"
        assert hasattr(agent, 'writing_styles')
        assert "formal" in agent.writing_styles
        assert "casual" in agent.writing_styles
        assert "technical" in agent.writing_styles
    
    def test_writer_agent_get_capabilities(self):
        """Test WriterAgent get_capabilities method."""
        agent = WriterAgent()
        capabilities = agent.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert "content_creation" in capabilities
        assert "document_writing" in capabilities
        assert "technical_writing" in capabilities
    
    @pytest.mark.asyncio
    async def test_writer_agent_execute_success(self):
        """Test WriterAgent successful execution."""
        agent = WriterAgent()
        
        task = {
            "type": "writing",
            "content_type": "blog_post",
            "topic": "The Future of Artificial Intelligence",
            "style": "formal",
            "length": "medium",
            "requirements": ["headings", "examples"]
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert "content" in response.data
        assert "word_count" in response.data
        assert "structure" in response.data
        assert response.data["content_type"] == "blog_post"
        assert response.data["style"] == "formal"
    
    @pytest.mark.asyncio
    async def test_writer_agent_execute_invalid_task(self):
        """Test WriterAgent execution with invalid task."""
        agent = WriterAgent()
        
        # Invalid task (missing topic)
        invalid_task = {"type": "writing", "content_type": "blog_post"}
        response = await agent.execute(invalid_task)
        
        assert response.success == False
        assert "Invalid task format" in response.error
    
    @pytest.mark.asyncio
    async def test_writer_agent_different_styles(self):
        """Test WriterAgent with different writing styles."""
        agent = WriterAgent()
        
        styles = ["formal", "casual", "technical", "creative"]
        
        for style in styles:
            task = {
                "type": "writing",
                "content_type": "article",
                "topic": f"Test topic for {style} style",
                "style": style
            }
            
            response = await agent.execute(task)
            
            assert response.success == True
            assert response.data["style"] == style
            assert len(response.data["content"]) > 0


class TestCoderAgent:
    """Test cases for CoderAgent class."""
    
    def test_coder_agent_initialization(self):
        """Test CoderAgent initialization."""
        agent = CoderAgent()
        
        assert agent.name == "coder"
        assert hasattr(agent, 'supported_languages')
        assert "python" in agent.supported_languages
        assert "javascript" in agent.supported_languages
        assert "java" in agent.supported_languages
    
    def test_coder_agent_get_capabilities(self):
        """Test CoderAgent get_capabilities method."""
        agent = CoderAgent()
        capabilities = agent.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert "code_generation" in capabilities
        assert "code_modification" in capabilities
        assert "debugging" in capabilities
    
    @pytest.mark.asyncio
    async def test_coder_agent_execute_generate_success(self):
        """Test CoderAgent successful code generation."""
        agent = CoderAgent()
        
        task = {
            "type": "coding",
            "language": "python",
            "task_type": "generate",
            "requirements": "Create a function that calculates factorial",
            "specifications": {"include_tests": True}
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert "code" in response.data
        assert "validation" in response.data
        assert "documentation" in response.data
        assert "test_cases" in response.data
        assert response.data["language"] == "python"
        assert response.data["task_type"] == "generate"
    
    @pytest.mark.asyncio
    async def test_coder_agent_execute_invalid_task(self):
        """Test CoderAgent execution with invalid task."""
        agent = CoderAgent()
        
        # Invalid task (missing language)
        invalid_task = {"type": "coding", "task_type": "generate"}
        response = await agent.execute(invalid_task)
        
        assert response.success == False
        assert "Invalid task format" in response.error
    
    @pytest.mark.asyncio
    async def test_coder_agent_different_languages(self):
        """Test CoderAgent with different programming languages."""
        agent = CoderAgent()
        
        languages = ["python", "javascript", "java", "cpp", "html", "css"]
        
        for language in languages:
            task = {
                "type": "coding",
                "language": language,
                "task_type": "generate",
                "requirements": f"Create a simple {language} program"
            }
            
            response = await agent.execute(task)
            
            assert response.success == True
            assert response.data["language"] == language
            assert len(response.data["code"]) > 0
    
    @pytest.mark.asyncio
    async def test_coder_agent_modify_task(self):
        """Test CoderAgent code modification task."""
        agent = CoderAgent()
        
        existing_code = "def hello():\n    print('Hello World')"
        
        task = {
            "type": "coding",
            "language": "python",
            "task_type": "modify",
            "requirements": "add comments and error handling",
            "existing_code": existing_code
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert response.data["task_type"] == "modify"
        assert len(response.data["code"]) > len(existing_code)


class TestVerifierAgent:
    """Test cases for VerifierAgent class."""
    
    def test_verifier_agent_initialization(self):
        """Test VerifierAgent initialization."""
        agent = VerifierAgent()
        
        assert agent.name == "verifier"
        assert hasattr(agent, 'verification_types')
        assert "content" in agent.verification_types
        assert "code" in agent.verification_types
        assert "data" in agent.verification_types
    
    def test_verifier_agent_get_capabilities(self):
        """Test VerifierAgent get_capabilities method."""
        agent = VerifierAgent()
        capabilities = agent.get_capabilities()
        
        assert isinstance(capabilities, list)
        assert "content_verification" in capabilities
        assert "code_verification" in capabilities
        assert "quality_assurance" in capabilities
    
    @pytest.mark.asyncio
    async def test_verifier_agent_execute_content_success(self):
        """Test VerifierAgent successful content verification."""
        agent = VerifierAgent()
        
        task = {
            "type": "verification",
            "verification_type": "content",
            "content": "This is a well-written article about artificial intelligence with proper structure and grammar.",
            "requirements": ["grammar", "structure"],
            "criteria": {"min_length": 50, "required_sections": ["introduction", "conclusion"]}
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert "verification_result" in response.data
        assert "overall_score" in response.data
        assert "report" in response.data
        assert "recommendations" in response.data
        assert "passed" in response.data
    
    @pytest.mark.asyncio
    async def test_verifier_agent_execute_invalid_task(self):
        """Test VerifierAgent execution with invalid task."""
        agent = VerifierAgent()
        
        # Invalid task (missing verification_type)
        invalid_task = {"type": "verification", "content": "test"}
        response = await agent.execute(invalid_task)
        
        assert response.success == False
        assert "Invalid task format" in response.error
    
    @pytest.mark.asyncio
    async def test_verifier_agent_code_verification(self):
        """Test VerifierAgent code verification."""
        agent = VerifierAgent()
        
        code = """
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

# Test the function
print(factorial(5))
"""
        
        task = {
            "type": "verification",
            "verification_type": "code",
            "content": code,
            "requirements": ["comments", "error_handling"],
            "criteria": {"min_length": 10}
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert response.data["verification_type"] == "code"
        verification_result = response.data["verification_result"]
        assert "checks" in verification_result
        assert "passed_checks" in verification_result
        assert "total_checks" in verification_result
    
    @pytest.mark.asyncio
    async def test_verifier_agent_data_verification(self):
        """Test VerifierAgent data verification."""
        agent = VerifierAgent()
        
        data = {
            "name": "John Doe",
            "age": 30,
            "email": "john@example.com"
        }
        
        task = {
            "type": "verification",
            "verification_type": "data",
            "content": data,
            "criteria": {
                "required_keys": ["name", "age", "email"],
                "expected_types": {"age": "int"}
            }
        }
        
        response = await agent.execute(task)
        
        assert response.success == True
        assert response.data["verification_type"] == "data"
        verification_result = response.data["verification_result"]
        assert "checks" in verification_result


# Integration Tests
@pytest.mark.asyncio
async def test_agent_workflow_integration():
    """Test integration between multiple agents."""
    # Initialize agents
    planner = PlannerAgent()
    researcher = ResearcherAgent()
    writer = WriterAgent()
    verifier = VerifierAgent()
    
    # Step 1: Create plan
    plan_task = {
        "type": "planning",
        "description": "Create a blog post about renewable energy",
        "requirements": ["research", "writing", "review"]
    }
    
    plan_response = await planner.execute(plan_task)
    assert plan_response.success == True
    
    # Step 2: Research
    research_task = {
        "type": "research",
        "query": "renewable energy trends and benefits",
        "sources": ["web_search"]
    }
    
    research_response = await researcher.execute(research_task)
    assert research_response.success == True
    
    # Step 3: Write content
    write_task = {
        "type": "writing",
        "content_type": "blog_post",
        "topic": "The Future of Renewable Energy",
        "style": "formal",
        "research_data": research_response.data
    }
    
    write_response = await writer.execute(write_task)
    assert write_response.success == True
    
    # Step 4: Verify content
    verify_task = {
        "type": "verification",
        "verification_type": "content",
        "content": write_response.data["content"],
        "requirements": ["grammar", "structure"],
        "criteria": {"min_length": 100}
    }
    
    verify_response = await verifier.execute(verify_task)
    assert verify_response.success == True
    
    # Verify the workflow completed successfully
    assert verify_response.data["passed"] == True
    assert verify_response.data["overall_score"] >= 0.7


# Performance Tests
@pytest.mark.asyncio
async def test_agent_performance():
    """Test agent performance with concurrent execution."""
    agents = [
        PlannerAgent(),
        ResearcherAgent(),
        WriterAgent(),
        CoderAgent(),
        VerifierAgent()
    ]
    
    # Create tasks for each agent
    tasks = []
    for i, agent in enumerate(agents):
        if agent.name == "planner":
            task = {
                "type": "planning",
                "description": f"Test plan {i}",
                "requirements": []
            }
        elif agent.name == "researcher":
            task = {
                "type": "research",
                "query": f"Test query {i}",
                "sources": ["web_search"]
            }
        elif agent.name == "writer":
            task = {
                "type": "writing",
                "content_type": "article",
                "topic": f"Test topic {i}",
                "style": "formal"
            }
        elif agent.name == "coder":
            task = {
                "type": "coding",
                "language": "python",
                "task_type": "generate",
                "requirements": f"Simple function {i}"
            }
        elif agent.name == "verifier":
            task = {
                "type": "verification",
                "verification_type": "content",
                "content": f"Test content {i}",
                "criteria": {}
            }
        
        tasks.append((agent, task))
    
    # Execute all tasks concurrently
    start_time = asyncio.get_event_loop().time()
    
    async def execute_agent_task(agent_task):
        agent, task = agent_task
        return await agent.execute(task)
    
    results = await asyncio.gather(
        *[execute_agent_task(agent_task) for agent_task in tasks],
        return_exceptions=True
    )
    
    end_time = asyncio.get_event_loop().time()
    execution_time = end_time - start_time
    
    # Verify all tasks completed successfully
    successful_results = [r for r in results if not isinstance(r, Exception) and r.success]
    assert len(successful_results) == len(agents)
    
    # Performance should be reasonable (less than 10 seconds for all agents)
    assert execution_time < 10.0
    
    print(f"Executed {len(agents)} agents concurrently in {execution_time:.2f} seconds")


if __name__ == "__main__":
    pytest.main([__file__])
