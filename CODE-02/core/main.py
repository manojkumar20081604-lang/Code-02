"""
============================================================
CODE-02 - LIVING AUTONOMOUS AI SYSTEM
============================================================
A truly intelligent, self-contained AI system that:
- Runs continuously like a living machine
- Understands, decides, executes, and learns
- Auto-installs missing dependencies
- Connects all modules seamlessly
- Works cross-platform (Windows/Linux)

Author: Manojkumar M (B.Tech AI & Data Science)
============================================================
"""

import os
import sys
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for i, p in enumerate(sys.path):
    if 'CODE-02\\core' in p or p.endswith('CODE-02/core'):
        sys.path.pop(i)
        break
sys.path[0:0] = [project_root]

try:
    import readline
except ImportError:
    pass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger("Code02")

# ================================================================
# CORE ENUMS AND DATA CLASSES
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
    MULTI_INTENT = "multi_intent"
    UNKNOWN = "unknown"


class SafetyLevel(Enum):
    SAFE = "safe"
    ELEVATED = "elevated"
    FULL = "full"


class ThreatLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class PipelineStage(Enum):
    INPUT = "input"
    UNDERSTAND = "understand"
    DECIDE = "decide"
    PLAN = "plan"
    EXECUTE = "execute"
    OUTPUT = "output"
    LEARN = "learn"


@dataclass
class Task:
    id: str
    intent: Intent
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Optional[Dict] = None
    error: Optional[str] = None


@dataclass
class ExecutionContext:
    user_input: str
    intent: Intent
    tasks: List[Task]
    current_task: int = 0
    results: List[Dict] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    pipeline_stage: PipelineStage = PipelineStage.INPUT
    start_time: datetime = field(default_factory=datetime.now)


@dataclass
class PipelineResult:
    success: bool
    output: str
    context: ExecutionContext
    error: Optional[str] = None
    tasks_executed: int = 0
    execution_time: float = 0.0


@dataclass
class CommandResult:
    success: bool
    output: str
    error: Optional[str] = None
    module: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


# ================================================================
# MEMORY SYSTEM - Long-term and Short-term memory
# ================================================================

class Memory:
    def __init__(self):
        self.short_term: Dict[str, Any] = {}
        self.long_term_file = os.path.join(project_root, "data", "memory", "long_term.jsonl")
        os.makedirs(os.path.dirname(self.long_term_file), exist_ok=True)
        self.command_patterns: Dict[str, int] = {}
        
    def store_short(self, key: str, value: Any):
        self.short_term[key] = {"value": value, "timestamp": datetime.now().isoformat()}
        if len(self.short_term) > 100:
            oldest = min(self.short_term.keys(), key=lambda k: self.short_term[k]["timestamp"])
            del self.short_term[oldest]
    
    def get_short(self, key: str) -> Optional[Any]:
        entry = self.short_term.get(key)
        return entry["value"] if entry else None
    
    def store_long(self, entry_type: str, data: Dict):
        with open(self.long_term_file, "a") as f:
            f.write(json.dumps({"type": entry_type, "data": data, "timestamp": datetime.now().isoformat()}) + "\n")
    
    def learn_pattern(self, command: str, success: bool):
        self.command_patterns[command] = self.command_patterns.get(command, 0) + (1 if success else -1)
    
    def get_successful_commands(self) -> List[str]:
        return [cmd for cmd, score in self.command_patterns.items() if score > 0]


# ================================================================
# DECISION ENGINE - Multi-intent parsing and task planning
# ================================================================

class DecisionEngine:
    def __init__(self, memory: Memory, classifier=None):
        self.memory = memory
        self.classifier = classifier
        
        self.multi_intent_patterns = [
            r'([^,]+)\s+and\s+([^,]+)',
            r'([^,]+)\s*,\s*then\s+([^,]+)',
            r'(install|scan|check|run)\s+([^,]+),\s*(install|scan|check|run)\s+([^,]+)',
        ]
        
        self.intent_keywords = {
            Intent.INSTALL: ['install', 'pip install', 'npm install', 'apt install', 'pacman', 'add', 'download'],
            Intent.SECURITY_SCAN: ['scan', 'nmap', 'port', 'vulnerability', 'phishing', 'security', 'check url', 'check domain'],
            Intent.THINK: ['think', 'analyze', 'reason', 'explain', 'how to', 'why'],
            Intent.FILE_OP: ['file', 'read', 'write', 'open', 'directory', 'folder', 'list', 'dir', 'ls'],
            Intent.SYSTEM: ['system', 'process', 'memory', 'cpu', 'status', 'uptime', 'info', 'sysinfo', 'monitor'],
            Intent.HELP: ['help', 'commands', 'what can', 'how does'],
            Intent.CHAT: ['hello', 'hi', 'hey', 'thanks', 'bye', 'goodbye', 'good morning'],
            Intent.COMMAND: ['ls', 'cd', 'cat', 'grep', 'find', 'ps', 'kill', 'rm', 'mkdir', 'touch', 'pwd', 'echo', 'chmod', 'chown', 'cp', 'mv', 'python', 'node', 'run'],
        }
    
    def parse(self, user_input: str) -> ExecutionContext:
        text = user_input.lower().strip()
        intent = self._classify_intent(text)
        
        context = ExecutionContext(
            user_input=user_input,
            intent=intent,
            tasks=[],
            pipeline_stage=PipelineStage.INPUT
        )
        
        if intent == Intent.UNKNOWN:
            return context
        
        if intent == Intent.SECURITY_SCAN and ' and ' in text:
            intents = self._extract_multi_intents(text)
            for idx, (intent_type, action) in enumerate(intents):
                task = Task(
                    id=f"task_{idx}",
                    intent=intent_type,
                    action=action,
                    params=self._extract_params(intent_type, action)
                )
                context.tasks.append(task)
        else:
            task = Task(
                id="task_0",
                intent=intent,
                action=user_input,
                params=self._extract_params(intent, user_input)
            )
            context.tasks.append(task)
        
        return context
    
    def _classify_intent(self, text: str) -> Intent:
        if self.classifier:
            try:
                result = self.classifier.classify(text)
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
                return intent_map.get(result.get("intent", ""), Intent.UNKNOWN)
            except:
                pass
        
        for intent, keywords in self.intent_keywords.items():
            if any(text.startswith(kw) or kw in text for kw in keywords):
                return intent
        return Intent.UNKNOWN
    
    def _extract_multi_intents(self, text: str) -> List[tuple]:
        results = []
        parts = re.split(r'\s+and\s+', text)
        for part in parts:
            part = part.strip()
            if 'install' in part:
                results.append((Intent.INSTALL, part))
            elif 'scan' in part or 'check' in part:
                results.append((Intent.SECURITY_SCAN, part))
            elif any(kw in part for kw in ['run', 'execute', 'do']):
                results.append((Intent.COMMAND, part))
            else:
                results.append((Intent.COMMAND, part))
        return results
    
    def _extract_params(self, intent: Intent, text: str) -> Dict[str, Any]:
        params = {"raw": text}
        
        urls = re.findall(r'https?://\S+', text)
        if urls:
            params["url"] = urls[0]
        
        ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', text)
        if ips:
            params["ip"] = ips[0]
        
        ports = re.findall(r'port[:\s]+(\d+)', text)
        if ports:
            params["port"] = int(ports[0])
        
        packages = re.findall(r'(?:install|add)\s+(\S+)', text.lower())
        if packages:
            params["package"] = packages[0]
        
        return params


# ================================================================
# SAFETY LAYER - Command validation and confirmation
# ================================================================

class SafetyLayer:
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf\s+/', ThreatLevel.CRITICAL, "Recursive root deletion"),
        (r'format\s+[a-z]:', ThreatLevel.CRITICAL, "Drive format"),
        (r'del\s+/[sq]\s+/f\s+/s', ThreatLevel.CRITICAL, "Recursive force delete"),
        (r'>\s*/dev/sd', ThreatLevel.CRITICAL, "Direct device write"),
        (r'mkfs\s+', ThreatLevel.CRITICAL, "Filesystem creation"),
        (r'dd\s+.*of=/dev/', ThreatLevel.CRITICAL, "Direct device copy"),
        (r':(){.*:|:&};:', ThreatLevel.CRITICAL, "Fork bomb"),
        (r'chmod\s+-R\s+777\s+/', ThreatLevel.HIGH, "World-writable root"),
        (r'wget.*\|\s*sh', ThreatLevel.HIGH, "Pipe to shell download"),
        (r'curl.*\|\s*sh', ThreatLevel.HIGH, "Pipe to shell download"),
        (r'shutdown|reboot|init\s+0', ThreatLevel.HIGH, "System shutdown"),
        (r'kill\s+-9\s+1', ThreatLevel.HIGH, "Kill init process"),
        (r'>\s*/etc/', ThreatLevel.HIGH, "Write to system config"),
        (r'eval\s+.*\$', ThreatLevel.MEDIUM, "Eval with variable"),
        (r'`.*`', ThreatLevel.MEDIUM, "Command substitution"),
    ]
    
    def __init__(self, safety_level: SafetyLevel):
        self.safety_level = safety_level
        self.pending_confirmations: Dict[str, Dict] = {}
    
    def check(self, command: str) -> tuple[bool, ThreatLevel, str]:
        for pattern, level, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                if level.value >= ThreatLevel.HIGH.value:
                    return False, level, description
                elif self.safety_level == SafetyLevel.SAFE:
                    return False, level, description
        return True, ThreatLevel.NONE, "OK"
    
    def needs_confirmation(self, command: str) -> bool:
        _, level, _ = self.check(command)
        return level.value >= ThreatLevel.MEDIUM.value


# ================================================================
# AUTONOMOUS EXECUTOR - Handles retries and auto-install
# ================================================================

class AutonomousExecutor:
    def __init__(self, automation, installer, safety: SafetyLayer):
        self.automation = automation
        self.installer = installer
        self.safety = safety
        self.retry_count = 2
    
    def execute(self, task: Task) -> CommandResult:
        if task.intent == Intent.COMMAND:
            return self._execute_command(task)
        elif task.intent == Intent.INSTALL:
            return self._execute_install(task)
        elif task.intent == Intent.SECURITY_SCAN:
            return self._execute_security(task)
        elif task.intent == Intent.SYSTEM:
            return self._execute_system(task)
        elif task.intent == Intent.FILE_OP:
            return self._execute_file(task)
        else:
            return CommandResult(False, "", f"Unknown intent: {task.intent}", "executor")
    
    def _execute_command(self, task: Task) -> CommandResult:
        command = task.action
        safe, level, desc = self.safety.check(command)
        
        if not safe:
            return CommandResult(False, "", f"Blocked: {desc}", "safety")
        
        result = self.automation.execute(command)
        
        if not result.success and "not found" in result.stderr.lower():
            tool = self._extract_tool_name(command)
            if tool and self.installer:
                install_result = self.installer.install(tool)
                if install_result.success:
                    result = self.automation.execute(command)
        
        return CommandResult(
            success=result.success,
            output=result.stdout,
            error=result.stderr if not result.success else None,
            module="automation"
        )
    
    def _execute_install(self, task: Task) -> CommandResult:
        package = task.params.get("package") or self._extract_package_name(task.action)
        
        if not package:
            return CommandResult(False, "", "No package specified", "installer")
        
        if self.installer.check_dependency(package):
            return CommandResult(True, f"{package} is already installed", "installer")
        
        result = self.installer.install(package)
        return CommandResult(
            success=result.success,
            output=f"Installed {package}" if result.success else "",
            error=result.stderr if not result.success else None,
            module="installer"
        )
    
    def _execute_security(self, task: Task) -> CommandResult:
        from core.cybersecurity import get_security
        security = get_security()
        
        if task.params.get("url"):
            check = security.check_url_safety(task.params["url"])
            if check["safe"]:
                return CommandResult(True, f"URL {task.params['url']} is safe", "security")
            else:
                return CommandResult(False, "", f"Threat: {check['threat_level']}", "security")
        
        if task.params.get("ip"):
            ip = task.params["ip"]
            if task.params.get("port"):
                result = security.scan_port(ip, task.params["port"])
                return CommandResult(True, f"Port {result.port}: {result.status}", "security")
            else:
                results = security.scan_common_ports(ip)
                open_ports = [r for r in results if r.status == "open"]
                output = f"Open ports on {ip}: " + ", ".join([str(r.port) for r in open_ports]) if open_ports else "No open ports"
                return CommandResult(True, output, "security")
        
        return CommandResult(True, "Security tools ready", "security")
    
    def _execute_system(self, task: Task) -> CommandResult:
        text = task.action.lower()
        
        if "process" in text or "ps" in text:
            processes = self.automation.get_process_list()[:10]
            output = "\n".join([f"{p['pid']}: {p['name']}" for p in processes])
            return CommandResult(True, output, "system")
        
        if "info" in text or "sysinfo" in text:
            info = self.automation.get_system_info()
            return CommandResult(True, json.dumps(info, indent=2), "system")
        
        return CommandResult(True, "System commands: process, info, status", "system")
    
    def _execute_file(self, task: Task) -> CommandResult:
        text = task.action.lower()
        
        if "ls" in text or "dir" in text or "list" in text:
            result = self.automation.execute("dir" if os.name == "nt" else "ls -la")
            return CommandResult(result.success, result.stdout, result.stderr, "automation")
        
        return CommandResult(True, "File operations: ls, dir, list", "automation")
    
    def _extract_tool_name(self, command: str) -> Optional[str]:
        parts = command.split()
        return parts[0] if parts else None
    
    def _extract_package_name(self, text: str) -> Optional[str]:
        match = re.search(r'(?:install|add)\s+(\S+)', text.lower())
        return match.group(1) if match else None


# ================================================================
# MAIN CODE-02 SYSTEM ENGINE
# ================================================================

class Code02System:
    VERSION = "3.1-LIVING"
    
    def __init__(self):
        self.name = "CODE-02"
        self.start_time = datetime.now()
        self.running = False
        
        self.platform = self._detect_platform()
        self.safety_level = SafetyLevel.FULL if self.platform == "linux" else SafetyLevel.SAFE
        
        self.memory = Memory()
        self.modules = self._init_modules()
        self.safety = SafetyLayer(self.safety_level)
        self.decision_engine = DecisionEngine(self.memory, self.modules.get("classifier"))
        self.executor = AutonomousExecutor(
            self.modules.get("automation"),
            self.modules.get("installer"),
            self.safety
        )
        
        self.config = {
            "auto_install": True,
            "confirm_dangerous": True,
            "learn_from_mistakes": True,
            "retry_on_failure": True,
        }
        
        logger.info(f"{self.name} v{self.VERSION} INITIALIZED")
        logger.info(f"Platform: {self.platform} | Safety: {self.safety_level.name}")
    
    def _detect_platform(self) -> str:
        if os.name == "nt":
            return "windows"
        elif os.name == "posix":
            if os.path.exists("/etc/arch-release"):
                return "linux-arch"
            elif os.path.exists("/etc/debian_version"):
                return "linux-debian"
            return "linux"
        return "unknown"
    
    def _init_modules(self) -> Dict[str, Any]:
        modules = {}
        
        try:
            from core.automation import get_automation, SafetyLevel as AutoSafety
            safety = AutoSafety.SAFE if self.safety_level == SafetyLevel.SAFE else AutoSafety.ELEVATED
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
            from core.datascience import get_classifier
            modules["classifier"] = get_classifier()
            logger.info("Module loaded: classifier")
        except Exception as e:
            logger.error(f"Failed to load classifier: {e}")
            modules["classifier"] = None
        
        return modules
    
    # ================================================================
    # MAIN EXECUTION LOOP - Listen → Understand → Decide → Execute → Learn
    # ================================================================
    
    def run(self):
        self.running = True
        
        self._print_banner()
        
        while self.running:
            try:
                user_input = input(f"{self.name}> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self._shutdown()
                    break
                
                if user_input.lower() == 'help':
                    print(self._get_help())
                    continue
                
                if user_input.lower() == 'status':
                    print(json.dumps(self._get_status(), indent=2))
                    continue
                
                if user_input.lower() == 'memory':
                    print(f"Short-term: {len(self.memory.short_term)} items")
                    print(f"Successful patterns: {len(self.memory.get_successful_commands())}")
                    continue
                
                result = self._pipeline(user_input)
                self._output_result(result)
                
            except KeyboardInterrupt:
                print("\n(Use 'exit' to quit)")
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Pipeline error: {e}")
                print(f"Error: {e}")
        
        self._shutdown()
    
    def _pipeline(self, user_input: str) -> PipelineResult:
        start = datetime.now()
        
        ctx = ExecutionContext(
            user_input=user_input,
            intent=Intent.UNKNOWN,
            tasks=[],
            start_time=start
        )
        
        ctx.pipeline_stage = PipelineStage.UNDERSTAND
        ctx = self.decision_engine.parse(user_input)
        ctx.intent = ctx.tasks[0].intent if ctx.tasks else Intent.UNKNOWN
        
        logger.info(f"Intent: {ctx.intent.value} | Tasks: {len(ctx.tasks)}")
        
        ctx.pipeline_stage = PipelineStage.EXECUTE
        for idx, task in enumerate(ctx.tasks):
            ctx.current_task = idx
            task.status = "executing"
            
            if task.intent == Intent.CHAT:
                result = self._handle_chat(task.action)
            elif task.intent == Intent.HELP:
                result = CommandResult(True, self._get_help(), "system")
            elif task.intent == Intent.THINK:
                result = self._handle_think(task.action)
            else:
                result = self.executor.execute(task)
            
            task.result = {"success": result.success, "output": result.output}
            task.error = result.error
            task.status = "completed" if result.success else "failed"
            
            ctx.results.append({
                "task_id": task.id,
                "success": result.success,
                "output": result.output,
                "error": result.error
            })
            
            self.memory.learn_pattern(task.action, result.success)
        
        ctx.pipeline_stage = PipelineStage.LEARN
        self.memory.store_long("interaction", {
            "input": user_input,
            "intent": ctx.intent.value,
            "results": ctx.results
        })
        
        combined_output = "\n".join([r["output"] for r in ctx.results if r.get("output")])
        combined_error = "\n".join([r["error"] for r in ctx.results if r.get("error")])
        
        execution_time = (datetime.now() - start).total_seconds()
        
        return PipelineResult(
            success=all(r["success"] for r in ctx.results),
            output=combined_output,
            context=ctx,
            error=combined_error if combined_error else None,
            tasks_executed=len(ctx.tasks),
            execution_time=execution_time
        )
    
    def _handle_chat(self, text: str) -> CommandResult:
        text = text.lower()
        
        if any(kw in text for kw in ['hello', 'hi', 'hey']):
            return CommandResult(True, "Hello! I'm CODE-02, your autonomous AI. What shall we accomplish today?", "brain")
        if 'thanks' in text:
            return CommandResult(True, "You're welcome! Let me know if you need anything else.", "brain")
        if 'bye' in text:
            return CommandResult(True, "Goodbye! It was great working with you.", "brain")
        
        return CommandResult(True, "I'm CODE-02. Type 'help' for available commands.", "brain")
    
    def _handle_think(self, text: str) -> CommandResult:
        problem = text.replace('think', '').replace('about', '').strip()
        
        reasoning = f"""
ANALYZING: "{problem}"

1. UNDERSTANDING
   - Breaking down the problem
   - Identifying key components

2. ANALYSIS
   - Evaluating possible approaches
   - Checking dependencies

3. REASONING
   - Drawing logical conclusions
   - Identifying constraints

4. RECOMMENDATION
   - Next steps for success

[LLM integration available for deeper reasoning]
"""
        return CommandResult(True, reasoning.strip(), "brain")
    
    def _output_result(self, result: PipelineResult):
        if result.success and result.output:
            print(result.output)
        elif not result.success and result.error:
            print(f"Error: {result.error}")
        elif not result.output:
            print("Command completed.")
        
        print(f"\n[{result.tasks_executed} task(s) | {result.execution_time:.2f}s]")
    
    def _print_banner(self):
        print(f"""
+============================================================+
|                  CODE-02 v{self.VERSION}                       |
|              LIVING AUTONOMOUS AI SYSTEM                   |
+============================================================+
|  Platform: {self.platform:<15} Safety: {self.safety_level.name:<15}  |
|  Modules: {', '.join(k for k, v in self.modules.items() if v)[:43]}
|  Memory: Active | Learning: Enabled                         |
+============================================================+
|  LOOP: listen -> understand -> decide -> execute -> learn  |
+============================================================+
""")
    
    def _shutdown(self):
        uptime = datetime.now() - self.start_time
        print(f"\nShutting down... Uptime: {str(uptime).split('.')[0]}")
        self.running = False
        logger.info(f"{self.name} stopped")
    
    def _get_status(self) -> Dict[str, Any]:
        uptime = datetime.now() - self.start_time
        return {
            "name": self.name,
            "version": self.VERSION,
            "platform": self.platform,
            "safety_level": self.safety_level.name,
            "uptime_seconds": uptime.total_seconds(),
            "modules": [k for k, v in self.modules.items() if v],
            "memory_items": len(self.memory.short_term),
            "patterns_learned": len(self.memory.command_patterns)
        }
    
    def _get_help(self) -> str:
        linux_extra = """
LINUX-SPECIFIC:
  systemctl start nginx    Service management
  service ssh status       Check service status""" if self.platform == "linux" else ""
        
        return f"""
CODE-02 Commands:
==================

AUTOMATION:
  <any shell command>       Execute command (ls, cd, cat, grep, etc.)
  ls, ps, pwd, echo        Standard commands

INSTALLATION:
  install <package>        Install package (auto-detects manager)
  pip install flask        Python package
  npm install react        Node package

SECURITY:
  scan <ip>                Scan IP for open ports
  scan <ip> port 80        Scan specific port
  check <url>              Check URL for threats{linux_extra}

INTELLIGENCE:
  think about <topic>      Analyze a problem
  help                    Show this help

SYSTEM:
  status                  System information
  memory                  Memory statistics
  exit                    Quit

MULTI-INTENT EXAMPLES:
  install nmap and scan 192.168.1.1
  install requests and check http://example.com

NOTE: System auto-installs missing tools and learns patterns.
"""


# ================================================================
# ENTRY POINT
# ================================================================

def main():
    try:
        system = Code02System()
        system.run()
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
