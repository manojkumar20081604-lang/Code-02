"""
============================================================
MULTI-AGENT ARCHITECTURE
============================================================
Specialized agents coordinated by AI Core
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import asyncio
import logging

logger = logging.getLogger("Agents")


@dataclass
class AgentMessage:
    from_agent: str
    to_agent: str
    content: Any
    message_type: str  # task, response, query, broadcast
    timestamp: float


class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.active = True
        self.message_queue: List[AgentMessage] = []
    
    async def receive(self, message: AgentMessage):
        """Receive a message"""
        self.message_queue.append(message)
        await self.process_message(message)
    
    async def process_message(self, message: AgentMessage):
        """Process incoming message - override in subclasses"""
        pass
    
    async def send(self, to: str, content: Any, agent_coordinator: Any, msg_type: str = "task"):
        """Send a message to another agent"""
        message = AgentMessage(
            from_agent=self.name,
            to_agent=to,
            content=content,
            message_type=msg_type,
            timestamp=asyncio.get_event_loop().time()
        )
        await agent_coordinator.route_message(message)


class OrchestratorAgent(BaseAgent):
    """Central orchestrator - coordinates all agents"""
    
    def __init__(self):
        super().__init__("orchestrator", "coordinator")
        self.agents: Dict[str, BaseAgent] = {}
        self.task_queue: List[Dict] = []
    
    def register_agent(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.name] = agent
        logger.info(f"Agent registered: {agent.name} ({agent.role})")
    
    async def route_message(self, message: AgentMessage):
        """Route message to target agent"""
        if message.to_agent in self.agents:
            await self.agents[message.to_agent].receive(message)
        elif message.to_agent == "all":
            # Broadcast
            for agent in self.agents.values():
                if agent.name != message.from_agent:
                    await agent.receive(message)
        else:
            logger.warning(f"Unknown agent: {message.to_agent}")
    
    async def assign_task(self, task: Dict) -> Dict:
        """Assign task to appropriate agent"""
        
        task_type = task.get("type", "general")
        self.task_queue.append(task)
        
        # Route to appropriate agent
        if task_type == "code":
            target = "developer"
        elif task_type == "data":
            target = "data_processor"
        elif task_type == "security":
            target = "security"
        elif task_type == "system":
            target = "system_control"
        elif task_type == "planning":
            target = "planner"
        else:
            target = "assistant"
        
        if target in self.agents:
            message = AgentMessage(
                from_agent="orchestrator",
                to_agent=target,
                content=task,
                message_type="task",
                timestamp=asyncio.get_event_loop().time()
            )
            await self.route_message(message)
        
        return {"status": "assigned", "target": target, "task": task}
    
    def get_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "agents": {
                name: {"role": agent.role, "active": agent.active}
                for name, agent in self.agents.items()
            },
            "queue_size": len(self.task_queue)
        }


class PlannerAgent(BaseAgent):
    """Agent specialized in planning and reasoning"""
    
    def __init__(self):
        super().__init__("planner", "planning")
        self.plans: List[Dict] = []
    
    async def process_message(self, message: AgentMessage):
        """Create a plan based on task"""
        
        if message.message_type == "task":
            task = message.content
            
            # Create plan
            plan = {
                "id": f"plan_{len(self.plans) + 1}",
                "task": task,
                "steps": self._create_steps(task),
                "status": "created"
            }
            
            self.plans.append(plan)
            
            # Send back to orchestrator
            return plan
    
    def _create_steps(self, task: Dict) -> List[Dict]:
        """Create execution steps for task"""
        
        task_desc = str(task.get("description", "")).lower()
        
        if "code" in task_desc or "build" in task_desc:
            return [
                {"step": 1, "action": "analyze_requirements"},
                {"step": 2, "action": "design_solution"},
                {"step": 3, "action": "implement_code"},
                {"step": 4, "action": "test_solution"}
            ]
        elif "data" in task_desc or "analyze" in task_desc:
            return [
                {"step": 1, "action": "load_data"},
                {"step": 2, "action": "process_data"},
                {"step": 3, "action": "analyze_data"},
                {"step": 4, "action": "generate_insights"}
            ]
        else:
            return [
                {"step": 1, "action": "understand_task"},
                {"step": 2, "action": "execute_task"},
                {"step": 3, "action": "verify_result"}
            ]


class DeveloperAgent(BaseAgent):
    """Agent specialized in code development"""
    
    def __init__(self):
        super().__init__("developer", "development")
        self.projects: List[Dict] = []
    
    async def process_message(self, message: AgentMessage):
        """Handle code development tasks"""
        
        if message.message_type == "task":
            task = message.content
            return await self._handle_code_task(task)
    
    async def _handle_code_task(self, task: Dict) -> Dict:
        """Handle a coding task"""
        
        task_desc = str(task.get("description", "")).lower()
        
        if "python" in task_desc:
            language = "python"
            template = "# Python code generated by CODE: 02\n\ndef main():\n    pass\n"
        elif "javascript" in task_desc or "js" in task_desc:
            language = "javascript"
            template = "// JavaScript code generated by CODE: 02\n\nfunction main() {}\n"
        else:
            language = "general"
            template = "// Code generated by CODE: 02\n"
        
        return {
            "language": language,
            "code": template,
            "status": "ready"
        }


class DataProcessorAgent(BaseAgent):
    """Agent specialized in data processing"""
    
    def __init__(self):
        super().__init__("data_processor", "data")
        self.analyses: List[Dict] = []
    
    async def process_message(self, message: AgentMessage):
        """Handle data processing tasks"""
        
        if message.message_type == "task":
            task = message.content
            return await self._handle_data_task(task)
    
    async def _handle_data_task(self, task: Dict) -> Dict:
        """Handle a data task"""
        
        return {
            "analysis_type": "ready",
            "capabilities": [
                "statistical_analysis",
                "visualization",
                "pattern_recognition",
                "prediction"
            ]
        }


class SecurityAgent(BaseAgent):
    """Agent specialized in security operations"""
    
    def __init__(self):
        super().__init__("security", "security")
        self.scans: List[Dict] = []
    
    async def process_message(self, message: AgentMessage):
        """Handle security tasks"""
        
        if message.message_type == "task":
            task = message.content
            return await self._handle_security_task(task)
    
    async def _handle_security_task(self, task: Dict) -> Dict:
        """Handle a security task"""
        
        task_desc = str(task.get("description", "")).lower()
        
        if "phishing" in task_desc or "url" in task_desc:
            return {
                "scan_type": "phishing_detection",
                "status": "ready"
            }
        elif "scan" in task_desc or "vulnerability" in task_desc:
            return {
                "scan_type": "vulnerability_scan",
                "status": "ready"
            }
        else:
            return {
                "scan_type": "general",
                "status": "ready",
                "tools": ["scanner", "analyzer", "detector"]
            }


class SystemControlAgent(BaseAgent):
    """Agent specialized in system control"""
    
    def __init__(self):
        super().__init__("system_control", "system")
    
    async def process_message(self, message: AgentMessage):
        """Handle system control tasks"""
        
        if message.message_type == "task":
            task = message.content
            return await self._handle_system_task(task)
    
    async def _handle_system_task(self, task: Dict) -> Dict:
        """Handle a system task"""
        
        return {
            "system_operations": [
                "file_management",
                "process_control",
                "terminal_execution",
                "application_launch"
            ],
            "status": "ready"
        }


class AssistantAgent(BaseAgent):
    """General purpose assistant agent"""
    
    def __init__(self):
        super().__init__("assistant", "general")
    
    async def process_message(self, message: AgentMessage):
        """Handle general tasks"""
        
        if message.message_type == "task":
            task = message.content
            return {
                "response": f"Assistant processing: {task.get('description', 'No description')}",
                "status": "completed"
            }


def create_agent_system() -> OrchestratorAgent:
    """Create and initialize the multi-agent system"""
    
    orchestrator = OrchestratorAgent()
    
    # Register all agents
    orchestrator.register_agent(PlannerAgent())
    orchestrator.register_agent(DeveloperAgent())
    orchestrator.register_agent(DataProcessorAgent())
    orchestrator.register_agent(SecurityAgent())
    orchestrator.register_agent(SystemControlAgent())
    orchestrator.register_agent(AssistantAgent())
    
    logger.info("Multi-agent system initialized")
    
    return orchestrator
