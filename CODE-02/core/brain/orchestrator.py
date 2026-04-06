"""
============================================================
ORCHESTRATOR - Task Coordination and Execution
============================================================
Coordinates tools and agents to execute plans
"""

import asyncio
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger("Orchestrator")


@dataclass
class ExecutionResult:
    step_id: int
    action: str
    success: bool
    result: Any
    error: str = None
    duration: float = 0.0


class Orchestrator:
    """
    Orchestrates the execution of plans using available tools
    """
    
    def __init__(self):
        self.execution_history = []
    
    async def execute(
        self, 
        plan: Dict, 
        context: Any, 
        tools: Any, 
        executor: Any
    ) -> List[Dict]:
        """Execute a plan step by step"""
        
        results = []
        steps = plan.get("steps", [])
        
        logger.info(f"Executing plan with {len(steps)} steps")
        
        for i, step in enumerate(steps):
            step_result = await self._execute_step(step, context, tools, executor)
            results.append(step_result)
            
            # Update context
            context.current_step = i + 1
            context.reasoning_chain.append(f"Completed: {step['action']}")
            
            # Log progress
            logger.info(f"Step {i+1}/{len(steps)}: {step['action']} - {'Success' if step_result['success'] else 'Failed'}")
        
        return results
    
    async def _execute_step(
        self, 
        step: Dict, 
        context: Any, 
        tools: Any, 
        executor: Any
    ) -> Dict:
        """Execute a single step"""
        
        action = step.get("action")
        tool_name = step.get("tool")
        
        try:
            # Get the appropriate tool
            tool = tools.get_tool(tool_name)
            
            if tool:
                # Execute via tool
                result = await tool.execute(context, executor)
            else:
                # Execute via direct action
                result = await self._direct_action(action, context)
            
            return {
                "step_id": step.get("id"),
                "action": action,
                "success": True,
                "result": result,
                "output": self._format_output(result)
            }
            
        except Exception as e:
            logger.error(f"Error executing {action}: {e}")
            return {
                "step_id": step.get("id"),
                "action": action,
                "success": False,
                "error": str(e),
                "output": f"Error: {str(e)}"
            }
    
    async def _direct_action(self, action: str, context: Any) -> Any:
        """Handle direct actions without tools"""
        
        if action == "understand":
            return {"understanding": "Goal is clear and achievable"}
        
        if action == "identify_tools":
            return {"tools": ["code_generator", "data_analyzer"]}
        
        if action == "verify":
            return {"verified": True}
        
        return {"completed": True}
    
    def _format_output(self, result: Any) -> str:
        """Format result for display"""
        if isinstance(result, dict):
            if "message" in result:
                return result["message"]
            return str(result)
        return str(result) if result else "Completed"
