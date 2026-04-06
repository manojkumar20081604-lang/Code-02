"""
============================================================
CODE-02 MAIN ORCHESTRATOR
============================================================
Central controller that ties all modules together
"""

import asyncio
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

# Import all modules
from core import get_code02 as get_base_code02
from core.environment.manager import get_env_manager, EnvironmentManager
from core.llm import create_llm_brain, get_llm_brain, LLMBrain
from core.database import get_enhanced_memory, EnhancedMemory
from core.automation import get_automation_engine, AutomationEngine, ExecutionMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Code02")


@dataclass
class ModuleStatus:
    name: str
    status: str  # online, offline, error
    last_update: str
    info: Dict = None


@dataclass
class SystemEvent:
    type: str  # startup, shutdown, error, task_complete, etc.
    source: str
    data: Dict
    timestamp: str


class Code02OS:
    """
    Code-02 Autonomous AI Operating System
    Main orchestrator that coordinates all modules
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.version = "2.0.0"
        
        # Core modules
        self.llm: Optional[LLMBrain] = None
        self.memory: Optional[EnhancedMemory] = None
        self.automation: Optional[AutomationEngine] = None
        self.env_manager: Optional[EnvironmentManager] = None
        
        # Module status
        self.modules: Dict[str, ModuleStatus] = {}
        
        # Event handlers
        self.event_handlers: Dict[str, List] = {}
        
        # Configuration
        self.config = self._load_config()
        
        # Running state
        self.running = False
        self.background_tasks: List[asyncio.Task] = []
        
        logger.info(f"Code-02 OS v{self.version} initializing...")
    
    def _load_config(self) -> Dict:
        """Load configuration"""
        config_path = os.path.join("data", "config", "code02.json")
        
        default_config = {
            "llm": {
                "provider": "auto",  # auto, ollama, openai, anthropic, mock
                "model": "llama3.2",
                "temperature": 0.7,
                "max_tokens": 2048
            },
            "automation": {
                "mode": "safe",  # safe, standard, advanced, dangerous
                "timeout": 60,
                "max_history": 100
            },
            "memory": {
                "data_dir": "data/memory",
                "auto_cleanup_days": 30,
                "min_importance": 0.3
            },
            "environment": {
                "auto_install": True,
                "allowed_managers": ["pip", "npm", "pacman", "apt", "dnf"]
            },
            "modules": {
                "automation": True,
                "security": True,
                "monitor": True,
                "filesystem": True
            }
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    user_config = json.load(f)
                    # Merge with defaults
                    for key in default_config:
                        if key in user_config:
                            default_config[key].update(user_config[key])
            except:
                pass
        
        return default_config
    
    def _save_config(self):
        """Save configuration"""
        config_path = os.path.join("data", "config", "code02.json")
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        with open(config_path, "w") as f:
            json.dump(self.config, f, indent=2)
    
    async def initialize(self) -> bool:
        """Initialize all modules"""
        logger.info("Initializing Code-02 OS modules...")
        
        success = True
        
        # Initialize LLM Brain
        try:
            self.llm = create_llm_brain(
                provider=self.config["llm"]["provider"],
                model=self.config["llm"]["model"]
            )
            await self.llm.initialize()
            self._update_module_status("llm", "online")
            logger.info(f"LLM Brain initialized ({self.llm.provider.value})")
        except Exception as e:
            logger.error(f"LLM initialization failed: {e}")
            self._update_module_status("llm", "error", {"error": str(e)})
            success = False
        
        # Initialize Memory
        try:
            self.memory = get_enhanced_memory()
            self._update_module_status("memory", "online", self.memory.get_stats())
            logger.info("Enhanced Memory initialized")
        except Exception as e:
            logger.error(f"Memory initialization failed: {e}")
            self._update_module_status("memory", "error", {"error": str(e)})
            success = False
        
        # Initialize Automation Engine
        try:
            mode = ExecutionMode(self.config["automation"]["mode"])
            self.automation = get_automation_engine(mode)
            self._update_module_status("automation", "online", 
                                       self.automation.get_capabilities())
            logger.info(f"Automation Engine initialized ({mode.value})")
        except Exception as e:
            logger.error(f"Automation initialization failed: {e}")
            self._update_module_status("automation", "error", {"error": str(e)})
            success = False
        
        # Initialize Environment Manager
        try:
            self.env_manager = get_env_manager()
            self._update_module_status("environment", "online",
                                       await self.env_manager.get_system_info())
            logger.info("Environment Manager initialized")
        except Exception as e:
            logger.error(f"Environment initialization failed: {e}")
            self._update_module_status("environment", "error", {"error": str(e)})
        
        self.running = True
        self._emit_event("startup", "system", {"success": success})
        
        return success
    
    def _update_module_status(self, name: str, status: str, info: Dict = None):
        """Update module status"""
        self.modules[name] = ModuleStatus(
            name=name,
            status=status,
            last_update=datetime.now().isoformat(),
            info=info or {}
        )
    
    def _emit_event(self, event_type: str, source: str, data: Dict):
        """Emit system event"""
        event = SystemEvent(
            type=event_type,
            source=source,
            data=data,
            timestamp=datetime.now().isoformat()
        )
        
        # Store in memory
        if self.memory:
            self.memory.store(
                f"event_{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                json.dumps(data),
                entry_type="event",
                tags=[event_type, source]
            )
        
        # Call handlers
        if event_type in self.event_handlers:
            for handler in self.event_handlers[event_type]:
                try:
                    handler(event)
                except:
                    pass
    
    def on_event(self, event_type: str, handler):
        """Register event handler"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    async def process(self, user_input: str) -> Dict[str, Any]:
        """Process user input through the AI system"""
        
        # Store in memory
        if self.memory:
            self.memory.store_conversation("user", user_input)
        
        # Use LLM for reasoning
        if self.llm and self.llm.provider != "none":
            response = await self.llm.generate(user_input)
            
            # Store response
            if self.memory:
                self.memory.store_conversation("assistant", response.text)
            
            return {
                "success": True,
                "response": response.text,
                "model": response.model,
                "latency_ms": response.latency_ms
            }
        else:
            # Fallback to base Code-02
            base = get_base_code02()
            result = await base.process(user_input)
            return {
                "success": result["success"],
                "response": result["response"],
                "model": "code02-base"
            }
    
    async def execute_task(self, task: str, mode: str = None) -> Dict[str, Any]:
        """Execute a task using automation engine"""
        
        if mode:
            self.automation.set_mode(ExecutionMode(mode))
        
        result = await self.automation.execute(task, name=task[:50])
        
        # Learn from result
        if self.memory:
            self.memory.learn_from_action(
                task,
                result.status.value == "completed",
                result.stdout,
                result.stderr
            )
        
        return {
            "task_id": result.id,
            "status": result.status.value,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code
        }
    
    async def execute_workflow(self, workflow_def: Dict) -> Dict[str, Any]:
        """Execute a multi-step workflow"""
        
        workflow = self.automation.create_workflow(
            workflow_def.get("name", "Workflow"),
            workflow_def.get("steps", [])
        )
        
        result = await self.automation.execute_workflow(workflow)
        
        return {
            "workflow_id": result.id,
            "status": result.status.value,
            "results": result.results
        }
    
    async def install_dependency(self, package: str) -> Dict[str, Any]:
        """Install a dependency"""
        
        if self.config["environment"]["auto_install"]:
            result = await self.env_manager.install(package)
            
            # Store in memory
            if self.memory:
                self.memory.store(
                    f"installed_{package}",
                    json.dumps({"success": result.success, "output": result.output}),
                    entry_type="action",
                    tags=["installed", "dependency"]
                )
            
            return {
                "success": result.success,
                "package": result.package,
                "manager": result.manager,
                "output": result.output,
                "error": result.error
            }
        else:
            return {
                "success": False,
                "error": "Auto-install is disabled"
            }
    
    async def check_and_fix_environment(self) -> Dict[str, Any]:
        """Check and fix environment issues"""
        
        issues_found = []
        fixes_applied = []
        
        # Get required packages
        required = self.env_manager.get_required_packages()
        
        # Check each
        missing = await self.env_manager.check_dependencies(required)
        
        for pkg, installed in missing.items():
            if not installed:
                issues_found.append(pkg)
                
                if self.config["environment"]["auto_install"]:
                    result = await self.env_manager.install(pkg)
                    if result.success:
                        fixes_applied.append(pkg)
        
        return {
            "issues_found": issues_found,
            "fixes_applied": fixes_applied,
            "auto_install_enabled": self.config["environment"]["auto_install"]
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            "version": self.version,
            "running": self.running,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_str": str(uptime).split('.')[0],
            "modules": {
                name: {
                    "status": m.status,
                    "last_update": m.last_update,
                    "info": m.info
                }
                for name, m in self.modules.items()
            },
            "memory_stats": self.memory.get_stats() if self.memory else {},
            "config": self.config
        }
    
    async def think(self, problem: str) -> Dict[str, Any]:
        """Deep thinking about a problem"""
        
        if self.llm:
            return await self.llm.think(problem)
        else:
            return {
                "problem": problem,
                "error": "LLM not available"
            }
    
    async def shutdown(self):
        """Shutdown the system gracefully"""
        logger.info("Shutting down Code-02 OS...")
        
        self.running = False
        
        # Cancel background tasks
        for task in self.background_tasks:
            task.cancel()
        
        # Close memory
        if self.memory:
            self.memory.close()
        
        self._emit_event("shutdown", "system", {"graceful": True})
        
        logger.info("Code-02 OS shutdown complete")
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """Get system logs"""
        
        if self.memory:
            events = self.memory.search("event_", limit=limit)
            return [
                {
                    "id": e.get("id"),
                    "content": e.get("content"),
                    "timestamp": e.get("created_at")
                }
                for e in events
            ]
        
        return []


# Singleton
_code02_os: Optional[Code02OS] = None

def get_code02_os() -> Code02OS:
    global _code02_os
    if _code02_os is None:
        _code02_os = Code02OS()
    return _code02_os


async def main():
    """Main entry point"""
    
    print("=" * 60)
    print("CODE: 02 - Autonomous AI Operating System")
    print("=" * 60)
    print()
    
    os_instance = get_code02_os()
    
    # Initialize
    success = await os_instance.initialize()
    
    if not success:
        print("Warning: Some modules failed to initialize")
    
    print()
    print("System Status:")
    print("-" * 40)
    
    status = os_instance.get_system_status()
    print(f"Version: {status['version']}")
    print(f"Uptime: {status['uptime_str']}")
    print()
    
    for name, module in status["modules"].items():
        icon = "✓" if module["status"] == "online" else "✗"
        print(f"  [{icon}] {name}: {module['status']}")
    
    print()
    print("Ready! Type 'help' for commands.")
    print()
    
    # Interactive loop
    while os_instance.running:
        try:
            user_input = input("Code-02> ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                break
            
            if user_input.lower() == "status":
                status = os_instance.get_system_status()
                print(json.dumps(status, indent=2))
                continue
            
            if user_input.lower() == "help":
                print("""
Available commands:
  <message>     - Chat with AI
  status        - Show system status
  exec <cmd>    - Execute command
  install <pkg> - Install package
  think <topic> - Deep thinking
  history       - Show command history
  exit          - Exit
""")
                continue
            
            if user_input.startswith("exec "):
                cmd = user_input[5:]
                result = await os_instance.execute_task(cmd)
                print(f"Status: {result['status']}")
                if result.get("stdout"):
                    print(result["stdout"])
                if result.get("stderr"):
                    print(f"Error: {result['stderr']}")
                continue
            
            if user_input.startswith("install "):
                pkg = user_input[8:]
                result = await os_instance.install_dependency(pkg)
                print(f"Success: {result['success']}")
                if result.get("error"):
                    print(f"Error: {result['error']}")
                continue
            
            if user_input.startswith("think "):
                topic = user_input[6:]
                result = await os_instance.think(topic)
                print(result.get("reasoning", "Thinking unavailable"))
                continue
            
            # Default: process with AI
            result = await os_instance.process(user_input)
            print(result.get("response", "No response"))
            
        except KeyboardInterrupt:
            print("\nInterrupt received. Type 'exit' to quit.")
        except Exception as e:
            print(f"Error: {e}")
    
    await os_instance.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
