"""
02 v1 - Autonomous Agent System
Executes tasks autonomously with learning and self-improvement
"""

import os
import json
import time
import uuid
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from threading import Thread, Event
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("02-Agent")

class AgentState(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    WAITING = "waiting"
    LEARNING = "learning"
    ERROR = "error"

@dataclass
class Task:
    id: str
    description: str
    priority: int = 2
    status: str = "pending"
    steps: List[Dict] = field(default_factory=list)
    current_step: int = 0
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

class AutonomousAgent:
    """
    Autonomous Agent - Executes tasks with minimal human intervention.
    
    Features:
    - Goal-oriented behavior
    - Multi-step execution
    - Error recovery
    - Learning from feedback
    - Proactive suggestions
    """
    
    def __init__(self, cognitive_system=None):
        self.cognitive = cognitive_system
        self.state = AgentState.IDLE
        self.tasks: Dict[str, Task] = {}
        self.current_task: Optional[Task] = None
        self.execution_history: List[Dict] = []
        self.is_autonomous_mode = False
        self.stop_event = Event()
        
        # Tools registry
        self.tools: Dict[str, Callable] = {}
        self._register_default_tools()
        
        # Performance metrics
        self.metrics = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "avg_execution_time": 0,
            "success_rate": 1.0
        }
        
        logger.info("Autonomous Agent initialized")
    
    def _register_default_tools(self):
        """Register default execution tools"""
        
        def tool_search(query: str) -> Dict:
            """Search the web"""
            return {"action": "search", "query": query, "status": "simulated"}
        
        def tool_code(language: str, code: str) -> Dict:
            """Execute code"""
            return {"action": "code", "language": language, "status": "simulated"}
        
        def tool_file(operation: str, path: str, content: str = None) -> Dict:
            """File operations"""
            return {"action": "file", "operation": operation, "path": path, "status": "simulated"}
        
        def tool_memory(operation: str, key: str, value: str = None) -> Dict:
            """Memory operations"""
            return {"action": "memory", "operation": operation, "key": key, "status": "simulated"}
        
        def tool_analyze(data: str) -> Dict:
            """Analyze data"""
            return {"action": "analyze", "data": data, "status": "simulated"}
        
        def tool_respond(message: str) -> Dict:
            """Generate response"""
            return {"action": "respond", "message": message, "status": "simulated"}
        
        self.tools = {
            "search": tool_search,
            "code": tool_code,
            "file": tool_file,
            "memory": tool_memory,
            "analyze": tool_analyze,
            "respond": tool_respond
        }
    
    def register_tool(self, name: str, func: Callable):
        """Register a new tool"""
        self.tools[name] = func
        logger.info(f"Registered tool: {name}")
    
    def create_task(self, description: str, priority: int = 2) -> Task:
        """Create a new task"""
        task_id = str(uuid.uuid4())[:8]
        task = Task(id=task_id, description=description, priority=priority)
        self.tasks[task_id] = task
        logger.info(f"Created task {task_id}: {description[:50]}...")
        return task
    
    def decompose_task(self, task: Task) -> List[Dict]:
        """Break task into executable steps"""
        desc_lower = task.description.lower()
        steps = []
        
        if "code" in desc_lower or "write" in desc_lower:
            steps = [
                {"action": "Understand requirements", "tool": "cognitive", "params": {}},
                {"action": "Generate code", "tool": "code", "params": {"language": "python"}},
                {"action": "Review code", "tool": "cognitive", "params": {}},
                {"action": "Return result", "tool": "respond", "params": {}}
            ]
        elif "analyze" in desc_lower:
            steps = [
                {"action": "Gather data", "tool": "analyze", "params": {}},
                {"action": "Process data", "tool": "analyze", "params": {}},
                {"action": "Generate insights", "tool": "cognitive", "params": {}},
                {"action": "Present results", "tool": "respond", "params": {}}
            ]
        elif "search" in desc_lower or "find" in desc_lower:
            steps = [
                {"action": "Parse query", "tool": "cognitive", "params": {}},
                {"action": "Execute search", "tool": "search", "params": {}},
                {"action": "Process results", "tool": "cognitive", "params": {}},
                {"action": "Present findings", "tool": "respond", "params": {}}
            ]
        else:
            steps = [
                {"action": "Process request", "tool": "cognitive", "params": {}},
                {"action": "Execute", "tool": "respond", "params": {}}
            ]
        
        task.steps = steps
        return steps
    
    async def execute_task(self, task: Task) -> Dict:
        """Execute a task with all steps"""
        self.state = AgentState.EXECUTING
        self.current_task = task
        task.status = "in_progress"
        
        logger.info(f"Executing task {task.id}: {task.description[:50]}...")
        
        start_time = time.time()
        results = []
        
        # Decompose if not already done
        if not task.steps:
            self.decompose_task(task)
        
        # Execute each step
        for i, step in enumerate(task.steps):
            task.current_step = i
            
            try:
                tool_name = step.get("tool", "respond")
                params = step.get("params", {})
                
                # Execute tool
                if tool_name in self.tools:
                    result = self.tools[tool_name](**params)
                else:
                    result = {"status": "unknown_tool", "action": step.get("action")}
                
                results.append({
                    "step": i,
                    "action": step.get("action"),
                    "result": result,
                    "success": True
                })
                
                # Store in memory
                if self.cognitive:
                    self.cognitive.memory.store(
                        content=f"Executed: {step.get('action')} - Result: {json.dumps(result)[:100]}",
                        memory_type=MemoryType.EPISODIC,
                        tags=["execution", tool_name]
                    )
                
            except Exception as e:
                error_result = {"status": "error", "error": str(e)}
                results.append({
                    "step": i,
                    "action": step.get("action"),
                    "result": error_result,
                    "success": False
                })
                task.error = str(e)
                logger.error(f"Step {i} failed: {e}")
        
        # Complete task
        task.status = "completed"
        task.completed_at = datetime.now()
        task.result = results
        
        elapsed = time.time() - start_time
        self.execution_history.append({
            "task_id": task.id,
            "description": task.description,
            "steps": len(task.steps),
            "success": task.error is None,
            "duration": elapsed,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update metrics
        self._update_metrics(success=task.error is None, duration=elapsed)
        
        self.state = AgentState.IDLE
        self.current_task = None
        
        return {
            "task_id": task.id,
            "success": task.error is None,
            "results": results,
            "duration": elapsed
        }
    
    def _update_metrics(self, success: bool, duration: float):
        """Update performance metrics"""
        total = self.metrics["tasks_completed"] + self.metrics["tasks_failed"] + 1
        if success:
            self.metrics["tasks_completed"] += 1
        else:
            self.metrics["tasks_failed"] += 1
        
        self.metrics["success_rate"] = self.metrics["tasks_completed"] / total
        self.metrics["avg_execution_time"] = (
            (self.metrics["avg_execution_time"] * (total - 1) + duration) / total
        )
    
    def enable_autonomous_mode(self):
        """Enable autonomous behavior"""
        self.is_autonomous_mode = True
        self.stop_event.clear()
        logger.info("Autonomous mode ENABLED")
    
    def disable_autonomous_mode(self):
        """Disable autonomous behavior"""
        self.is_autonomous_mode = False
        self.stop_event.set()
        logger.info("Autonomous mode DISABLED")
    
    def get_active_tasks(self) -> List[Dict]:
        """Get all active tasks"""
        return [
            {
                "id": t.id,
                "description": t.description,
                "status": t.status,
                "progress": t.current_step / len(t.steps) if t.steps else 0
            }
            for t in self.tasks.values()
            if t.status in ["pending", "in_progress"]
        ]
    
    def get_status(self) -> Dict:
        """Get agent status"""
        return {
            "state": self.state.value,
            "autonomous_mode": self.is_autonomous_mode,
            "current_task": self.current_task.id if self.current_task else None,
            "active_tasks": len(self.get_active_tasks()),
            "metrics": self.metrics
        }

class WorkflowExecutor:
    """
    Workflow Executor - Runs predefined automation workflows.
    """
    
    def __init__(self, agent: AutonomousAgent):
        self.agent = agent
        self.workflows: Dict[str, List[Dict]] = {}
        self._register_default_workflows()
    
    def _register_default_workflows(self):
        """Register common workflows"""
        
        self.workflows["code_review"] = [
            {"action": "Fetch code", "tool": "file", "params": {}},
            {"action": "Analyze code", "tool": "analyze", "params": {}},
            {"action": "Generate review", "tool": "cognitive", "params": {}},
            {"action": "Report findings", "tool": "respond", "params": {}}
        ]
        
        self.workflows["data_analysis"] = [
            {"action": "Load data", "tool": "file", "params": {}},
            {"action": "Clean data", "tool": "analyze", "params": {}},
            {"action": "Generate insights", "tool": "analyze", "params": {}},
            {"action": "Create visualizations", "tool": "cognitive", "params": {}},
            {"action": "Present report", "tool": "respond", "params": {}}
        ]
        
        self.workflows["security_scan"] = [
            {"action": "Scan ports", "tool": "search", "params": {}},
            {"action": "Check vulnerabilities", "tool": "analyze", "params": {}},
            {"action": "Generate report", "tool": "cognitive", "params": {}},
            {"action": "Alert if critical", "tool": "respond", "params": {}}
        ]
    
    def register_workflow(self, name: str, steps: List[Dict]):
        """Register a new workflow"""
        self.workflows[name] = steps
        logger.info(f"Registered workflow: {name}")
    
    async def run_workflow(self, name: str, context: Dict = None) -> Dict:
        """Execute a workflow"""
        if name not in self.workflows:
            return {"error": f"Workflow '{name}' not found"}
        
        steps = self.workflows[name]
        task = self.agent.create_task(f"Workflow: {name}", priority=1)
        task.steps = steps
        
        result = await self.agent.execute_task(task)
        return result


# Import memory type for storage
from core.cognitive import MemoryType

__all__ = ['AutonomousAgent', 'WorkflowExecutor', 'AgentState', 'Task']
