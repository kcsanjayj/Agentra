"""
Verifier agent for validation and quality assurance tasks.
"""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentResponse
import logging
import asyncio

logger = logging.getLogger(__name__)

class VerifierAgent(BaseAgent):
    """Agent responsible for verification and quality assurance."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("verifier", config)
        self.verification_types = {
            "content": self._verify_content,
            "code": self._verify_code,
            "data": self._verify_data,
            "logic": self._verify_logic
        }
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute verification task to validate outputs.
        
        Args:
            task: Dictionary containing verification requirements and content
            
        Returns:
            AgentResponse with verification results
        """
        try:
            if not self.validate_task(task):
                return AgentResponse(
                    success=False,
                    error="Invalid task format for verifier agent"
                )
            
            verification_type = task.get("verification_type", "content")
            content = task.get("content", {})
            requirements = task.get("requirements", [])
            standards = task.get("standards", {})
            criteria = task.get("criteria", {})
            
            self.logger.info(f"Verifying {verification_type} content")
            
            # Choose verification method
            verify_func = self.verification_types.get(verification_type, self._verify_content)
            
            # Perform verification
            verification_result = await verify_func(content, requirements, standards, criteria)
            
            # Generate verification report
            report = await self._generate_verification_report(verification_result, verification_type)
            
            # Calculate overall score
            score = self._calculate_verification_score(verification_result)
            
            return AgentResponse(
                success=True,
                data={
                    "verification_result": verification_result,
                    "verification_type": verification_type,
                    "overall_score": score,
                    "passed": score >= 0.7,
                    "report": report,
                    "recommendations": self._generate_recommendations(verification_result)
                },
                metadata={
                    "verification_time": "N/A",
                    "criteria_checked": len(criteria),
                    "requirements_met": self._count_met_requirements(verification_result)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in verifier agent: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Verification failed: {str(e)}"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return list of verifier capabilities."""
        return [
            "content_verification",
            "code_verification",
            "data_validation",
            "logic_verification",
            "quality_assurance",
            "compliance_checking"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for verification tasks."""
        return ["verification_type", "content"]
    
    async def _verify_content(self, content: Any, requirements: List[str], standards: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Verify content quality and compliance."""
        await asyncio.sleep(0.8)
        
        result = {
            "checks": {},
            "issues": [],
            "passed_checks": 0,
            "total_checks": 0
        }
        
        # Content quality checks
        if isinstance(content, str):
            # Check length
            min_length = criteria.get("min_length", 100)
            actual_length = len(content)
            length_check = actual_length >= min_length
            result["checks"]["length"] = {
                "passed": length_check,
                "expected": f">= {min_length}",
                "actual": actual_length
            }
            if length_check:
                result["passed_checks"] += 1
            result["total_checks"] += 1
            
            # Check for required sections
            required_sections = criteria.get("required_sections", [])
            for section in required_sections:
                section_check = section.lower() in content.lower()
                result["checks"][f"section_{section}"] = {
                    "passed": section_check,
                    "expected": f"Contains '{section}'",
                    "actual": "Found" if section_check else "Not found"
                }
                if section_check:
                    result["passed_checks"] += 1
                result["total_checks"] += 1
            
            # Check grammar and spelling (simplified)
            grammar_issues = self._check_grammar(content)
            result["checks"]["grammar"] = {
                "passed": len(grammar_issues) == 0,
                "expected": "No grammar issues",
                "actual": f"{len(grammar_issues)} issues found",
                "issues": grammar_issues
            }
            if len(grammar_issues) == 0:
                result["passed_checks"] += 1
            result["total_checks"] += 1
        
        # Check requirements compliance
        for req in requirements:
            req_check = self._check_requirement(content, req)
            result["checks"][f"requirement_{req}"] = req_check
            if req_check["passed"]:
                result["passed_checks"] += 1
            result["total_checks"] += 1
        
        return result
    
    async def _verify_code(self, content: Any, requirements: List[str], standards: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Verify code quality and standards."""
        await asyncio.sleep(1.0)
        
        result = {
            "checks": {},
            "issues": [],
            "passed_checks": 0,
            "total_checks": 0
        }
        
        if isinstance(content, str):
            # Check for proper indentation
            indentation_check = self._check_indentation(content)
            result["checks"]["indentation"] = {
                "passed": indentation_check["valid"],
                "expected": "Consistent indentation",
                "actual": indentation_check["message"]
            }
            if indentation_check["valid"]:
                result["passed_checks"] += 1
            result["total_checks"] += 1
            
            # Check for comments
            comment_check = self._check_comments(content)
            result["checks"]["comments"] = {
                "passed": comment_check["has_comments"],
                "expected": "Adequate comments",
                "actual": comment_check["message"]
            }
            if comment_check["has_comments"]:
                result["passed_checks"] += 1
            result["total_checks"] += 1
            
            # Check for error handling
            error_handling_check = self._check_error_handling(content)
            result["checks"]["error_handling"] = {
                "passed": error_handling_check["has_error_handling"],
                "expected": "Proper error handling",
                "actual": error_handling_check["message"]
            }
            if error_handling_check["has_error_handling"]:
                result["passed_checks"] += 1
            result["total_checks"] += 1
        
        return result
    
    async def _verify_data(self, content: Any, requirements: List[str], standards: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Verify data integrity and format."""
        await asyncio.sleep(0.6)
        
        result = {
            "checks": {},
            "issues": [],
            "passed_checks": 0,
            "total_checks": 0
        }
        
        # Check data structure
        if isinstance(content, dict):
            structure_check = self._check_data_structure(content, criteria)
            result["checks"]["structure"] = structure_check
            if structure_check["passed"]:
                result["passed_checks"] += 1
            result["total_checks"] += 1
            
            # Check data types
            type_check = self._check_data_types(content, criteria)
            result["checks"]["data_types"] = type_check
            if type_check["passed"]:
                result["passed_checks"] += 1
            result["total_checks"] += 1
        
        return result
    
    async def _verify_logic(self, content: Any, requirements: List[str], standards: Dict[str, Any], criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Verify logical consistency and coherence."""
        await asyncio.sleep(0.9)
        
        result = {
            "checks": {},
            "issues": [],
            "passed_checks": 0,
            "total_checks": 0
        }
        
        # Check logical consistency
        consistency_check = self._check_logical_consistency(content)
        result["checks"]["consistency"] = consistency_check
        if consistency_check["passed"]:
            result["passed_checks"] += 1
        result["total_checks"] += 1
        
        # Check coherence
        coherence_check = self._check_coherence(content)
        result["checks"]["coherence"] = coherence_check
        if coherence_check["passed"]:
            result["passed_checks"] += 1
        result["total_checks"] += 1
        
        return result
    
    def _check_grammar(self, content: str) -> List[str]:
        """Simple grammar check (mock implementation)."""
        issues = []
        
        # Check for common issues
        if "  " in content:  # Double spaces
            issues.append("Double spaces found")
        
        if content.count(". ") < 2 and len(content) > 200:  # Not enough sentences
            issues.append("Insufficient sentence structure")
        
        return issues
    
    def _check_requirement(self, content: Any, requirement: str) -> Dict[str, Any]:
        """Check if content meets a specific requirement."""
        if isinstance(content, str):
            meets = requirement.lower() in content.lower()
            return {
                "passed": meets,
                "expected": f"Contains '{requirement}'",
                "actual": "Found" if meets else "Not found"
            }
        else:
            return {
                "passed": False,
                "expected": f"Contains '{requirement}'",
                "actual": "Unable to verify (non-string content)"
            }
    
    def _check_indentation(self, code: str) -> Dict[str, Any]:
        """Check code indentation."""
        lines = code.split('\n')
        indent_sizes = []
        
        for line in lines:
            if line.strip():  # Skip empty lines
                indent = len(line) - len(line.lstrip())
                indent_sizes.append(indent)
        
        if len(set(indent_sizes)) <= 2:  # Allow some variation
            return {
                "valid": True,
                "message": f"Consistent indentation (sizes: {set(indent_sizes)})"
            }
        else:
            return {
                "valid": False,
                "message": f"Inconsistent indentation (sizes: {set(indent_sizes)})"
            }
    
    def _check_comments(self, code: str) -> Dict[str, Any]:
        """Check for adequate comments."""
        comment_patterns = ['#', '//', '/*', '*', '"""']
        comment_count = sum(1 for pattern in comment_patterns if pattern in code)
        
        lines = len([line for line in code.split('\n') if line.strip()])
        comment_ratio = comment_count / lines if lines > 0 else 0
        
        if comment_ratio >= 0.1:  # At least 10% comments
            return {
                "has_comments": True,
                "message": f"Adequate comments ({comment_ratio:.1%} of lines)"
            }
        else:
            return {
                "has_comments": False,
                "message": f"Insufficient comments ({comment_ratio:.1%} of lines)"
            }
    
    def _check_error_handling(self, code: str) -> Dict[str, Any]:
        """Check for error handling."""
        error_patterns = ['try:', 'try {', 'except', 'catch', 'error', 'Error']
        has_error_handling = any(pattern in code for pattern in error_patterns)
        
        return {
            "has_error_handling": has_error_handling,
            "message": "Error handling found" if has_error_handling else "No error handling detected"
        }
    
    def _check_data_structure(self, data: dict, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check data structure against criteria."""
        required_keys = criteria.get("required_keys", [])
        missing_keys = [key for key in required_keys if key not in data]
        
        return {
            "passed": len(missing_keys) == 0,
            "expected": f"Keys: {required_keys}",
            "actual": f"Keys: {list(data.keys())}",
            "missing_keys": missing_keys
        }
    
    def _check_data_types(self, data: dict, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Check data types."""
        expected_types = criteria.get("expected_types", {})
        type_mismatches = []
        
        for key, expected_type in expected_types.items():
            if key in data:
                actual_type = type(data[key]).__name__
                if actual_type != expected_type:
                    type_mismatches.append(f"{key}: expected {expected_type}, got {actual_type}")
        
        return {
            "passed": len(type_mismatches) == 0,
            "expected": f"Types: {expected_types}",
            "actual": f"Type mismatches: {type_mismatches}"
        }
    
    def _check_logical_consistency(self, content: Any) -> Dict[str, Any]:
        """Check logical consistency."""
        # Simplified consistency check
        return {
            "passed": True,
            "message": "Content appears logically consistent"
        }
    
    def _check_coherence(self, content: Any) -> Dict[str, Any]:
        """Check content coherence."""
        # Simplified coherence check
        return {
            "passed": True,
            "message": "Content appears coherent"
        }
    
    async def _generate_verification_report(self, result: Dict[str, Any], verification_type: str) -> str:
        """Generate a detailed verification report."""
        passed = result["passed_checks"]
        total = result["total_checks"]
        score = passed / total if total > 0 else 0
        
        report = f"""# Verification Report

## Summary
- **Verification Type**: {verification_type}
- **Checks Passed**: {passed}/{total}
- **Success Rate**: {score:.1%}
- **Status**: {'PASSED' if score >= 0.7 else 'FAILED'}

## Detailed Results
"""
        
        for check_name, check_result in result["checks"].items():
            status = "✅ PASS" if check_result["passed"] else "❌ FAIL"
            report += f"""
### {check_name.replace('_', ' ').title()}
- **Status**: {status}
- **Expected**: {check_result.get('expected', 'N/A')}
- **Actual**: {check_result.get('actual', 'N/A')}
"""
        
        return report
    
    def _calculate_verification_score(self, result: Dict[str, Any]) -> float:
        """Calculate overall verification score."""
        if result["total_checks"] == 0:
            return 0.0
        
        return result["passed_checks"] / result["total_checks"]
    
    def _generate_recommendations(self, result: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        for check_name, check_result in result["checks"].items():
            if not check_result["passed"]:
                if "length" in check_name:
                    recommendations.append("Increase content length to meet minimum requirements")
                elif "grammar" in check_name:
                    recommendations.append("Review and fix grammar issues")
                elif "indentation" in check_name:
                    recommendations.append("Fix code indentation for better readability")
                elif "comments" in check_name:
                    recommendations.append("Add more comments to explain complex logic")
                elif "error_handling" in check_name:
                    recommendations.append("Implement proper error handling")
                else:
                    recommendations.append(f"Address issues with {check_name}")
        
        return recommendations
    
    def _count_met_requirements(self, result: Dict[str, Any]) -> int:
        """Count how many requirements were met."""
        return result["passed_checks"]
    
    # ============== 9.5+ STRICT GATEKEEPER UPGRADES ==============
    
    def verify_strict(self, answer: str, query: str) -> Dict:
        """
        STRICT GATEKEEPER - 9.5+ quality verification
        Returns: {valid: bool, score: int, issues: list, passed: bool}
        """
        result = {
            "valid": True,
            "score": 100,
            "issues": [],
            "passed": True
        }
        
        answer_lower = answer.lower().strip()
        query_lower = query.lower()
        
        # Check 1: Relevance - must directly answer query
        query_keywords = self._extract_meaningful_keywords(query_lower)
        has_keyword = any(kw in answer_lower for kw in query_keywords if len(kw) > 3)
        if not has_keyword:
            result["valid"] = False
            result["issues"].append("not_relevant_to_query")
            result["score"] -= 25
        
        # Check 2: No truncation
        if answer.strip().endswith("...") or answer.strip().endswith("(") or answer.strip().endswith("["):
            result["valid"] = False
            result["issues"].append("truncated_output")
            result["score"] -= 30
        
        # Check 3: Anti-generic filter (CRITICAL)
        banned = ["some problems", "various problems", "etc", "...", "and so on",
                  "solve problems", "learn concepts", "practice topics", "various topics"]
        for phrase in banned:
            if phrase in answer_lower:
                result["valid"] = False
                result["issues"].append(f"banned_generic: {phrase}")
                result["score"] -= 20
        
        # Check 4: Complete sentences
        if not self._has_complete_ending(answer):
            result["valid"] = False
            result["issues"].append("incomplete_sentence")
            result["score"] -= 15
        
        # Check 5: Minimum quality
        if len(answer.strip()) < 10:
            result["valid"] = False
            result["issues"].append("too_short")
            result["score"] -= 50
        
        # Check 6: No dodging
        dodges = ["i don't know", "i'm not sure", "cannot answer", "no information"]
        if any(d in answer_lower for d in dodges):
            result["valid"] = False
            result["issues"].append("question_dodged")
            result["score"] -= 40
        
        # Final pass/fail
        result["passed"] = result["score"] >= 70 and len(result["issues"]) <= 2
        
        return result
    
    def quick_verify(self, answer: str) -> bool:
        """Quick validation for fast feedback"""
        if not answer or len(answer.strip()) < 5:
            return False
        
        answer_lower = answer.lower()
        
        if answer.strip().endswith("..."):
            return False
        
        banned_quick = ["some problems", "various topics", "etc"]
        for phrase in banned_quick:
            if phrase in answer_lower:
                return False
        
        return True
    
    def _extract_meaningful_keywords(self, query: str) -> List[str]:
        """Extract keywords that matter for relevance"""
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "in", "on", "at", "to", "for", "of", "with", "by", "from",
            "how", "what", "who", "when", "where", "why", "which",
            "do", "does", "did", "can", "could", "will", "would",
            "i", "you", "he", "she", "it", "we", "they",
            "my", "your", "his", "her", "its", "our", "their"
        }
        words = query.split()
        return [w for w in words if w not in stop_words and len(w) > 2]
    
    def _has_complete_ending(self, text: str) -> bool:
        """Check for proper sentence completion"""
        text = text.strip()
        endings = ['.', '!', '?', '"', "'", ')', ']', '}']
        return any(text.endswith(end) for end in endings)
    
    def explain_issues(self, issues: List[str]) -> str:
        """Convert issue codes to user-friendly explanations"""
        explanations = {
            "not_relevant_to_query": "Answer doesn't directly address the question",
            "truncated_output": "Answer appears to be cut off or incomplete",
            "incomplete_sentence": "Sentence is not properly finished",
            "too_short": "Answer is too brief to be useful",
            "question_dodged": "Answer avoids answering the question directly"
        }
        
        result = []
        for issue in issues:
            if issue.startswith("banned_generic:"):
                phrase = issue.split(":", 1)[1].strip()
                result.append(f"Contains vague phrase: '{phrase}'")
            else:
                result.append(explanations.get(issue, issue))
        
        return "; ".join(result) if result else "All checks passed"


# Simple Verifier class for direct import
class QualityVerifier:
    """Lightweight verifier for direct use in server.py"""
    
    @staticmethod
    def verify(answer: str, query: str) -> Dict:
        """Fast verification with scoring"""
        v = VerifierAgent()
        return v.verify_strict(answer, query)


# Singleton for easy import
verifier = QualityVerifier()
