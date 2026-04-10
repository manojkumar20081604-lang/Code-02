"""
============================================================
UNIFIED MAIN EXECUTION LOOP
============================================================
Cross-platform AI controller: listen → understand → decide → execute → learn
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

from core.platform import detect, OSType, LinuxDistro
from core.automation import (
    get_automation,
    SafetyLevel,
    BaseAutomation,
    LinuxAutomation,
    WindowsAutomation
)
from core.installer import (
    get_installer,
    BaseInstaller,
    LinuxInstaller,
    WindowsInstaller
)
from core.system.decision import DecisionEngine, Intent, Decision

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
)
logger = logging.getLogger("Code02Main")


@dataclass
class CapabilityMode:
    name: str
    safety_level: SafetyLevel
    description: str


class Code02Unified:
    """
    Unified CODE-02 - Cross-Platform Autonomous AI System
    
    Architecture:
    ┌─────────────────────────────────────────────────────────┐
    │                    CODE-02 Core                        │
    │  ┌─────────┐  ┌──────────┐  ┌───────────────────┐   │
    │  │Decision │  │ Memory   │  │ Learning           │   │
    │  │ Engine  │  │ System   │  │ Loop               │   │
    │  └────┬────┘  └──────────┘  └───────────────────┘   │
    │       │                                             │
    │  ┌────▼────────────────────────────────────────┐   │
    │  │           Platform Abstraction Layer          │   │
    │  │  ┌──────────────┐  ┌───────────────────┐   │   │
    │  │  │ Automation   │  │ Installer          │   │   │
    │  │  │ (executor)   │  │ (dependencies)     │   │   │
    │  │  └──────┬───────┘  └─────────┬─────────┘   │   │
    │  └─────────┼─────────────────────┼─────────────┘   │
    │            │                     │                   │
    │  ┌─────────▼─────────┐ ┌──────▼─────────┐        │
    │  │ Linux │ Windows    │ │ Linux │ Windows │        │
    │  │ bash  │ PowerShell │ │pacman│ pip     │        │
    │  └───────┴────────────┘ └──────┴─────────┘        │
    └─────────────────────────────────────────────────────┘
    """
    
    # Capability modes
    SAFE_MODE = CapabilityMode(
        name="SAFE_MODE",
        safety_level=SafetyLevel.SAFE,
        description="Limited operations, high safety"
    )
    
    FULL_POWER = CapabilityMode(
        name="FULL_POWER",
        safety_level=SafetyLevel.ELEVATED,
        description="Full system access, all operations"
    )
    
    def __init__(self, mode: CapabilityMode = None):
        self.name = "CODE-02"
        self.version = "2.0"
        self.running = False
        self.start_time = datetime.now()
        
        # Detect OS
        self.os_info = detect.get_os()
        
        # Set capability mode based on OS
        if mode is None:
            if self.os_info.is_linux:
                self.mode = self.FULL_POWER
            else:
                self.mode = self.SAFE_MODE
        else:
            self.mode = mode
        
        # Initialize OS-specific modules
        self.automation = self._create_automation()
        self.installer = self._create_installer()
        self.decision_engine = DecisionEngine()
        
        # Context
        self.context: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.system_logs: List[Dict] = []
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"{self.name} v{self.version} initialized")
        logger.info(f"Platform: {self.os_info}")
        logger.info(f"Mode: {self.mode.name}")
    
    def _create_automation(self) -> BaseAutomation:
        """Create appropriate automation for OS"""
        if self.os_info.is_linux:
            return LinuxAutomation(self.mode.safety_level)
        elif self.os_info.is_windows:
            return WindowsAutomation(self.mode.safety_level)
        else:
            return LinuxAutomation(self.mode.safety_level)
    
    def _create_installer(self) -> BaseInstaller:
        """Create appropriate installer for OS"""
        if self.os_info.is_linux:
            return LinuxInstaller()
        elif self.os_info.is_windows:
            return WindowsInstaller()
        else:
            return LinuxInstaller()
    
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
            Intent.SYSTEM,
            self._handle_system,
            priority=8
        )
    
    def _log(self, level: str, source: str, message: str):
        """Log system event"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "source": source,
            "message": message
        }
        self.system_logs.append(entry)
        if len(self.system_logs) > 500:
            self.system_logs = self.system_logs[-500:]
    
    # ============================================================
    # MAIN LOOP STEPS
    # ============================================================
    
    def listen(self) -> str:
        """Step 1: Get user input"""
        try:
            user_input = input(f"{self.name}> ").strip()
            return user_input
        except (KeyboardInterrupt, EOFError):
            return "exit"
    
    def understand(self, user_input: str) -> Decision:
        """Step 2: Classify intent"""
        self._log("INFO", "Decision", f"Understanding: {user_input[:50]}...")
        return self.decision_engine.decide(user_input)
    
    async def decide_and_execute(self, decision: Decision) -> Dict[str, Any]:
        """Step 3 & 4: Decide and execute"""
        self._log("INFO", "Execution", f"Action: {decision.action}")
        
        try:
            if decision.action == "execute_command":
                return await self._handle_command(decision)
            elif decision.action == "install_package":
                return await self._handle_install(decision)
            elif decision.action == "system_operation":
                return await self._handle_system(decision)
            else:
                return await self._handle_chat(decision)
        except Exception as e:
            self._log("ERROR", "Execution", str(e))
            return {"success": False, "error": str(e)}
    
    def learn(self, decision: Decision, result: Dict):
        """Step 5: Learn from result"""
        self.conversation_history.append({
            "role": "user" if not result.get("role") else result["role"],
            "intent": decision.intent.value,
            "success": result.get("success", False),
            "timestamp": datetime.now().isoformat()
        })
    
    # ============================================================
    # ACTION HANDLERS
    # ============================================================
    
    async def _handle_command(self, decision: Decision) -> Dict[str, Any]:
        """Handle command execution"""
        
        command = decision.parameters.get("command", "")
        if not command:
            command = self.decision_engine.context.get("last_input", "")
        
        self._log("INFO", "Automation", f"Executing: {command}")
        
        result = self.automation.execute(command)
        
        return {
            "success": result.success,
            "output": result.stdout,
            "error": result.stderr if not result.success else None,
            "exit_code": result.exit_code,
            "duration_ms": result.duration_ms
        }
    
    async def _handle_install(self, decision: Decision) -> Dict[str, Any]:
        """Handle package installation"""
        
        package = decision.parameters.get("package", "")
        
        # Try entities
        if not package:
            for key, value in decision.entities.items():
                if key in ["package", "language"]:
                    package = value
                    break
        
        if not package:
            return {
                "success": False,
                "error": "No package specified"
            }
        
        self._log("INFO", "Installer", f"Installing: {package}")
        
        result = self.installer.install(package)
        
        return {
            "success": result.success,
            "package": result.package,
            "manager": result.manager,
            "output": result.stdout[:500] if result.stdout else None,
            "error": result.stderr if not result.success else None
        }
    
    async def _handle_system(self, decision: Decision) -> Dict[str, Any]:
        """Handle system operations"""
        
        user_input = self.decision_engine.context.get("last_input", "").lower()
        
        if "status" in user_input:
            return {
                "success": True,
                "output": json.dumps(self.get_status(), indent=2)
            }
        
        elif "process" in user_input or "ps" in user_input:
            processes = self.automation.get_process_list()
            return {
                "success": True,
                "output": f"Running processes:\n" + 
                         "\n".join([f"  {p['pid']}: {p['name']}" for p in processes[:10]])
            }
        
        elif "info" in user_input or "sysinfo" in user_input:
            info = self.automation.get_system_info()
            return {
                "success": True,
                "output": json.dumps(info, indent=2)
            }
        
        return {
            "success": True,
            "output": "Available system commands: status, process list, sysinfo"
        }
    
    async def _handle_chat(self, decision: Decision) -> Dict[str, Any]:
        """Handle general chat"""
        
        responses = [
            "I understand. How can I help you accomplish this?",
            "Got it. Let me help you with that.",
            "Interesting. Would you like me to take action?"
        ]
        
        import time
        response = responses[int(time.time()) % len(responses)]
        
        return {
            "success": True,
            "output": response
        }
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get system status"""
        return {
            "name": self.name,
            "version": self.version,
            "platform": str(self.os_info),
            "mode": self.mode.name,
            "capabilities": self.os_info.get_capabilities(),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "automation": self.automation.get_capabilities(),
            "installer": self.installer.get_status()
        }
    
    def get_platform_info(self) -> Dict[str, Any]:
        """Get detailed platform information"""
        return {
            "os_type": self.os_info.os_type.value,
            "distro": self.os_info.distro.value if self.os_info.distro else None,
            "version": self.os_info.info.version,
            "arch": self.os_info.info.arch,
            "full_power": self.os_info.is_linux,
            "safe_mode": not self.os_info.is_linux
        }
    
    def set_mode(self, mode: CapabilityMode):
        """Change operating mode"""
        self.mode = mode
        self.automation.set_safety_level(mode.safety_level)
        self._log("INFO", "System", f"Mode changed to: {mode.name}")
    
    # ============================================================
    # MAIN LOOP
    # ============================================================
    
    async def run(self):
        """Main execution loop"""
        
        self.running = True
        
        print("=" * 60)
        print(f"  {self.name} v{self.version} - Unified AI System")
        print("=" * 60)
        print(f"  Platform: {self.os_info}")
        print(f"  Mode: {self.mode.name} ({self.mode.description})")
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
                
                # Special commands
                if user_input.lower() == "help":
                    print(self._get_help_text())
                    continue
                
                if user_input.lower() == "status":
                    print(json.dumps(self.get_status(), indent=2))
                    continue
                
                if user_input.lower() == "platform":
                    print(json.dumps(self.get_platform_info(), indent=2))
                    continue
                
                if user_input.lower() == "mode":
                    print(f"Current mode: {self.mode.name}")
                    print(f"Available modes: SAFE_MODE, FULL_POWER")
                    continue
                
                # Step 2: Understand
                decision = self.understand(user_input)
                
                # Step 3 & 4: Decide & Execute
                result = await self.decide_and_execute(decision)
                
                # Step 5: Learn
                self.learn(decision, result)
                
                # Output
                if result.get("success"):
                    if result.get("output"):
                        print(result["output"])
                else:
                    error = result.get("error") or result.get("output", "Unknown error")
                    print(f"Error: {error}")
                
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
    
    def _get_help_text(self) -> str:
        """Get help text"""
        linux_extra = """
SYSTEM (Linux):
  systemctl <service> <start|stop|restart>  Manage services
  service <name> status                  Check service status
  
FULL POWER MODE:
  Set mode to FULL_POWER for elevated access
""" if self.os_info.is_linux else ""
        
        return f"""
CODE-02 Commands:
==================

COMMANDS:
  <any command>     Execute a shell command
  exec <command>     Execute a command explicitly

INSTALLATION:
  install <package>  Install a package
  pip install flask  Install Python package
{linux_extra}
SYSTEM:
  status            Show system status
  platform          Show platform information
  process           List running processes
  sysinfo           Get system information

MODES:
  mode              Show current mode

GENERAL:
  help              Show this help
  exit              Exit the system
"""


async def main():
    """Entry point"""
    system = Code02Unified()
    await system.run()


if __name__ == "__main__":
    asyncio.run(main())
