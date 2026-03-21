"""
Coder agent for code generation and development tasks.
"""

from typing import Dict, Any, List, Optional
from .base import BaseAgent, AgentResponse
import logging
import asyncio

logger = logging.getLogger(__name__)

class CoderAgent(BaseAgent):
    """Agent responsible for code generation and development."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__("coder", config)
        self.supported_languages = {
            "python": self._generate_python,
            "javascript": self._generate_javascript,
            "java": self._generate_java,
            "cpp": self._generate_cpp,
            "html": self._generate_html,
            "css": self._generate_css
        }
    
    async def execute(self, task: Dict[str, Any]) -> AgentResponse:
        """
        Execute coding task to generate or modify code.
        
        Args:
            task: Dictionary containing coding requirements and specifications
            
        Returns:
            AgentResponse with generated code
        """
        try:
            if not self.validate_task(task):
                return AgentResponse(
                    success=False,
                    error="Invalid task format for coder agent"
                )
            
            language = task.get("language", "python")
            task_type = task.get("task_type", "generate")
            requirements = task.get("requirements", "")
            specifications = task.get("specifications", {})
            existing_code = task.get("existing_code", "")
            
            self.logger.info(f"Generating {language} code for: {task_type}")
            
            # Generate code based on task type
            if task_type == "generate":
                code = await self._generate_code(language, requirements, specifications)
            elif task_type == "modify":
                code = await self._modify_code(existing_code, requirements, specifications)
            elif task_type == "debug":
                code = await self._debug_code(existing_code, requirements)
            elif task_type == "optimize":
                code = await self._optimize_code(existing_code, specifications)
            else:
                return AgentResponse(
                    success=False,
                    error=f"Unsupported task type: {task_type}"
                )
            
            # Validate generated code
            validation_result = await self._validate_code(code, language)
            
            # Generate documentation
            documentation = await self._generate_documentation(code, language)
            
            # Create test cases
            test_cases = await self._generate_test_cases(code, language, requirements)
            
            return AgentResponse(
                success=True,
                data={
                    "code": code,
                    "language": language,
                    "task_type": task_type,
                    "validation": validation_result,
                    "documentation": documentation,
                    "test_cases": test_cases,
                    "complexity": self._assess_complexity(code),
                    "lines_of_code": len(code.split('\n'))
                },
                metadata={
                    "generation_time": "N/A",
                    "confidence": validation_result.get("confidence", 0.8)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in coder agent: {str(e)}")
            return AgentResponse(
                success=False,
                error=f"Code generation failed: {str(e)}"
            )
    
    def get_capabilities(self) -> List[str]:
        """Return list of coder capabilities."""
        return [
            "code_generation",
            "code_modification",
            "debugging",
            "code_optimization",
            "documentation_generation",
            "test_case_generation"
        ]
    
    def get_required_fields(self) -> List[str]:
        """Return required fields for coding tasks."""
        return ["language", "task_type", "requirements"]
    
    async def _generate_code(self, language: str, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate code based on language and requirements."""
        generator_func = self.supported_languages.get(language, self._generate_python)
        return await generator_func(requirements, specifications)
    
    async def _modify_code(self, existing_code: str, requirements: str, specifications: Dict[str, Any]) -> str:
        """Modify existing code based on requirements."""
        await asyncio.sleep(1)
        
        # Simple modification logic (in real implementation, would use LLM)
        modifications = []
        
        if "add comments" in requirements.lower():
            modifications.append("# Added comments for clarity")
        
        if "add error handling" in requirements.lower():
            modifications.append("# Added error handling")
        
        if "optimize" in requirements.lower():
            modifications.append("# Optimized implementation")
        
        if modifications:
            header = "\n".join(modifications) + "\n\n"
            return header + existing_code
        else:
            return existing_code
    
    async def _debug_code(self, existing_code: str, requirements: str) -> str:
        """Debug existing code."""
        await asyncio.sleep(0.8)
        
        # Simple debugging (in real implementation, would analyze and fix issues)
        debugged_code = existing_code
        
        # Add common debugging patterns
        if "print(" not in existing_code and "python" in requirements.lower():
            debugged_code += "\n\n# Debug statements\nprint('Debug: Code execution reached this point')"
        
        return debugged_code
    
    async def _optimize_code(self, existing_code: str, specifications: Dict[str, Any]) -> str:
        """Optimize existing code."""
        await asyncio.sleep(1.1)
        
        # Simple optimization (in real implementation, would use advanced techniques)
        optimized_code = f"""# Optimized version of the code
# Performance improvements applied:
# - Reduced time complexity
# - Improved memory usage
# - Added caching where appropriate

{existing_code}"""
        
        return optimized_code
    
    async def _generate_python(self, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate Python code."""
        await asyncio.sleep(1.2)
        
        return f'''"""
Python code generated for: {requirements}
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class GeneratedSolution:
    """Auto-generated solution based on requirements."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {{}}
        self.logger = logging.getLogger(__name__)
    
    async def execute(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the main logic for: {requirements}
        
        Args:
            data: Input data for processing
            
        Returns:
            Processed output data
        """
        try:
            # Main implementation logic here
            result = await self._process_data(data)
            
            self.logger.info("Execution completed successfully")
            return {{
                "status": "success",
                "result": result,
                "metadata": {{
                    "processing_time": "N/A",
                    "data_points": len(data) if isinstance(data, (list, dict)) else 1
                }}
            }}
            
        except Exception as e:
            self.logger.error(f"Execution failed: {{str(e)}}")
            return {{
                "status": "error",
                "error": str(e)
            }}
    
    async def _process_data(self, data: Dict[str, Any]) -> Any:
        """Process the input data."""
        # Implementation specific to requirements
        return data
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data."""
        return isinstance(data, dict)

# Example usage
async def main():
    solution = GeneratedSolution()
    result = await solution.execute({{"input": "test"}})
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    async def _generate_javascript(self, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate JavaScript code."""
        await asyncio.sleep(1.0)
        
        return f'''/**
 * JavaScript code generated for: {requirements}
 */

class GeneratedSolution {{
    constructor(config = {{}}) {{
        this.config = config;
        this.logger = console;
    }}
    
    /**
     * Execute the main logic
     * @param {{Object}} data - Input data for processing
     * @returns {{Promise<Object>}} Processed output data
     */
    async execute(data) {{
        try {{
            // Main implementation logic here
            const result = await this._processData(data);
            
            this.logger.info('Execution completed successfully');
            return {{
                status: 'success',
                result: result,
                metadata: {{
                    processingTime: Date.now(),
                    dataPoints: Array.isArray(data) ? data.length : 1
                }}
            }};
        }} catch (error) {{
            this.logger.error('Execution failed:', error);
            return {{
                status: 'error',
                error: error.message
            }};
        }}
    }}
    
    /**
     * Process the input data
     * @param {{Object}} data - Input data
     * @returns {{Promise<any>}} Processed data
     */
    async _processData(data) {{
        // Implementation specific to requirements
        return data;
    }}
    
    /**
     * Validate input data
     * @param {{Object}} data - Input data
     * @returns {{boolean}} True if valid
     */
    validateInput(data) {{
        return typeof data === 'object' && data !== null;
    }}
}}

// Example usage
async function main() {{
    const solution = new GeneratedSolution();
    const result = await solution.execute({{ input: 'test' }});
    console.log(result);
}}

if (require.main === module) {{
    main().catch(console.error);
}}

module.exports = GeneratedSolution;
'''
    
    async def _generate_java(self, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate Java code."""
        await asyncio.sleep(1.3)
        
        return f'''/**
 * Java code generated for: {requirements}
 */

import java.util.*;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.Future;
import java.util.logging.Logger;

public class GeneratedSolution {{
    private static final Logger logger = Logger.getLogger(GeneratedSolution.class.getName());
    private Map<String, Object> config;
    
    public GeneratedSolution(Map<String, Object> config) {{
        this.config = config != null ? config : new HashMap<>();
    }}
    
    public GeneratedSolution() {{
        this(new HashMap<>());
    }}
    
    /**
     * Execute the main logic
     * @param data Input data for processing
     * @return Future containing processed output data
     */
    public CompletableFuture<Map<String, Object>> execute(Map<String, Object> data) {{
        return CompletableFuture.supplyAsync(() -> {{
            try {{
                // Main implementation logic here
                Object result = processData(data);
                
                logger.info("Execution completed successfully");
                Map<String, Object> response = new HashMap<>();
                response.put("status", "success");
                response.put("result", result);
                
                Map<String, Object> metadata = new HashMap<>();
                metadata.put("processingTime", System.currentTimeMillis());
                metadata.put("dataPoints", data != null ? data.size() : 0);
                response.put("metadata", metadata);
                
                return response;
                
            }} catch (Exception e) {{
                logger.severe("Execution failed: " + e.getMessage());
                Map<String, Object> response = new HashMap<>();
                response.put("status", "error");
                response.put("error", e.getMessage());
                return response;
            }}
        }});
    }}
    
    /**
     * Process the input data
     * @param data Input data
     * @return Processed data
     */
    private Object processData(Map<String, Object> data) {{
        // Implementation specific to requirements
        return data;
    }}
    
    /**
     * Validate input data
     * @param data Input data
     * @return True if valid
     */
    public boolean validateInput(Map<String, Object> data) {{
        return data != null;
    }}
    
    public static void main(String[] args) {{
        GeneratedSolution solution = new GeneratedSolution();
        Map<String, Object> input = new HashMap<>();
        input.put("input", "test");
        
        solution.execute(input)
            .thenAccept(result -> System.out.println(result))
            .exceptionally(throwable -> {{
                System.err.println("Error: " + throwable.getMessage());
                return null;
            }});
    }}
}}
'''
    
    async def _generate_cpp(self, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate C++ code."""
        await asyncio.sleep(1.1)
        
        return f'''/**
 * C++ code generated for: {requirements}
 */

#include <iostream>
#include <map>
#include <string>
#include <vector>
#include <memory>
#include <chrono>
#include <future>

class GeneratedSolution {{
private:
    std::map<std::string, std::any> config;
    
public:
    explicit GeneratedSolution(const std::map<std::string, std::any>& cfg = {{}}) 
        : config(cfg) {{}}
    
    /**
     * Execute the main logic
     * @param data Input data for processing
     * @return Future containing processed output data
     */
    std::future<std::map<std::string, std::any>> execute(const std::map<std::string, std::any>& data) {{
        return std::async(std::launch::async, [this, data]() {{
            try {{
                // Main implementation logic here
                auto result = processData(data);
                
                std::cout << "Execution completed successfully" << std::endl;
                std::map<std::string, std::any> response;
                response["status"] = std::string("success");
                response["result"] = result;
                
                std::map<std::string, std::any> metadata;
                metadata["processingTime"] = std::chrono::duration_cast<std::chrono::milliseconds>(
                    std::chrono::system_clock::now().time_since_epoch()).count();
                metadata["dataPoints"] = data.size();
                response["metadata"] = metadata;
                
                return response;
                
            }} catch (const std::exception& e) {{
                std::cerr << "Execution failed: " << e.what() << std::endl;
                std::map<std::string, std::any> response;
                response["status"] = std::string("error");
                response["error"] = std::string(e.what());
                return response;
            }}
        }});
    }}
    
    /**
     * Process the input data
     * @param data Input data
     * @return Processed data
     */
    std::any processData(const std::map<std::string, std::any>& data) {{
        // Implementation specific to requirements
        return data;
    }}
    
    /**
     * Validate input data
     * @param data Input data
     * @return True if valid
     */
    bool validateInput(const std::map<std::string, std::any>& data) const {{
        return !data.empty();
    }}
}};

int main() {{
    try {{
        GeneratedSolution solution;
        std::map<std::string, std::any> input;
        input["input"] = std::string("test");
        
        auto future = solution.execute(input);
        auto result = future.get();
        
        // Print result (simplified)
        std::cout << "Execution completed" << std::endl;
        
    }} catch (const std::exception& e) {{
        std::cerr << "Error: " << e.what() << std::endl;
        return 1;
    }}
    
    return 0;
}}
'''
    
    async def _generate_html(self, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate HTML code."""
        await asyncio.sleep(0.7)
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{requirements}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            background: #f4f4f4;
            padding: 20px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .btn {{
            background: #007bff;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }}
        .btn:hover {{
            background: #0056b3;
        }}
    </style>
</head>
<body>
    <header>
        <h1>{requirements}</h1>
        <p>Auto-generated HTML page</p>
    </header>
    
    <main>
        <section class="container">
            <h2>Overview</h2>
            <p>This page was automatically generated to fulfill the requirements: {requirements}</p>
        </section>
        
        <section class="container">
            <h2>Features</h2>
            <ul>
                <li>Responsive design</li>
                <li>Clean semantic HTML</li>
                <li>Modern CSS styling</li>
                <li>Interactive elements</li>
            </ul>
        </section>
        
        <section class="container">
            <h2>Interactive Demo</h2>
            <button class="btn" onclick="showMessage()">Click Me!</button>
            <div id="message" style="margin-top: 10px;"></div>
        </section>
    </main>
    
    <footer>
        <p>&copy; 2024 Autonomous Multi-Agent Executor. Generated content.</p>
    </footer>
    
    <script>
        function showMessage() {{
            const messageDiv = document.getElementById('message');
            messageDiv.innerHTML = '<p style="color: green;">Button clicked! This is interactive content.</p>';
        }}
        
        // Add more interactive features as needed
        document.addEventListener('DOMContentLoaded', function() {{
            console.log('Page loaded successfully');
        }});
    </script>
</body>
</html>'''
    
    async def _generate_css(self, requirements: str, specifications: Dict[str, Any]) -> str:
        """Generate CSS code."""
        await asyncio.sleep(0.5)
        
        return f'''/**
 * CSS generated for: {requirements}
 */

/* Reset and base styles */
* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}}

/* Container styles */
.container {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}}

/* Header styles */
.header {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem 0;
    text-align: center;
}}

.header h1 {{
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    font-weight: 300;
}}

/* Navigation styles */
.nav {{
    background: #343a40;
    padding: 1rem 0;
}}

.nav ul {{
    list-style: none;
    display: flex;
    justify-content: center;
    gap: 2rem;
}}

.nav a {{
    color: white;
    text-decoration: none;
    padding: 0.5rem 1rem;
    border-radius: 4px;
    transition: background-color 0.3s ease;
}}

.nav a:hover {{
    background-color: #495057;
}}

/* Main content styles */
.main {{
    padding: 2rem 0;
}}

.card {{
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    padding: 1.5rem;
    margin-bottom: 2rem;
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}}

.card:hover {{
    transform: translateY(-2px);
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}}

.card h2 {{
    color: #495057;
    margin-bottom: 1rem;
    font-size: 1.5rem;
}}

/* Button styles */
.btn {{
    display: inline-block;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 4px;
    text-decoration: none;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s ease;
    text-align: center;
}}

.btn-primary {{
    background: #007bff;
    color: white;
}}

.btn-primary:hover {{
    background: #0056b3;
    transform: translateY(-1px);
}}

.btn-secondary {{
    background: #6c757d;
    color: white;
}}

.btn-secondary:hover {{
    background: #545b62;
}}

/* Form styles */
.form-group {{
    margin-bottom: 1rem;
}}

.form-label {{
    display: block;
    margin-bottom: 0.5rem;
    font-weight: 500;
}}

.form-control {{
    width: 100%;
    padding: 0.75rem;
    border: 1px solid #ced4da;
    border-radius: 4px;
    font-size: 1rem;
    transition: border-color 0.3s ease;
}}

.form-control:focus {{
    outline: none;
    border-color: #007bff;
    box-shadow: 0 0 0 2px rgba(0,123,255,0.25);
}}

/* Utility classes */
.text-center {{ text-align: center; }}
.text-right {{ text-align: right; }}
.mt-2 {{ margin-top: 1rem; }}
.mb-2 {{ margin-bottom: 1rem; }}
.p-2 {{ padding: 1rem; }}

/* Responsive design */
@media (max-width: 768px) {{
    .container {{
        padding: 0 10px;
    }}
    
    .header h1 {{
        font-size: 2rem;
    }}
    
    .nav ul {{
        flex-direction: column;
        gap: 0.5rem;
    }}
    
    .card {{
        padding: 1rem;
    }}
}}

@media (max-width: 480px) {{
    .header {{
        padding: 1rem 0;
    }}
    
    .header h1 {{
        font-size: 1.5rem;
    }}
    
    .btn {{
        display: block;
        width: 100%;
        margin-bottom: 0.5rem;
    }}
}}'''
    
    async def _validate_code(self, code: str, language: str) -> Dict[str, Any]:
        """Validate generated code."""
        await asyncio.sleep(0.3)
        
        # Basic validation checks
        validation = {
            "valid": True,
            "issues": [],
            "confidence": 0.8
        }
        
        # Check for basic syntax patterns
        if language == "python":
            if "def " not in code and "class " not in code:
                validation["issues"].append("No functions or classes found")
                validation["confidence"] -= 0.2
        elif language == "javascript":
            if "function" not in code and "class" not in code and "=>" not in code:
                validation["issues"].append("No functions or classes found")
                validation["confidence"] -= 0.2
        
        if validation["confidence"] < 0.5:
            validation["valid"] = False
        
        return validation
    
    async def _generate_documentation(self, code: str, language: str) -> str:
        """Generate documentation for the code."""
        await asyncio.sleep(0.4)
        
        doc_lines = [
            f"# Documentation for {language} code",
            "",
            "## Overview",
            "This code was automatically generated based on the provided requirements.",
            "",
            "## Usage",
            "```" + language,
            code[:200] + "..." if len(code) > 200 else code,
            "```",
            "",
            "## Features",
            "- Clean, readable code structure",
            "- Proper error handling",
            "- Comprehensive documentation",
            "- Modern best practices"
        ]
        
        return "\n".join(doc_lines)
    
    async def _generate_test_cases(self, code: str, language: str, requirements: str) -> List[str]:
        """Generate test cases for the code."""
        await asyncio.sleep(0.5)
        
        test_cases = [
            f"# Test case for {language} code",
            "## Test 1: Basic functionality",
            "## Test 2: Error handling", 
            "## Test 3: Edge cases",
            "## Test 4: Performance"
        ]
        
        return test_cases
    
    def _assess_complexity(self, code: str) -> str:
        """Assess the complexity of the generated code."""
        lines = len(code.split('\n'))
        
        if lines <= 50:
            return "low"
        elif lines <= 150:
            return "medium"
        else:
            return "high"
