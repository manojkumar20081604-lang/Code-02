"""
============================================================
PLANNER - Goal Decomposition and Planning
============================================================
Breaks down complex goals into actionable steps
"""

from typing import Dict, List, Any
import json


class Planner:
    """
    Creates execution plans for user goals
    """
    
    def __init__(self):
        self.plan_templates = {
            "build_project": [
                {"action": "analyze_requirements", "description": "Analyze project requirements"},
                {"action": "design_structure", "description": "Design project structure"},
                {"action": "generate_code", "description": "Generate code files"},
                {"action": "setup_dependencies", "description": "Setup dependencies"},
                {"action": "test_project", "description": "Test the project"}
            ],
            "analyze_data": [
                {"action": "load_data", "description": "Load and validate data"},
                {"action": "preprocess", "description": "Preprocess and clean data"},
                {"action": "analyze", "description": "Perform analysis"},
                {"action": "visualize", "description": "Generate visualizations"},
                {"action": "summarize", "description": "Summarize findings"}
            ],
            "security_check": [
                {"action": "scan_target", "description": "Scan target for vulnerabilities"},
                {"action": "analyze_results", "description": "Analyze scan results"},
                {"action": "generate_report", "description": "Generate security report"}
            ],
            "code_task": [
                {"action": "understand_code", "description": "Understand the code requirement"},
                {"action": "write_code", "description": "Write the code"},
                {"action": "validate_code", "description": "Validate the code"}
            ],
            "general": [
                {"action": "understand", "description": "Understand the goal"},
                {"action": "identify_tools", "description": "Identify required tools"},
                {"action": "execute", "description": "Execute the plan"},
                {"action": "verify", "description": "Verify results"}
            ]
        }
    
    async def create_plan(self, goal: str, intent: Dict) -> Dict[str, Any]:
        """Create an execution plan based on goal and intent"""
        
        intent_type = intent.get("type", "chat")
        context = intent.get("context", [])
        entities = intent.get("entities", {})
        
        # Select appropriate template
        template = self._select_template(goal, intent_type, context)
        
        # Customize plan based on entities
        steps = self._customize_steps(template, entities, goal)
        
        return {
            "goal": goal,
            "intent_type": intent_type,
            "steps": steps,
            "estimated_steps": len(steps),
            "requires_tools": self._check_tool_requirements(steps)
        }
    
    def _select_template(self, goal: str, intent_type: str, context: List[str]) -> List[Dict]:
        """Select the appropriate planning template"""
        goal_lower = goal.lower()
        
        # Check for specific patterns
        if any(w in goal_lower for w in ["build", "create", "make project"]):
            return self.plan_templates["build_project"]
        
        if any(w in goal_lower for w in ["analyze", "analysis", "data"]):
            return self.plan_templates["analyze_data"]
        
        if any(w in goal_lower for w in ["security", "scan", "vulnerability", "hack"]):
            return self.plan_templates["security_check"]
        
        if any(w in goal_lower for w in ["code", "function", "script", "python", "javascript"]):
            return self.plan_templates["code_task"]
        
        # Default based on intent type
        if intent_type == "task":
            return self.plan_templates["build_project"]
        if intent_type == "analysis":
            return self.plan_templates["analyze_data"]
        
        return self.plan_templates["general"]
    
    def _customize_steps(self, template: List[Dict], entities: Dict, goal: str) -> List[Dict]:
        """Customize plan steps based on entities and goal"""
        steps = []
        
        for i, step in enumerate(template):
            new_step = {
                "id": i + 1,
                "action": step["action"],
                "description": step["description"],
                "status": "pending",
                "tool": self._get_tool_for_action(step["action"])
            }
            steps.append(new_step)
        
        return steps
    
    def _get_tool_for_action(self, action: str) -> str:
        """Map actions to available tools"""
        tool_mapping = {
            "analyze_requirements": "code_analyzer",
            "design_structure": "code_generator",
            "generate_code": "code_generator",
            "setup_dependencies": "package_manager",
            "test_project": "code_tester",
            "load_data": "data_loader",
            "preprocess": "data_processor",
            "analyze": "data_analyzer",
            "visualize": "data_visualizer",
            "summarize": "text_generator",
            "scan_target": "security_scanner",
            "analyze_results": "security_analyzer",
            "generate_report": "report_generator",
            "understand": "reasoning",
            "identify_tools": "tool_selector",
            "execute": "action_executor",
            "verify": "verification",
            "understand_code": "code_reader",
            "write_code": "code_generator",
            "validate_code": "code_tester"
        }
        
        return tool_mapping.get(action, "general")
    
    def _check_tool_requirements(self, steps: List[Dict]) -> List[str]:
        """Check which tools are required"""
        tools = set()
        for step in steps:
            if step.get("tool"):
                tools.add(step["tool"])
        return list(tools)
    
    async def refine_plan(self, plan: Dict, feedback: Dict) -> Dict:
        """Refine plan based on execution feedback"""
        # Add learning from feedback
        return plan
