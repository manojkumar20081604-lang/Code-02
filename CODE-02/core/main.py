"""
============================================================
CODE-02 MAIN SYSTEM - Complete AI Controller
============================================================
A unified, autonomous AI system that:
- Runs continuously
- Understands commands intelligently
- Routes tasks correctly
- Executes actions automatically
- Installs dependencies when needed
- Works on Windows and Linux

Author: Manojkumar M (B.Tech AI & Data Science)
============================================================
"""

import asyncio
import logging
import sys
import os
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for i, p in enumerate(sys.path):
    if 'CODE-02\\core' in p or p.endswith('CODE-02/core'):
        sys.path.pop(i)
        break
sys.path[0:0] = [project_root]

try:
    import readline  # Unix only
except ImportError:
    pass  # Windows doesn't have readline
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("Code02Main")

# ================================================================
# ENUMS AND DATACLASSES
# ================================================================

class Intent(Enum):
    COMMAND = "command"
    INSTALL = "install"
    SECURITY_SCAN = "security_scan"
    THINK = "think"
    FILE_OP = "file_operation"
    SYSTEM = "system"
    CHAT = "chat"
    HELP = "help"
    UNKNOWN = "unknown"


class Module(Enum):
    AUTOMATION = "automation"
    INSTALLER = "installer"
    SECURITY = "security"
    BRAIN = "brain"
    MEMORY = "memory"


class SafetyLevel(Enum):
    SAFE = "safe"
    ELEVATED = "elevated"
    FULL = "full"


@dataclass
class CommandResult:
    success: bool
    output: str
    error: Optional[str] = None
    module: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ================================================================
# MAIN CODE-02 SYSTEM
# ================================================================

class Code02System:
    """
    CODE-02 - Unified Autonomous AI System
    
    Continuous loop: listen → understand → decide → execute → learn
    """
    
    def __init__(self):
        self.name = "CODE-02"
        self.version = "3.0"
        self.running = False
        self.start_time = datetime.now()
        
        # Platform detection
        self.platform = self._detect_platform()
        
        # Safety level based on platform
        self.safety_level = SafetyLevel.FULL if self.platform == "linux" else SafetyLevel.SAFE
        
        # Initialize all modules
        self.modules = self._init_modules()
        
        # Context and memory
        self.context: Dict[str, Any] = {}
        self.conversation_history: List[Dict] = []
        self.command_history: List[Dict] = []
        
        # Configuration
        self.config = {
            "auto_install": True,
            "confirm_dangerous": True,
            "log_level": "INFO"
        }
        
        # Register command handlers
        self.handlers: Dict[Intent, Callable] = {
            Intent.COMMAND: self._handle_command,
            Intent.INSTALL: self._handle_install,
            Intent.SECURITY_SCAN: self._handle_security,
            Intent.THINK: self._handle_think,
            Intent.FILE_OP: self._handle_file,
            Intent.SYSTEM: self._handle_system,
            Intent.CHAT: self._handle_chat,
            Intent.HELP: self._handle_help,
            Intent.UNKNOWN: self._handle_unknown,
        }
        
        logger.info(f"{self.name} v{self.version} initialized")
        logger.info(f"Platform: {self.platform} | Safety: {self.safety_level.name}")
    
    # ============================================================
    # INITIALIZATION
    # ============================================================
    
    def _detect_platform(self) -> str:
        """Detect current platform"""
        if os.name == "nt":
            return "windows"
        elif os.name == "posix":
            if os.path.exists("/etc/arch-release"):
                return "linux-arch"
            elif os.path.exists("/etc/debian_version"):
                return "linux-debian"
            else:
                return "linux"
        return "unknown"
    
    def _init_modules(self) -> Dict[str, Any]:
        """Initialize all system modules"""
        modules = {}
        
        # Import and initialize modules
        try:
            from core.automation import get_automation, SafetyLevel as AutoSafety
            
            safety = AutoSafety.SAFE
            if self.safety_level == SafetyLevel.FULL:
                safety = AutoSafety.ELEVATED
            elif self.safety_level == SafetyLevel.SAFE:
                safety = AutoSafety.SAFE
            
            modules["automation"] = get_automation(safety)
            logger.info("Module loaded: automation")
        except Exception as e:
            logger.error(f"Failed to load automation: {e}")
            modules["automation"] = None
        
        try:
            from core.installer import get_installer
            modules["installer"] = get_installer()
            logger.info("Module loaded: installer")
        except Exception as e:
            logger.error(f"Failed to load installer: {e}")
            modules["installer"] = None
        
        try:
            from core.cybersecurity import get_security
            modules["security"] = get_security()
            logger.info("Module loaded: security")
        except Exception as e:
            logger.error(f"Failed to load security: {e}")
            modules["security"] = None
        
        try:
            from core.datascience import get_router
            modules["router"] = get_router()
            logger.info("Module loaded: router")
        except Exception as e:
            logger.error(f"Failed to load router: {e}")
            modules["router"] = None
        
        try:
            from core.datascience import get_classifier
            modules["classifier"] = get_classifier()
            logger.info("Module loaded: classifier")
        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")
            modules["classifier"] = None
        
        return modules
    
    # ============================================================
    # MAIN LOOP
    # ============================================================
    
    def run(self):
        """Main execution loop"""
        
        self.running = True
        
        print("\n" + "=" * 60)
        print(f"  {self.name} v{self.version} - Autonomous AI System")
        print("=" * 60)
        print(f"  Platform: {self.platform}")
        print(f"  Safety Level: {self.safety_level.name}")
        print(f"  Modules: {', '.join(k for k, v in self.modules.items() if v)}")
        print("=" * 60)
        print("\nType 'help' for commands, 'exit' to quit.\n")
        
        logger.info(f"{self.name} started")
        
        while self.running:
            try:
                # Get user input
                user_input = input(f"{self.name}> ").strip()
                
                # Handle empty input
                if not user_input:
                    continue
                
                # Handle exit commands
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("Shutting down...")
                    break
                
                # Handle special commands
                if user_input.lower() == 'help':
                    print(self._get_help_text())
                    continue
                
                if user_input.lower() == 'status':
                    print(json.dumps(self._get_status(), indent=2))
                    continue
                
                if user_input.lower() == 'history':
                    self._show_history()
                    continue
                
                if user_input.lower() == 'platform':
                    print(f"Platform: {self.platform}")
                    print(f"Safety: {self.safety_level.name}")
                    continue
                
                # Process input through AI pipeline
                result = self._process(user_input)
                
                # Output result
                if result.success:
                    if result.output:
                        print(result.output)
                else:
                    print(f"Error: {result.error}")
                
                # Log to history
                self._log_interaction(user_input, result)
                
            except KeyboardInterrupt:
                print("\n(Use 'exit' to quit)")
                continue
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                print(f"Error: {e}")
        
        self.running = False
        logger.info(f"{self.name} stopped")
    
    # ============================================================
    # PROCESSING PIPELINE
    # ============================================================
    
    def _process(self, user_input: str) -> CommandResult:
        """
        Main processing pipeline:
        1. Understand (classify intent)
        2. Decide (route to module)
        3. Execute (run action)
        4. Learn (store result)
        """
        
        logger.info(f"Processing: {user_input[:50]}...")
        
        # Step 1: Understand - Classify intent
        intent = self._classify_intent(user_input)
        logger.info(f"Intent: {intent.name}")
        
        # Step 2: Execute based on intent
        handler = self.handlers.get(intent, self._handle_unknown)
        
        try:
            result = handler(user_input)
            
            # Step 3: Learn - Store in context
            self.context["last_result"] = result
            self.context["last_intent"] = intent.name
            
            return result
            
        except Exception as e:
            logger.error(f"Execution error: {e}")
            return CommandResult(
                success=False,
                output="",
                error=str(e),
                module="system"
            )
    
    def _classify_intent(self, user_input: str) -> Intent:
        """Classify user intent using ML classifier or rules"""
        
        text = user_input.lower().strip()
        
        # Use ML classifier if available
        if self.modules.get("classifier"):
            try:
                result = self.modules["classifier"].classify(user_input)
                intent_str = result.get("intent", "unknown")
                
                # Map classifier intents to our intents
                intent_map = {
                    "command": Intent.COMMAND,
                    "install": Intent.INSTALL,
                    "security_scan": Intent.SECURITY_SCAN,
                    "network": Intent.COMMAND,
                    "file": Intent.FILE_OP,
                    "system": Intent.SYSTEM,
                    "think": Intent.THINK,
                    "help": Intent.HELP,
                    "chat": Intent.CHAT,
                }
                
                return intent_map.get(intent_str, Intent.UNKNOWN)
            except Exception as e:
                logger.warning(f"Classifier error: {e}")
        
        # Fallback to rule-based classification
        if any(text.startswith(cmd) for cmd in ['ls', 'cd', 'cat', 'grep', 'find', 'ps', 'kill', 'rm', 'mkdir', 'touch', 'pwd', 'echo', 'chmod', 'chown', 'cp', 'mv']):
            return Intent.COMMAND
        
        if any(text.startswith(cmd) for cmd in ['install', 'pip install', 'npm install', 'apt install', 'pacman']):
            return Intent.INSTALL
        
        if any(kw in text for kw in ['scan', 'nmap', 'port', 'vulnerability', 'phishing', 'security']):
            return Intent.SECURITY_SCAN
        
        if any(kw in text for kw in ['think', 'analyze', 'reason', 'explain']):
            return Intent.THINK
        
        if any(kw in text for kw in ['file', 'read', 'write', 'open', 'directory']):
            return Intent.FILE_OP
        
        if any(kw in text for kw in ['system', 'process', 'memory', 'cpu', 'status', 'uptime']):
            return Intent.SYSTEM
        
        if any(kw in text for kw in ['help', 'how to', 'what can']):
            return Intent.HELP
        
        if any(kw in text for kw in ['hello', 'hi', 'hey', 'thanks', 'bye']):
            return Intent.CHAT
        
        return Intent.UNKNOWN
    
    # ============================================================
    # INTENT HANDLERS
    # ============================================================
    
    def _handle_command(self, user_input: str) -> CommandResult:
        """Handle shell commands"""
        
        # Check for multi-part commands
        if " and " in user_input.lower():
            # Split compound commands
            parts = user_input.lower().split(" and ")
            outputs = []
            
            for part in parts:
                result = self._execute_single_command(part.strip())
                outputs.append(result)
            
            combined_output = "\n".join([o.output for o in outputs if o.success])
            combined_error = "\n".join([o.error for o in outputs if o.error])
            
            return CommandResult(
                success=all(o.success for o in outputs),
                output=combined_output,
                error=combined_error if combined_error else None,
                module="automation"
            )
        
        return self._execute_single_command(user_input)
    
    def _execute_single_command(self, command: str) -> CommandResult:
        """Execute a single command"""
        
        automation = self.modules.get("automation")
        if not automation:
            return CommandResult(False, "", "Automation module not loaded", "automation")
        
        # Check command safety
        security = self.modules.get("security")
        if security:
            safety_check = security.check_command_safety(command)
            
            if safety_check.threat_level.value >= 3:  # HIGH or CRITICAL
                return CommandResult(
                    success=False,
                    output="",
                    error=f"Dangerous command blocked: {safety_check.indicators[0] if safety_check.indicators else 'Unknown'}",
                    module="security"
                )
        
        # Execute command
        result = automation.execute(command)
        
        return CommandResult(
            success=result.success,
            output=result.stdout,
            error=result.stderr if not result.success else None,
            module="automation",
            metadata={"exit_code": result.exit_code}
        )
    
    def _handle_install(self, user_input: str) -> CommandResult:
        """Handle package installation with auto-detection"""
        
        installer = self.modules.get("installer")
        if not installer:
            return CommandResult(False, "", "Installer module not loaded", "installer")
        
        # Extract package name
        package = self._extract_package_name(user_input)
        
        if not package:
            return CommandResult(False, "", "No package specified", "installer")
        
        # Check if already installed
        if installer.check_dependency(package):
            return CommandResult(
                success=True,
                output=f"{package} is already installed",
                module="installer"
            )
        
        # Install package
        result = installer.install(package)
        
        if result.success:
            return CommandResult(
                success=True,
                output=f"Successfully installed {package} using {result.manager}",
                module="installer"
            )
        else:
            return CommandResult(
                success=False,
                output="",
                error=f"Failed to install {package}: {result.stderr}",
                module="installer"
            )
    
    def _handle_security(self, user_input: str) -> CommandResult:
        """Handle security operations"""
        
        security = self.modules.get("security")
        if not security:
            return CommandResult(False, "", "Security module not loaded", "security")
        
        text = user_input.lower()
        
        # URL check
        if "url" in text or "http" in text:
            import re
            urls = re.findall(r'https?://\S+', user_input)
            
            if urls:
                url = urls[0]
                check = security.check_url_safety(url)
                
                if check["safe"]:
                    return CommandResult(
                        success=True,
                        output=f"URL {url} appears safe (Threat Level: {check['threat_level']})",
                        module="security"
                    )
                else:
                    return CommandResult(
                        success=False,
                        output="",
                        error=f"Threat detected! Level: {check['threat_level']}\nIndicators: {', '.join(check['indicators'])}",
                        module="security"
                    )
        
        # IP/Port scan
        if "scan" in text or "port" in text:
            import re
            
            # Extract IP
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', user_input)
            
            if ips:
                ip = ips[0]
                
                # Extract port if present
                ports = re.findall(r'port[:\s]+(\d+)', text)
                
                if ports:
                    port = int(ports[0])
                    result = security.scan_port(ip, port)
                    
                    return CommandResult(
                        success=True,
                        output=f"Port {port} on {ip}: {result.status.upper()} ({result.service})",
                        module="security"
                    )
                else:
                    # Scan common ports
                    results = security.scan_common_ports(ip)
                    open_ports = [r for r in results if r.status == "open"]
                    
                    if open_ports:
                        output = f"Open ports on {ip}:\n"
                        output += "\n".join([f"  {r.port}/tcp - {r.service}" for r in open_ports])
                        return CommandResult(True, output, module="security")
                    else:
                        return CommandResult(True, f"No open ports found on {ip}", module="security")
        
        return CommandResult(True, "Security tools ready. Try 'scan <ip>' or 'check <url>'", module="security")
    
    def _handle_think(self, user_input: str) -> CommandResult:
        """Handle thinking/reasoning requests"""
        
        problem = user_input.replace("think", "").replace("about", "").strip()
        
        if not problem:
            return CommandResult(True, "What would you like me to think about?", module="brain")
        
        # Simple reasoning (placeholder for LLM)
        reasoning = f"""
Analyzing: "{problem}"

Step 1: Understanding the Goal
- Break down the problem into components
- Identify key factors

Step 2: Analysis
- Consider possible approaches
- Evaluate constraints

Step 3: Reasoning
- Draw logical conclusions
- Identify dependencies

Step 4: Recommendation
- Suggest actionable next steps

[Connect LLM (Ollama/OpenAI) for advanced reasoning]
"""
        
        return CommandResult(True, reasoning.strip(), module="brain")
    
    def _handle_file(self, user_input: str) -> CommandResult:
        """Handle file operations"""
        
        automation = self.modules.get("automation")
        if not automation:
            return CommandResult(False, "", "Automation module not loaded", "automation")
        
        text = user_input.lower()
        
        # Read file
        if "read" in text or "show" in text or "cat" in text:
            import re
            paths = re.findall(r'(?:file|/)[^\s]+', user_input)
            
            if paths:
                path = paths[0].strip()
                content = automation.read_file(path)
                
                if "Error" not in content:
                    return CommandResult(True, content[:1000], module="automation")
                else:
                    return CommandResult(False, "", content, module="automation")
        
        # List directory
        if "list" in text or "dir" in text or "ls" in text:
            result = automation.execute("ls -la")
            return CommandResult(result.success, result.stdout, result.stderr, "automation")
        
        return CommandResult(True, "File operations: read <path>, ls, list <dir>", module="automation")
    
    def _handle_system(self, user_input: str) -> CommandResult:
        """Handle system operations"""
        
        text = user_input.lower()
        
        if "status" in text:
            return CommandResult(
                success=True,
                output=json.dumps(self._get_status(), indent=2),
                module="system"
            )
        
        if "uptime" in text:
            uptime = datetime.now() - self.start_time
            return CommandResult(
                success=True,
                output=f"System uptime: {str(uptime).split('.')[0]}",
                module="system"
            )
        
        if "process" in text or "ps" in text:
            automation = self.modules.get("automation")
            if automation:
                processes = automation.get_process_list()[:10]
                output = "Running processes:\n"
                output += "\n".join([f"  {p['pid']}: {p['name']}" for p in processes])
                return CommandResult(True, output, module="automation")
        
        if "info" in text or "sysinfo" in text:
            automation = self.modules.get("automation")
            if automation:
                info = automation.get_system_info()
                return CommandResult(True, json.dumps(info, indent=2), module="automation")
        
        return CommandResult(True, "System commands: status, uptime, process, info", module="system")
    
    def _handle_chat(self, user_input: str) -> CommandResult:
        """Handle casual conversation"""
        
        text = user_input.lower()
        
        responses = {
            "hello": "Hello! I'm CODE-02, your autonomous AI assistant. How can I help you today?",
            "hi": "Hi there! I'm CODE-02. Ready to assist with commands, installations, or security tasks.",
            "hey": "Hey! What can I do for you?",
            "thanks": "You're welcome! Let me know if you need anything else.",
            "bye": "Goodbye! It was great chatting with you.",
        }
        
        for key, response in responses.items():
            if key in text:
                return CommandResult(True, response, module="brain")
        
        return CommandResult(True, "I'm CODE-02, your AI assistant. Type 'help' for available commands.", module="brain")
    
    def _handle_help(self, user_input: str) -> CommandResult:
        """Handle help requests"""
        return CommandResult(True, self._get_help_text(), module="system")
    
    def _handle_unknown(self, user_input: str) -> CommandResult:
        """Handle unknown commands"""
        return CommandResult(
            True,
            f"I understand '{user_input}', but I'm not sure how to help with that.\n"
            f"Type 'help' for available commands.",
            module="brain"
        )
    
    # ============================================================
    # UTILITY METHODS
    # ============================================================
    
    def _extract_package_name(self, text: str) -> Optional[str]:
        """Extract package name from install command"""
        
        import re
        
        # Match patterns like "install <package>" or "pip install <package>"
        patterns = [
            r'(?:install|add)\s+(\S+)',
            r'(pip|npm|apt|pacman)\s+(?:install\s+)?(\S+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                # Return second group if present (for "pip install pkg")
                return match.group(2) if match.lastindex == 2 else match.group(1)
        
        return None
    
    def _get_status(self) -> Dict[str, Any]:
        """Get system status"""
        
        uptime = datetime.now() - self.start_time
        
        return {
            "name": self.name,
            "version": self.version,
            "platform": self.platform,
            "safety_level": self.safety_level.name,
            "uptime_seconds": uptime.total_seconds(),
            "modules_loaded": [k for k, v in self.modules.items() if v],
            "commands_executed": len(self.command_history),
            "conversations": len(self.conversation_history)
        }
    
    def _get_help_text(self) -> str:
        """Get help text"""
        
        linux_extra = """
LINUX-SPECIFIC:
  systemctl <svc> start|stop|restart   Manage services
  service <name> status              Check service status
""" if self.platform.startswith("linux") else ""
        
        return f"""
CODE-02 Commands:
====================

AUTOMATION:
  <shell command>              Execute a shell command
  ls, cd, cat, grep          Standard commands
  mkdir, touch, rm            File operations

INSTALLATION:
  install <package>            Install a package
  pip install flask           Install Python package
  npm install react           Install Node package

SECURITY:
  scan <ip>                   Scan IP for open ports
  scan <ip> port <n>         Scan specific port
  check <url>                  Check URL for threats{linux_extra}

SYSTEM:
  status                      System status
  uptime                      System uptime
  process                     List processes
  info                        System information

INTELLIGENCE:
  think <problem>            Analyze a problem
  help                       Show this help

EXAMPLES:
  install nmap
  scan 192.168.1.1
  check http://example.com
  think about building a web scraper
"""
    
    def _show_history(self):
        """Show command history"""
        
        if not self.command_history:
            print("No commands in history.")
            return
        
        print(f"\nLast {min(10, len(self.command_history))} commands:")
        print("-" * 50)
        
        for i, entry in enumerate(self.command_history[-10:], 1):
            status = "OK" if entry["success"] else "FAIL"
            print(f"{i}. [{status}] {entry['command'][:50]}")
    
    def _log_interaction(self, user_input: str, result: CommandResult):
        """Log interaction to history"""
        
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "success": result.success,
            "module": result.module
        })
        
        self.command_history.append({
            "timestamp": datetime.now().isoformat(),
            "command": user_input,
            "success": result.success,
            "module": result.module,
            "output_length": len(result.output)
        })
        
        # Keep history manageable
        if len(self.command_history) > 100:
            self.command_history = self.command_history[-100:]


# ================================================================
# MAIN ENTRY POINT
# ================================================================

def main():
    """Main entry point"""
    
    try:
        system = Code02System()
        system.run()
    except KeyboardInterrupt:
        print("\n\nInterrupted. Goodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
