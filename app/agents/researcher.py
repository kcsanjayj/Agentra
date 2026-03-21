"""
Researcher agent for gathering information and conducting research.
"""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentResponse
import logging
import asyncio

logger = logging.getLogger(__name__)

class ResearcherAgent(BaseAgent):
    """Agent responsible for research and information gathering."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("researcher", config)
        self.research_sources = [
            "web_search",
            "document_analysis", 
            "data_extraction",
            "fact_checking"
        ]
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute research task to gather information.
        
        Args:
            task: Dictionary containing research query and requirements
            
        Returns:
            AgentResponse with research findings
        """
        try:
            if not self.validate_task(task):
                return AgentResponse(
                    success=False,
                    error="Invalid task format for researcher agent"
                )
            
            query = task.get("query", "")
            research_type = task.get("type", "general")
            sources = task.get("sources", ["web_search"])
            depth = task.get("depth", "medium")
            
            self.logger.info(f"Researching: {query[:100]}...")
            
            # Gather information from specified sources
            findings = await self._gather_information(query, sources, depth)
            
            # Analyze and synthesize findings
            analysis = await self._analyze_findings(findings, research_type)
            
            # Generate summary
            summary = await self._generate_summary(analysis)
            
            return AgentResponse(
                success=True,
                data={
                    "query": query,
                    "findings": findings,
                    "analysis": analysis,
                    "summary": summary,
                    "sources_used": sources,
                    "confidence_score": self._calculate_confidence(findings)
                },
                metadata={
                    "research_type": research_type,
                    "depth": depth,
                    "processing_time": "N/A"
                }
            )
            
        except Exception as e:
            logger.error(f"Error in researcher agent: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Research failed: {str(e)}"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return list of researcher capabilities."""
        return [
            "web_research",
            "document_analysis",
            "data_extraction",
            "fact_checking",
            "information_synthesis",
            "source_validation"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for research tasks."""
        return ["query"]
    
    async def _gather_information(self, query: str, sources: List[str], depth: str) -> List[Dict[str, Any]]:
        """Gather information from specified sources."""
        findings = []
        
        for source in sources:
            try:
                if source == "web_search":
                    result = await self._web_search(query, depth)
                elif source == "document_analysis":
                    result = await self._document_analysis(query, depth)
                elif source == "data_extraction":
                    result = await self._data_extraction(query, depth)
                elif source == "fact_checking":
                    result = await self._fact_checking(query, depth)
                else:
                    result = {"source": source, "data": [], "error": "Unknown source"}
                
                findings.append(result)
                
            except Exception as e:
                logger.warning(f"Error gathering from {source}: {str(e)}")
                findings.append({
                    "source": source,
                    "data": [],
                    "error": str(e)
                })
        
        return findings
    
    async def _web_search(self, query: str, depth: str) -> Dict[str, Any]:
        """Perform web search (mock implementation)."""
        # In a real implementation, this would use a search API
        await asyncio.sleep(1)  # Simulate API call
        
        return {
            "source": "web_search",
            "data": [
                {
                    "title": f"Search result for: {query}",
                    "url": "https://example.com",
                    "snippet": f"This is a mock search result for {query}",
                    "relevance": 0.8
                }
            ],
            "metadata": {"depth": depth, "results_count": 1}
        }
    
    async def _document_analysis(self, query: str, depth: str) -> Dict[str, Any]:
        """Analyze documents (mock implementation)."""
        await asyncio.sleep(0.5)
        
        return {
            "source": "document_analysis",
            "data": [
                {
                    "document": "sample_document.pdf",
                    "relevant_content": f"Content related to {query}",
                    "confidence": 0.7
                }
            ],
            "metadata": {"depth": depth, "documents_analyzed": 1}
        }
    
    async def _data_extraction(self, query: str, depth: str) -> Dict[str, Any]:
        """Extract structured data (mock implementation)."""
        await asyncio.sleep(0.3)
        
        return {
            "source": "data_extraction",
            "data": [
                {
                    "field": "extracted_data",
                    "value": f"Data related to {query}",
                    "source": "structured_source"
                }
            ],
            "metadata": {"depth": depth, "records_extracted": 1}
        }
    
    async def _fact_checking(self, query: str, depth: str) -> Dict[str, Any]:
        """Perform fact checking (mock implementation)."""
        await asyncio.sleep(0.8)
        
        return {
            "source": "fact_checking",
            "data": [
                {
                    "claim": f"Claim related to {query}",
                    "verification": "verified",
                    "confidence": 0.9
                }
            ],
            "metadata": {"depth": depth, "claims_checked": 1}
        }
    
    async def _analyze_findings(self, findings: List[Dict[str, Any]], research_type: str) -> Dict[str, Any]:
        """Analyze and synthesize research findings."""
        all_data = []
        for finding in findings:
            if "data" in finding:
                all_data.extend(finding["data"])
        
        return {
            "total_sources": len(findings),
            "total_data_points": len(all_data),
            "research_type": research_type,
            "key_insights": [
                f"Insight {i+1} based on research"
                for i in range(min(3, len(all_data)))
            ],
            "data_quality": self._assess_data_quality(all_data)
        }
    
    async def _generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate a summary of the research findings."""
        return f"Research completed with {analysis['total_sources']} sources and {analysis['total_data_points']} data points. Key insights identified."
    
    def _calculate_confidence(self, findings: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score for the research."""
        if not findings:
            return 0.0
        
        total_confidence = 0.0
        count = 0
        
        for finding in findings:
            if "data" in finding:
                for data_point in finding["data"]:
                    if "confidence" in data_point:
                        total_confidence += data_point["confidence"]
                        count += 1
                    elif "relevance" in data_point:
                        total_confidence += data_point["relevance"]
                        count += 1
        
        return total_confidence / count if count > 0 else 0.5
    
    def _assess_data_quality(self, data: List[Dict[str, Any]]) -> str:
        """Assess the quality of gathered data."""
        if len(data) >= 10:
            return "high"
        elif len(data) >= 5:
            return "medium"
        else:
            return "low"
