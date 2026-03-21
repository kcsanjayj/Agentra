"""
router.py - Smart Query Routing for 9.5+ Quality
Detects query intent and routes to appropriate agent/strategy
"""

from typing import Dict, Optional


class QueryRouter:
    """Routes queries to the right processing strategy based on intent"""
    
    def __init__(self):
        self.routing_map = {
            "study_plan": ["study plan", "study schedule", "learning plan", "prep plan", "revision plan"],
            "count_fact": ["how many", "count", "number of", "total", "sum of"],
            "code_generation": ["write code", "write a program", "function to", "script for", "code to"],
            "explanation": ["explain", "how to", "why does", "what is", "how do"],
            "comparison": ["compare", "difference between", "vs", "versus", "better than"],
            "list": ["list of", "examples of", "types of", "what are"],
        }
    
    def route(self, query: str) -> Dict:
        """
        Route query to appropriate agent/strategy
        Returns: {agent: str, strategy: str, constraints: list}
        """
        query_lower = query.lower()
        
        # Check for study plan patterns
        if any(pattern in query_lower for pattern in self.routing_map["study_plan"]):
            return {
                "agent": "planner",
                "strategy": "structured_plan",
                "constraints": ["day-by-day", "specific tasks", "measurable outcomes"],
                "prompt_style": "detailed_plan"
            }
        
        # Check for count/fact patterns
        if any(pattern in query_lower for pattern in self.routing_map["count_fact"]):
            return {
                "agent": "executor",
                "strategy": "direct_answer",
                "constraints": ["one sentence", "exact number", "no explanation"],
                "prompt_style": "concise_fact"
            }
        
        # Check for code patterns
        if any(pattern in query_lower for pattern in self.routing_map["code_generation"]):
            return {
                "agent": "coder",
                "strategy": "code_first",
                "constraints": ["working code", "clean syntax", "brief comments"],
                "prompt_style": "code_block"
            }
        
        # Check for comparison patterns
        if any(pattern in query_lower for pattern in self.routing_map["comparison"]):
            return {
                "agent": "analyst",
                "strategy": "side_by_side",
                "constraints": ["clear comparison", "key differences", "balanced view"],
                "prompt_style": "structured_compare"
            }
        
        # Check for list patterns
        if any(pattern in query_lower for pattern in self.routing_map["list"]):
            return {
                "agent": "researcher",
                "strategy": "enumerated_list",
                "constraints": ["numbered items", "brief descriptions", "complete list"],
                "prompt_style": "bullet_list"
            }
        
        # Default to explanation
        return {
            "agent": "executor",
            "strategy": "explanation",
            "constraints": ["clear", "concise", "direct answer"],
            "prompt_style": "explanation"
        }
    
    def get_agent_for_query(self, query: str) -> str:
        """Simple agent selection based on query"""
        route_info = self.route(query)
        return route_info["agent"]
    
    def get_constraints(self, query: str) -> list:
        """Get constraints for query type"""
        route_info = self.route(query)
        return route_info["constraints"]


# Singleton
router = QueryRouter()
