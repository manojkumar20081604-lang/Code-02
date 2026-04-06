"""
============================================================
CODE: 02 - COGNITIVE AUTONOMOUS AI SYSTEM
============================================================
A goal-driven AI assistant that thinks, plans, executes,
and continuously improves.

Author: Manojkumar M (B.Tech AI & Data Science)
============================================================
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

from core.brain.intent_detector import IntentDetector
from core.brain.planner import Planner
from core.brain.orchestrator import Orchestrator
from core.memory.short_term import ShortTermMemory
from core.memory.long_term import LongTermMemory
from core.planning.reasoning import ReasoningEngine
from core.tools.tool_registry import ToolRegistry
from core.action.executor import ActionExecutor
from core.learning.feedback import LearningLoop

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("CODE02")


@dataclass
class Goal:
    id: str
    description: str
    status: str = "pending"  # pending, planning, executing, completed, failed
    steps: List[Dict] = field(default_factory=list)
    results: List[Any] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    feedback_score: float = 0.0


@dataclass
class ExecutionContext:
    goal: Goal
    user_id: str
    session_id: str
    current_step: int = 0
    tool_results: Dict[str, Any] = field(default_factory=dict)
    reasoning_chain: List[str] = field(default_factory=list)


class Code02:
    """
    CODE: 02 - Cognitive Autonomous AI System
    
    A goal-driven AI that:
    1. Understands user intent
    2. Creates execution plans
    3. Executes tasks using tools
    4. Evaluates outcomes
    5. Continuously improves
    """
    
    def __init__(self, user_id: str = "default"):
        self.user_id = user_id
        self.session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        logger.info(f"Initializing CODE: 02 - Session: {self.session_id}")
        
        # Initialize core components
        self.intent_detector = IntentDetector()
        self.planner = Planner()
        self.orchestrator = Orchestrator()
        
        # Memory systems
        self.short_term = ShortTermMemory(max_items=50)
        self.long_term = LongTermMemory(user_id=user_id)
        
        # Reasoning engine
        self.reasoning = ReasoningEngine()
        
        # Tool registry
        self.tools = ToolRegistry()
        
        # Action executor
        self.executor = ActionExecutor()
        
        # Learning system
        self.learning = LearningLoop()
        
        # Active goals
        self.active_goals: Dict[str, Goal] = {}
        
        # System state
        self.state = {
            "status": "idle",
            "current_goal": None,
            "thinking": False,
            "last_update": datetime.now()
        }
        
        logger.info("CODE: 02 initialized successfully")
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """
        Main entry point - process user input as a goal
        """
        self.state["thinking"] = True
        self.state["status"] = "processing"
        
        try:
            # Store in short-term memory
            self.short_term.add("user_input", user_input)
            
            # Step 1: Detect intent
            intent = await self.intent_detector.analyze(user_input)
            self.short_term.add("intent", intent)
            
            # Step 2: Create goal
            goal = Goal(
                id=f"goal_{len(self.active_goals) + 1}",
                description=user_input
            )
            self.active_goals[goal.id] = goal
            
            # Step 3: Generate plan
            plan = await self.planner.create_plan(user_input, intent)
            goal.steps = plan["steps"]
            goal.status = "planning"
            
            self.short_term.add("plan", plan)
            
            # Step 4: Execute plan
            goal.status = "executing"
            self.state["current_goal"] = goal.id
            
            execution_context = ExecutionContext(
                goal=goal,
                user_id=self.user_id,
                session_id=self.session_id
            )
            
            results = await self.orchestrator.execute(
                plan, execution_context, self.tools, self.executor
            )
            
            goal.results = results
            goal.status = "completed"
            goal.completed_at = datetime.now()
            
            # Step 5: Learn from feedback
            await self.learning.record_execution(goal, results)
            
            # Store important info in long-term memory
            if intent.get("type") == "task":
                self.long_term.store_interaction(user_input, results)
            
            # Step 6: Generate response
            response = await self._generate_response(goal, results)
            
            self.state["thinking"] = False
            self.state["status"] = "idle"
            
            return {
                "success": True,
                "goal_id": goal.id,
                "intent": intent,
                "plan": plan,
                "results": results,
                "response": response,
                "workflow": self._get_workflow_steps(goal)
            }
            
        except Exception as e:
            logger.error(f"Error processing input: {e}")
            self.state["thinking"] = False
            self.state["status"] = "error"
            
            return {
                "success": False,
                "error": str(e),
                "response": f"I encountered an error: {str(e)}"
            }
    
    async def _generate_response(self, goal: Goal, results: List[Any]) -> str:
        """Generate natural language response"""
        if not results:
            return "I've completed the task. Is there anything else you'd like me to help with?"
        
        # Summarize results
        summary = []
        for r in results:
            if isinstance(r, dict):
                if "message" in r:
                    summary.append(r["message"])
                elif "result" in r:
                    summary.append(str(r["result"]))
        
        if summary:
            return " | ".join(summary)
        return "Task completed successfully."
    
    def _get_workflow_steps(self, goal: Goal) -> List[Dict]:
        """Get visualization steps for workflow"""
        steps = [
            {"step": 1, "name": "Understanding", "status": "completed", "icon": "brain"},
            {"step": 2, "name": "Planning", "status": "completed", "icon": "map"},
            {"step": 3, "name": "Executing", "status": "completed", "icon": "play"},
            {"step": 4, "name": "Evaluating", "status": "completed", "icon": "check"}
        ]
        return steps
    
    def get_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return {
            "status": self.state["status"],
            "thinking": self.state["thinking"],
            "current_goal": self.state["current_goal"],
            "session_id": self.session_id,
            "active_goals": len(self.active_goals),
            "memory_items": self.short_term.size()
        }
    
    async def think(self, prompt: str) -> Dict[str, Any]:
        """
        Reasoning mode - think through a problem
        """
        reasoning = await self.reasoning.think(prompt)
        return reasoning


# Singleton instance
_code02_instance: Optional[Code02] = None


def get_code02(user_id: str = "default") -> Code02:
    """Get or create CODE: 02 instance"""
    global _code02_instance
    if _code02_instance is None:
        _code02_instance = Code02(user_id)
    return _code02_instance
