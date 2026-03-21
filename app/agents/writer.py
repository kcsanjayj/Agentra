"""
Writer agent for content creation and document generation.
"""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentResponse
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class WriterAgent(BaseAgent):
    """Agent responsible for writing and content creation."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("writer", config)
        self.writing_styles = {
            "formal": self._formal_writing,
            "casual": self._casual_writing,
            "technical": self._technical_writing,
            "creative": self._creative_writing
        }
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute writing task to create content.
        
        Args:
            task: Dictionary containing writing requirements and content
            
        Returns:
            AgentResponse with generated content
        """
        try:
            if not self.validate_task(task):
                return AgentResponse(
                    success=False,
                    error="Invalid task format for writer agent"
                )
            
            content_type = task.get("content_type", "general")
            topic = task.get("topic", "")
            style = task.get("style", "formal")
            length = task.get("length", "medium")
            research_data = task.get("research_data", {})
            requirements = task.get("requirements", [])
            
            self.logger.info(f"Writing {content_type} content about: {topic[:100]}...")
            
            # Choose writing style
            writing_func = self.writing_styles.get(style, self._formal_writing)
            
            # Generate content
            content = await writing_func(topic, research_data, length, requirements)
            
            # Format and structure content
            formatted_content = await self._format_content(content, content_type)
            
            # Review and refine
            refined_content = await self._refine_content(formatted_content, requirements)
            
            return AgentResponse(
                success=True,
                data={
                    "content": refined_content,
                    "content_type": content_type,
                    "topic": topic,
                    "style": style,
                    "word_count": len(refined_content.split()),
                    "structure": self._analyze_structure(refined_content)
                },
                metadata={
                    "writing_style": style,
                    "length_target": length,
                    "requirements_met": self._check_requirements(refined_content, requirements)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in writer agent: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Writing failed: {str(e)}"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return list of writer capabilities."""
        return [
            "content_creation",
            "document_writing",
            "technical_writing",
            "creative_writing",
            "content_formatting",
            "proofreading"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for writing tasks."""
        return ["topic", "content_type"]
    
    async def _formal_writing(self, topic: str, research_data: Dict[str, Any], length: str, requirements: List[str]) -> str:
        """Generate formal content."""
        await asyncio.sleep(1)
        
        content = f"""
# {topic.title()}

## Introduction
This document provides a comprehensive analysis of {topic}. Based on current research and best practices, we explore the key aspects and implications.

## Main Content
{topic} represents an important area of consideration. The research findings indicate several critical factors that must be addressed:

1. First, we examine the fundamental principles underlying {topic}.
2. Second, we analyze the practical applications and implementations.
3. Third, we consider future developments and potential improvements.

## Conclusion
In summary, {topic} requires careful consideration and strategic planning. The recommendations outlined in this document provide a foundation for successful implementation.
"""
        return content.strip()
    
    async def _casual_writing(self, topic: str, research_data: Dict[str, Any], length: str, requirements: List[str]) -> str:
        """Generate casual content."""
        await asyncio.sleep(0.8)
        
        content = f"""
# Let's Talk About {topic}

Hey there! Today we're diving into {topic} - something pretty interesting that you should know about.

## What's the Deal?
So, {topic} is actually pretty cool when you think about it. Here's what I've found:

- It's super relevant right now
- Lots of people are talking about it
- There are some neat things you can do with it

## My Take
Honestly, I think {topic} is worth paying attention to. Whether you're just curious or seriously looking into it, there's something here for everyone.

## What's Next?
Keep an eye on {topic} - I have a feeling we'll be hearing more about it soon!
"""
        return content.strip()
    
    async def _technical_writing(self, topic: str, research_data: Dict[str, Any], length: str, requirements: List[str]) -> str:
        """Generate technical content."""
        await asyncio.sleep(1.2)
        
        content = f"""
# Technical Specification: {topic}

## Overview
This document outlines the technical specifications and implementation details for {topic}.

## Architecture
The system architecture for {topic} consists of the following components:

### Core Components
- **Module A**: Primary processing unit
- **Module B**: Data management layer
- **Module C**: Interface controller

### Data Flow
```
Input → Processing → Validation → Output
```

## Implementation
```python
# Example implementation for {topic}
class {topic.replace(' ', '')}System:
    def __init__(self):
        self.config = {{}}
    
    def process(self, data):
        # Processing logic here
        return processed_data
```

## Performance Metrics
- Response time: <100ms
- Throughput: 1000 req/sec
- Memory usage: <512MB

## Conclusion
The technical implementation of {topic} provides robust performance and scalability.
"""
        return content.strip()
    
    async def _creative_writing(self, topic: str, research_data: Dict[str, Any], length: str, requirements: List[str]) -> str:
        """Generate creative content."""
        await asyncio.sleep(0.9)
        
        content = f"""
# The Story of {topic}

Once upon a time, in a world not so different from ours, {topic} emerged as a beacon of innovation and possibility.

## Chapter 1: The Beginning
It started with a simple idea - what if {topic} could change everything? The seeds of this revolution were planted in the most unexpected places.

## Chapter 2: The Journey
As {topic} began to grow, it faced challenges and triumphs. Each obstacle overcome made it stronger, each victory more meaningful.

## Chapter 3: The Transformation
Through perseverance and creativity, {topic} transformed from a mere concept into a powerful force that reshaped the landscape around it.

## Epilogue
And so the story continues, with {topic} writing new chapters every day, inspiring others to dream bigger and reach further.
"""
        return content.strip()
    
    async def _format_content(self, content: str, content_type: str) -> str:
        """Format content based on type."""
        if content_type == "blog_post":
            return self._format_blog_post(content)
        elif content_type == "report":
            return self._format_report(content)
        elif content_type == "documentation":
            return self._format_documentation(content)
        else:
            return content
    
    def _format_blog_post(self, content: str) -> str:
        """Format as blog post."""
        return f"""{content}

---
*This article was generated by an AI writing assistant. Please review and edit as needed.*"""
    
    def _format_report(self, content: str) -> str:
        """Format as formal report."""
        return f"""{content}

---
**Report Generated:** {datetime.now().isoformat()}
**Status:** Draft
**Review Required:** Yes"""
    
    def _format_documentation(self, content: str) -> str:
        """Format as technical documentation."""
        return f"""{content}

---
**Documentation Version:** 1.0
**Last Updated:** {datetime.now().isoformat()}"""
    
    async def _refine_content(self, content: str, requirements: List[str]) -> str:
        """Refine content based on requirements."""
        # In a real implementation, this would use an LLM for refinement
        refined = content
        
        # Basic refinement checks
        if "concise" in requirements:
            refined = self._make_concise(refined)
        if "detailed" in requirements:
            refined = self._add_details(refined)
        if "examples" in requirements:
            refined = self._add_examples(refined)
        
        return refined
    
    def _make_concise(self, content: str) -> str:
        """Make content more concise."""
        # Simple implementation - remove redundant phrases
        return content.replace("In order to", "To").replace("due to the fact that", "because")
    
    def _add_details(self, content: str) -> str:
        """Add more details to content."""
        # Simple implementation - add elaboration
        return content.replace("important", "critically important").replace("good", "excellent")
    
    def _add_examples(self, content: str) -> str:
        """Add examples to content."""
        # Simple implementation - add example sections
        if "##" in content and "Example:" not in content:
            content += "\n\n## Example\nHere's a practical example to illustrate this concept."
        return content
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze the structure of the content."""
        lines = content.split('\n')
        headings = [line for line in lines if line.startswith('#')]
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        
        return {
            "headings": len(headings),
            "paragraphs": len(paragraphs),
            "has_introduction": any("intro" in p.lower() for p in paragraphs[:3]),
            "has_conclusion": any("conclusion" in p.lower() for p in paragraphs[-3:]),
            "estimated_reading_time": len(content.split()) // 200  # words per minute
        }
    
    def _check_requirements(self, content: str, requirements: List[str]) -> List[str]:
        """Check which requirements were met."""
        met = []
        
        for req in requirements:
            if req == "concise" and len(content) < 1000:
                met.append(req)
            elif req == "detailed" and len(content) > 500:
                met.append(req)
            elif req == "examples" and "example" in content.lower():
                met.append(req)
            elif req == "headings" and "#" in content:
                met.append(req)
        
        return met

    # ============== 9.5+ QUALITY UPGRADES ==============
    
    def write_final(self, answer: str, query: str) -> str:
        """CONTROL CENTER: Final quality gate before output"""
        import google.generativeai as genai
        import os
        
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDcCisYIl4R9MVdLR2RiU6fg4By9yBgdPg"
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        
        model = genai.GenerativeModel(model_name="models/gemini-flash-latest")
        
        prompt = f"""You are a precise output formatter. Improve this answer to meet STRICT quality standards.

STANDARDS:
- Fully relevant to the query (no tangents)
- Well-structured (clear flow)
- Concise (no filler words)
- No generic phrases like "some problems", "various topics", "etc"
- No incomplete sentences or truncation (never end with "...")
- Direct answer comes first
- Use specific examples and numbers

QUERY: {query}

CURRENT ANSWER: {answer}

IMPROVED ANSWER:"""

        try:
            response = model.generate_content(prompt)
            improved = response.text if response.text else answer
            return improved.strip()
        except Exception as e:
            logger.error(f"Writer refinement error: {e}")
            return answer
    
    def refine(self, answer: str, query: str, issues: list) -> str:
        """Targeted refinement based on specific issues"""
        import google.generativeai as genai
        import os
        
        GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyDcCisYIl4R9MVdLR2RiU6fg4By9yBgdPg"
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
        
        model = genai.GenerativeModel(model_name="models/gemini-flash-latest")
        
        issues_text = "\n".join([f"- {issue}" for issue in issues])
        
        prompt = f"""Fix these specific issues in the answer:

QUERY: {query}

CURRENT ANSWER: {answer}

ISSUES TO FIX:
{issues_text}

RULES:
- Address each issue directly
- Keep the good parts
- Be concise
- No new issues

FIXED ANSWER:"""

        try:
            response = model.generate_content(prompt)
            fixed = response.text if response.text else answer
            return fixed.strip()
        except Exception as e:
            logger.error(f"Writer refinement error: {e}")
            return answer

# Singleton instance for easy import
writer = WriterAgent()
