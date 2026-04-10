"""
============================================================
TOOL REGISTRY - Modular Tool System
============================================================
Dynamic tool invocation based on context
"""

from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass
import importlib
import logging

logger = logging.getLogger("ToolRegistry")


@dataclass
class Tool:
    name: str
    description: str
    category: str
    execute: Callable
    requires_input: bool = True
    output_type: str = "text"


class ToolRegistry:
    """
    Central registry for all available tools
    Tools are dynamically loaded and can be invoked based on context
    """
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._categories: Dict[str, list] = {}
        
        # Initialize built-in tools
        self._register_builtin_tools()
    
    def _register_builtin_tools(self):
        """Register all built-in tools"""
        
        # Code Generation Tool
        self.register(Tool(
            name="code_generator",
            description="Generate code in various languages",
            category="development",
            execute=self._code_generator
        ))
        
        # Data Analysis Tool
        self.register(Tool(
            name="data_analyzer",
            description="Analyze datasets and provide insights",
            category="data",
            execute=self._data_analyzer
        ))
        
        # Security Scanner Tool
        self.register(Tool(
            name="security_scanner",
            description="Scan for vulnerabilities and security issues",
            category="security",
            execute=self._security_scanner
        ))
        
        # File Operations Tool
        self.register(Tool(
            name="file_manager",
            description="Manage files and directories",
            category="system",
            execute=self._file_manager
        ))
        
        # Web Search Tool
        self.register(Tool(
            name="web_search",
            description="Search the web for information",
            category="information",
            execute=self._web_search
        ))
        
        # Calculator Tool
        self.register(Tool(
            name="calculator",
            description="Perform mathematical calculations",
            category="utility",
            execute=self._calculator
        ))
        
        # Text Generator Tool
        self.register(Tool(
            name="text_generator",
            description="Generate text, summaries, and reports",
            category="content",
            execute=self._text_generator
        ))
        
        # Visualization Tool
        self.register(Tool(
            name="data_visualizer",
            description="Create charts and visualizations",
            category="data",
            execute=self._data_visualizer
        ))
        
        logger.info(f"Registered {len(self._tools)} tools")
    
    def register(self, tool: Tool) -> None:
        """Register a new tool"""
        self._tools[tool.name] = tool
        
        if tool.category not in self._categories:
            self._categories[tool.category] = []
        self._categories[tool.category].append(tool.name)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self._tools.get(name)
    
    def get_tools_by_category(self, category: str) -> list:
        """Get all tools in a category"""
        return [self.get_tool(name) for name in self._categories.get(category, [])]
    
    def get_all_tools(self) -> Dict[str, Tool]:
        """Get all registered tools"""
        return self._tools.copy()
    
    def get_categories(self) -> Dict[str, list]:
        """Get all categories"""
        return self._categories.copy()
    
    async def execute_tool(self, tool_name: str, context: Any, executor: Any) -> Dict:
        """Execute a tool"""
        
        tool = self.get_tool(tool_name)
        
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}
        
        try:
            result = await tool.execute(context, executor)
            return {"success": True, "result": result}
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {"success": False, "error": str(e)}
    
    # Built-in tool implementations
    
    async def _code_generator(self, context: Any, executor: Any) -> Dict:
        """Generate code based on context"""
        
        goal = context.goal.description.lower()
        
        code_templates = {
            "python": '''def main():
    """Generated Python code"""
    print("Hello from CODE: 02")
    
if __name__ == "__main__":
    main()
''',
            "javascript": '''// Generated JavaScript code
function main() {
    console.log("Hello from CODE: 02");
}

main();
''',
            "web": '''<!DOCTYPE html>
<html>
<head>
    <title>Generated Page</title>
</head>
<body>
    <h1>Hello from CODE: 02</h1>
</body>
</html>
'''
        }
        
        if "python" in goal:
            return {"language": "python", "code": code_templates["python"]}
        elif "javascript" in goal or "js" in goal:
            return {"language": "javascript", "code": code_templates["javascript"]}
        elif "web" in goal or "html" in goal:
            return {"language": "html", "code": code_templates["web"]}
        
        return {"message": "Code generation ready. Specify language for full generation."}
    
    async def _data_analyzer(self, context: Any, executor: Any) -> Dict:
        """Analyze data"""
        
        return {
            "analysis_type": "ready",
            "capabilities": [
                "Statistical analysis",
                "Trend detection",
                "Pattern recognition",
                "Anomaly detection"
            ],
            "message": "Data analysis tool ready. Provide dataset for analysis."
        }
    
    async def _security_scanner(self, context: Any, executor: Any) -> Dict:
        """Security scanning"""
        
        goal = context.goal.description.lower()
        
        if "url" in goal or "website" in goal:
            return {
                "scan_type": "phishing",
                "status": "ready",
                "message": "Phishing detection ready. Provide URL to scan."
            }
        
        return {
            "scan_type": "general",
            "status": "ready",
            "capabilities": [
                "Port scanning",
                "Vulnerability assessment",
                "Phishing detection",
                "Password strength analysis"
            ]
        }
    
    async def _file_manager(self, context: Any, executor: Any) -> Dict:
        """File management operations"""
        
        return {
            "operations": [
                "list - List directory contents",
                "create - Create new file",
                "read - Read file contents",
                "write - Write to file",
                "delete - Delete file",
                "copy - Copy file",
                "move - Move file"
            ],
            "status": "ready"
        }
    
    async def _web_search(self, context: Any, executor: Any) -> Dict:
        """Web search functionality"""
        
        return {
            "status": "ready",
            "message": "Web search tool ready. Specify search query."
        }
    
    async def _calculator(self, context: Any, executor: Any) -> Dict:
        """Mathematical calculations"""
        
        goal = context.goal.description
        
        # Extract numbers and operation
        import re
        numbers = re.findall(r'\d+\.?\d*', goal)
        
        if len(numbers) >= 2:
            nums = [float(n) for n in numbers[:5]]
            return {
                "operation": "math_calc",
                "numbers": nums,
                "sum": sum(nums),
                "average": sum(nums) / len(nums),
                "max": max(nums),
                "min": min(nums)
            }
        
        return {"status": "ready", "message": "Provide numbers for calculation"}
    
    async def _text_generator(self, context: Any, executor: Any) -> Dict:
        """Generate text content"""
        
        return {
            "capabilities": [
                "Summarize text",
                "Generate report",
                "Write email",
                "Create documentation"
            ],
            "status": "ready"
        }
    
    async def _data_visualizer(self, context: Any, executor: Any) -> Dict:
        """Create visualizations"""
        
        return {
            "chart_types": [
                "line - Line charts",
                "bar - Bar charts",
                "pie - Pie charts",
                "scatter - Scatter plots",
                "histogram - Histograms",
                "heatmap - Heatmaps"
            ],
            "status": "ready",
            "message": "Provide data for visualization"
        }
