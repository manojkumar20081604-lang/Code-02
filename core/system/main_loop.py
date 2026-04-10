"""
============================================================
MAIN EXECUTION LOOP - Central AI Controller
============================================================
Continuous: listen → understand → decide → execute → learn
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any, Optional, Callable, List
from dataclasses import dataclass
import json

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from core.system.executor import CommandExecutor, SafetyLevel, ExecutionResult
from core.system.installer import AutonomousInstaller, PackageManager, InstallResult
from core.system.decision import DecisionEngine, Intent, Decision

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("MainLoop")


@dataclass
class SystemLog:
    timestamp: str
    level: str
    source: str
    message: str
    data: Dict[str, Any] = None


@dataclass
class TaskResult:
    success: bool
    output: str
    error: str = ""
    duration_ms: float = 0


class Code02Loop:
    """
    CODE-02 Main Execution Loop
    
    Continuous cycle:
    1. LISTEN - Wait for user input
    2. UNDERSTAND - Classify intent, extract entities
    3. DECIDE - Choose action, plan execution
    4. EXECUTE - Run tasks through appropriate modules
    5. LEARN - Store results, update context
    """
    
    def __init__(self):
        self.name = "CODE-02"
        self.version = "2.0"
        self.running = False
        self.start_time = datetime.now()
        
        # Core modules
        self.executor = CommandExecutor(safety_level=SafetyLevel.SAFE)
        self.installer = AutonomousInstaller()
        self.decision_engine = DecisionEngine()
        
        # Context and memory
        self.context: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.system_logs: List[SystemLog] = []
        self.max_logs = 500
        
        # Callbacks
        self.on_decision: Optional[Callable] = None
        self.on_execution: Optional[Callable] = None
        self.on_log: Optional[Callable] = None
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"{self.name} v{self.version} initialized")
    
    def _setup_routes(self):
        """Setup decision engine routes"""
        
        self.decision_engine.register_route(
            Intent.COMMAND,
            self._handle_command,
            priority=10
        )
        
        self.decision_engine.register_route(
            Intent.INSTALL,
            self._handle_install,
            priority=10
        )
        
        self.decision_engine.register_route(
            Intent.THINK,
            self._handle_think,
            priority=10
        )
        
        self.decision_engine.register_route(
            Intent.SYSTEM,
            self._handle_system,
            priority=5
        )
        
        self.decision_engine.register_route(
            Intent.QUERY,
            self._handle_query,
            priority=5
        )
        
        self.decision_engine.register_route(
            Intent.HELP,
            self._handle_help,
            priority=10
        )
    
    def _log(self, level: str, source: str, message: str, data: Dict = None):
        """Internal logging"""
        log_entry = SystemLog(
            timestamp=datetime.now().isoformat(),
            level=level,
            source=source,
            message=message,
            data=data
        )
        
        self.system_logs.append(log_entry)
        if len(self.system_logs) > self.max_logs:
            self.system_logs = self.system_logs[-self.max_logs:]
        
        if self.on_log:
            self.on_log(log_entry)
    
    # ============================================================
    # STEP 1: LISTEN - Get user input
    # ============================================================
    
    def listen(self) -> str:
        """Get user input - can be overridden for different input sources"""
        try:
            user_input = input(f"{self.name}> ").strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            return "exit"
    
    # ============================================================
    # STEP 2: UNDERSTAND - Classify intent
    # ============================================================
    
    def understand(self, user_input: str) -> Decision:
        """Understand user input"""
        
        self._log("INFO", "Decision", f"Understanding: {user_input[:50]}...")
        
        decision = self.decision_engine.decide(user_input)
        
        # Store in conversation
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "intent": decision.intent.value,
            "timestamp": datetime.now().isoformat()
        })
        
        if self.on_decision:
            self.on_decision(decision)
        
        return decision
    
    # ============================================================
    # STEP 3: DECIDE & EXECUTE - Handle based on intent
    # ============================================================
    
    async def decide_and_execute(self, decision: Decision) -> TaskResult:
        """Decide action and execute"""
        
        self._log("INFO", "Execution", f"Executing action: {decision.action}")
        
        try:
            if decision.action == "execute_command":
                return await self._handle_command(decision)
            elif decision.action == "install_package":
                return await self._handle_install(decision)
            elif decision.action == "deep_think":
                return await self._handle_think(decision)
            elif decision.action == "system_operation":
                return await self._handle_system(decision)
            elif decision.action == "answer_query":
                return await self._handle_query(decision)
            elif decision.action == "show_help":
                return await self._handle_help(decision)
            else:
                return await self._handle_chat(decision)
                
        except Exception as e:
            self._log("ERROR", "Execution", str(e))
            return TaskResult(
                success=False,
                output="",
                error=f"Execution error: {str(e)}"
            )
    
    # ============================================================
    # ACTION HANDLERS
    # ============================================================
    
    async def _handle_command(self, decision: Decision) -> TaskResult:
        """Handle command execution"""
        
        command = decision.parameters.get("command", decision.entities.get("command", ""))
        
        if not command:
            # Try to extract from user input
            command = decision.context.get("last_input", "")
        
        self._log("INFO", "Executor", f"Running: {command}")
        
        result = self.executor.execute(command)
        
        return TaskResult(
            success=result.success,
            output=result.stdout,
            error=result.stderr,
            duration_ms=result.duration_ms
        )
    
    async def _handle_install(self, decision: Decision) -> TaskResult:
        """Handle package installation"""
        
        package = decision.parameters.get("package", "")
        
        if not package:
            # Try to extract from entities
            for key, value in decision.entities.items():
                if key in ["package", "language"]:
                    package = value
                    break
        
        if not package:
            return TaskResult(
                success=False,
                output="",
                error="No package specified"
            )
        
        self._log("INFO", "Installer", f"Installing: {package}")
        
        result = self.installer.install(package)
        
        if result.success:
            self._log("INFO", "Installer", f"Installed: {package}")
            return TaskResult(
                success=True,
                output=f"Successfully installed {package}",
                duration_ms=0
            )
        else:
            return TaskResult(
                success=False,
                output="",
                error=result.stderr
            )
    
    async def _handle_think(self, decision: Decision) -> TaskResult:
        """Handle deep thinking requests"""
        
        problem = decision.parameters.get("problem", decision.context.get("last_input", ""))
        
        self._log("INFO", "Brain", "Deep thinking engaged")
        
        # Simple reasoning (can be upgraded to LLM)
        response = self._simple_reasoning(problem)
        
        return TaskResult(
            success=True,
            output=response
        )
    
    async def _handle_system(self, decision: Decision) -> TaskResult:
        """Handle system operations"""
        
        user_input = decision.context.get("last_input", "").lower()
        
        if "status" in user_input:
            return TaskResult(
                success=True,
                output=json.dumps(self.get_status(), indent=2)
            )
        
        elif "uptime" in user_input:
            uptime = datetime.now() - self.start_time
            return TaskResult(
                success=True,
                output=f"System uptime: {str(uptime).split('.')[0]}"
            )
        
        elif "logs" in user_input:
            logs = self.get_logs(20)
            return TaskResult(
                success=True,
                output=json.dumps(logs, indent=2)
            )
        
        else:
            return TaskResult(
                success=True,
                output="Available system commands: status, uptime, logs"
            )
    
    async def _handle_query(self, decision: Decision) -> TaskResult:
        """Handle query/intelligence requests"""
        
        question = decision.parameters.get("question", "")
        
        # Simple responses (upgrade to LLM later)
        responses = {
            "who are you": "I am CODE-02, an autonomous AI system.",
            "what can you do": "I can execute commands, install packages, analyze problems, and more.",
            "help": self._get_help_text()
        }
        
        for key, value in responses.items():
            if key in question.lower():
                return TaskResult(success=True, output=value)
        
        return TaskResult(
            success=True,
            output=f"I understand you're asking about: {question[:50]}...\n{self._get_help_text()}"
        )
    
    async def _handle_help(self, decision: Decision) -> TaskResult:
        """Handle help requests"""
        return TaskResult(
            success=True,
            output=self._get_help_text()
        )
    
    async def _handle_chat(self, decision: Decision) -> TaskResult:
        """Handle general chat"""
        
        responses = [
            "I understand. How can I help you accomplish this?",
            "Got it. Let me help you with that.",
            "Interesting. Would you like me to take action on this?",
            "I'm here to help. What would you like to do?",
        ]
        
        import time
        response = responses[int(time.time()) % len(responses)]
        
        return TaskResult(success=True, output=response)
    
    # ============================================================
    # STEP 5: LEARN - Store results
    # ============================================================
    
    def learn(self, decision: Decision, result: TaskResult):
        """Learn from execution results"""
        
        # Store in conversation history
        self.conversation_history.append({
            "role": "assistant",
            "content": result.output if result.success else result.error,
            "intent": decision.intent.value,
            "success": result.success,
            "timestamp": datetime.now().isoformat()
        })
        
        # Update context
        self.context["last_result"] = result
        self.context["last_success"] = result.success
        
        self._log(
            "INFO" if result.success else "ERROR",
            "Learning",
            f"Task {'succeeded' if result.success else 'failed'}",
            {"intent": decision.intent.value, "duration_ms": result.duration_ms}
        )
    
    # ============================================================
    # SIMPLE REASONING
    # ============================================================
    
    def _simple_reasoning(self, problem: str) -> str:
        """Simple reasoning engine (placeholder for LLM)"""
        
        reasoning = f"""
Analysis of: "{problem}"

Step 1: Understanding
- This appears to be a request for analysis or explanation

Step 2: Breaking Down
- Identified key components
- Analyzing relationships

Step 3: Reasoning
- Drawing logical conclusions
- Considering alternatives

Step 4: Conclusion
- This requires deeper understanding
- Consider breaking into smaller steps

For advanced reasoning, connect an LLM (Ollama, OpenAI, or Anthropic).
"""
        
        return reasoning.strip()
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _get_help_text(self) -> str:
        """Get help text"""
        return """
CODE-02 Commands:
==================

COMMANDS:
  <any shell command>  Execute a shell command
  ls, ps, cat, grep     Run standard commands

INSTALLATION:
  install <package>     Install a package
  pip install flask     Install Python package
  npm install react     Install Node package

SYSTEM:
  status                Show system status
  uptime                Show system uptime
  logs                  Show recent logs

REASONING:
  think <problem>       Deep analysis of a problem

HELP:
  help                 Show this help
  commands             Show available commands

EXAMPLES:
  install nmap
  exec ls -la
  think about building a web scraper
"""
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        uptime = datetime.now() - self.start_time
        
        return {
            "name": self.name,
            "version": self.version,
            "running": self.running,
            "uptime_seconds": uptime.total_seconds(),
            "modules": {
                "executor": self.executor.get_capabilities(),
                "installer": self.installer.get_status(),
            },
            "history_count": len(self.conversation_history),
            "logs_count": len(self.system_logs)
        }
    
    def get_logs(self, limit: int = 50) -> List[Dict]:
        """Get system logs"""
        return [
            {
                "timestamp": log.timestamp,
                "level": log.level,
                "source": log.source,
                "message": log.message
            }
            for log in self.system_logs[-limit:]
        ]
    
    # ============================================================
    # MAIN LOOP
    # ============================================================
    
    async def run(self):
        """Main execution loop"""
        
        self.running = True
        
        print("=" * 60)
        print(f"  {self.name} v{self.version} - Autonomous AI System")
        print("=" * 60)
        print()
        print("Type 'help' for commands, 'exit' to quit")
        print()
        
        self._log("INFO", "System", f"{self.name} started")
        
        while self.running:
            try:
                # Step 1: Listen
                user_input = self.listen()
                
                if not user_input or user_input.lower() in ["exit", "quit", "bye"]:
                    break
                
                if not user_input.strip():
                    continue
                
                # Step 2: Understand
                decision = self.understand(user_input)
                
                # Step 3 & 4: Decide & Execute
                result = await self.decide_and_execute(decision)
                
                # Step 5: Learn
                self.learn(decision, result)
                
                # Output result
                if result.success:
                    print(result.output)
                else:
                    print(f"Error: {result.error}")
                
            except KeyboardInterrupt:
                print("\n(Use 'exit' to quit)")
                continue
            except EOFError:
                break
            except Exception as e:
                self._log("ERROR", "MainLoop", str(e))
                print(f"Error: {e}")
        
        self._log("INFO", "System", f"{self.name} stopped")
        self.running = False
    
    def stop(self):
        """Stop the main loop"""
        self.running = False


async def main():
    """Entry point"""
    system = Code02Loop()
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())
