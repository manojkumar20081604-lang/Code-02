"""
============================================================
CODE-02 - INTELLIGENT AUTONOMOUS AI SYSTEM v4.0
============================================================
A truly intelligent AI that:
- THINKS: Understands context and plans
- DECIDES: Creates execution strategies
- ACTS: Executes tasks autonomously
- LEARNS: Improves from every interaction
- ADAPTS: Handles errors and self-corrects

This is not a script runner - it's a thinking machine.

Author: Manojkumar M (B.Tech AI & Data Science)
============================================================
"""

import os
import sys
import json
import logging
import re
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union, Type
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict

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
# CORE ENUMS - Define system states and types
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
    CODE_GENERATION = "code_generation"
    MULTI_STEP = "multi_step"
    WORKFLOW = "workflow"
    UNKNOWN = "unknown"

class SafetyLevel(Enum):
    PARANOID = 0
    SAFE = 1
    ELEVATED = 2
    FULL = 3

class ThreatLevel(Enum):
    NONE = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class TaskStatus(Enum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    SKIPPED = "skipped"

class PipelineStage(Enum):
    RECEIVE = "receive"
    UNDERSTAND = "understand"
    PLAN = "plan"
    DECIDE = "decide"
    EXECUTE = "execute"
    VALIDATE = "validate"
    RESPOND = "respond"
    LEARN = "learn"

# ================================================================
# CORE DATA STRUCTURES - The language of the AI
# ================================================================

@dataclass
class Step:
    id: str
    description: str
    module: str
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    params_template: Dict[str, str] = field(default_factory=dict)
    depends_on: List[str] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    retries: int = 0
    max_retries: int = 3

@dataclass
class Task:
    id: str
    intent: Intent
    description: str
    steps: List[Step] = field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING
    context: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None

@dataclass
class Thought:
    timestamp: datetime
    stage: PipelineStage
    content: str
    data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ExecutionContext:
    session_id: str
    user_input: str
    original_input: str
    intent: Intent
    task: Optional[Task] = None
    thoughts: List[Thought] = field(default_factory=list)
    memory: Dict[str, Any] = field(default_factory=dict)
    history: List[Dict] = field(default_factory=list)
    current_step: int = 0
    start_time: datetime = field(default_factory=datetime.now)

@dataclass
class ModuleResult:
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

# ================================================================
# INTELLIGENT MEMORY - Short and long term with learning
# ================================================================

class IntelligentMemory:
    def __init__(self):
        self.short_term: Dict[str, Any] = {}
        self.learned_patterns: Dict[str, int] = {}
        self.tool_success_rate: Dict[str, float] = {}
        self.conversation_context: List[str] = []
        self.session_history: List[Dict] = []
        
        self.long_term_file = os.path.join(project_root, "data", "memory", "long_term.jsonl")
        os.makedirs(os.path.dirname(self.long_term_file), exist_ok=True)
        self._load_patterns()
    
    def _load_patterns(self):
        if os.path.exists(self.long_term_file):
            try:
                with open(self.long_term_file, 'r') as f:
                    for line in f:
                        entry = json.loads(line.strip())
                        if entry.get('type') == 'pattern':
                            pattern = entry.get('data', {}).get('pattern', '')
                            success = entry.get('data', {}).get('success', False)
                            if pattern:
                                self.learned_patterns[pattern] = self.learned_patterns.get(pattern, 0) + (1 if success else -1)
            except:
                pass
    
    def think(self, thought: Thought):
        self.short_term[f"thought_{len(self.short_term)}"] = {
            "content": thought.content,
            "stage": thought.stage.value,
            "timestamp": thought.timestamp.isoformat()
        }
        if len(self.short_term) > 50:
            oldest = list(self.short_term.keys())[0]
            del self.short_term[oldest]
    
    def remember(self, key: str, value: Any):
        self.short_term[key] = {"value": value, "timestamp": datetime.now().isoformat()}
    
    def recall(self, key: str) -> Optional[Any]:
        entry = self.short_term.get(key)
        return entry.get("value") if entry else None
    
    def learn(self, pattern: str, success: bool, metadata: Dict = None):
        self.learned_patterns[pattern] = self.learned_patterns.get(pattern, 0) + (1 if success else -1)
        
        self.session_history.append({
            "pattern": pattern,
            "success": success,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        })
        
        with open(self.long_term_file, 'a') as f:
            f.write(json.dumps({
                "type": "pattern",
                "data": {"pattern": pattern, "success": success, "metadata": metadata},
                "timestamp": datetime.now().isoformat()
            }) + "\n")
    
    def get_context(self) -> Dict[str, Any]:
        successful_patterns = [p for p, score in self.learned_patterns.items() if score > 0]
        return {
            "recent_patterns": successful_patterns[-10:],
            "session_history": self.session_history[-5:],
            "short_term_keys": list(self.short_term.keys())[-10:]
        }
    
    def update_tool_success(self, tool: str, success: bool):
        current = self.tool_success_rate.get(tool, 0.5)
        self.tool_success_rate[tool] = current * 0.7 + (1 if success else 0) * 0.3

# ================================================================
# ADVANCED TASK PLANNER - Breaks tasks into executable steps
# ================================================================

class TaskPlanner:
    def __init__(self, memory: IntelligentMemory):
        self.memory = memory
        
        self.action_templates = {
            Intent.INSTALL: [
                Step(id="check", description="Check if tool exists", module="installer", action="check", 
                     params_template={"package": "{package}"}),
                Step(id="install", description="Install tool", module="installer", action="install",
                     params_template={"package": "{package}"}, depends_on=["check"])
            ],
            Intent.SECURITY_SCAN: [
                Step(id="prepare", description="Prepare scan parameters", module="security", action="prepare",
                     params_template={"target": "{target}"}),
                Step(id="scan", description="Execute security scan", module="security", action="scan",
                     params_template={"target": "{target}", "type": "{scan_type}"}, depends_on=["prepare"]),
                Step(id="analyze", description="Analyze results", module="security", action="analyze",
                     params_template={}, depends_on=["scan"])
            ],
            Intent.COMMAND: [
                Step(id="validate", description="Validate command", module="safety", action="check",
                     params_template={"command": "{command}"}),
                Step(id="execute", description="Execute command", module="automation", action="execute",
                     params_template={"command": "{command}"}, depends_on=["validate"]),
                Step(id="log", description="Log result", module="memory", action="store",
                     params_template={"result": "{result}"}, depends_on=["execute"])
            ]
        }
    
    def plan(self, user_input: str, intent: Intent, params: Dict[str, Any]) -> Task:
        task_id = f"task_{int(time.time())}"
        task = Task(
            id=task_id,
            intent=intent,
            description=user_input,
            context=params
        )
        
        if intent in self.action_templates:
            for step_template in self.action_templates[intent]:
                step = Step(
                    id=f"{task_id}_{step_template.id}",
                    description=step_template.description,
                    module=step_template.module,
                    action=step_template.action,
                    depends_on=[f"{task_id}_{dep}" for dep in step_template.depends_on],
                    params=self._expand_params(step_template.params_template, params)
                )
                task.steps.append(step)
        else:
            step = Step(
                id=f"{task_id}_execute",
                description=f"Execute: {user_input}",
                module="automation",
                action="execute",
                params={"command": user_input}
            )
            task.steps.append(step)
        
        return task
    
    def _expand_params(self, template: Dict, params: Dict) -> Dict:
        expanded = {}
        for key, value in template.items():
            if isinstance(value, str) and "{" in value:
                for param_key in params:
                    value = value.replace(f"{{{param_key}}}", str(params.get(param_key, "")))
            expanded[key] = value
        return expanded

# ================================================================
# SAFETY LAYER - Intelligent threat detection
# ================================================================

class SafetyLayer:
    DANGEROUS_PATTERNS = [
        (r'rm\s+-rf\s+/\s*(--no-preserve-root)?', ThreatLevel.CRITICAL, "Recursive root deletion"),
        (r'format\s+[a-z]:', ThreatLevel.CRITICAL, "Drive format attempt"),
        (r':\(\)\{.*:\|.*&.*\}', ThreatLevel.CRITICAL, "Fork bomb"),
        (r'dd\s+.*of=/dev/[sh]d[a-z]', ThreatLevel.CRITICAL, "Direct device write"),
        (r'mkfs\.', ThreatLevel.CRITICAL, "Filesystem creation"),
        (r'>*/etc/passwd', ThreatLevel.CRITICAL, "System file corruption"),
        (r'chmod\s+-R\s+777\s+/', ThreatLevel.HIGH, "World-writable permissions"),
        (r'wget.*\|\s*sh', ThreatLevel.HIGH, "Pipe download to shell"),
        (r'curl.*\|\s*sh', ThreatLevel.HIGH, "Pipe download to shell"),
        (r'shutdown|reboot|init\s+0', ThreatLevel.HIGH, "System shutdown"),
        (r'kill\s+-9\s+-1', ThreatLevel.HIGH, "Kill all processes"),
        (r'eval\s+\$\(', ThreatLevel.MEDIUM, "Dynamic code execution"),
        (r';\s*rm\s+-rf\s+', ThreatLevel.MEDIUM, "Hidden deletion"),
    ]
    
    def __init__(self, safety_level: SafetyLevel):
        self.safety_level = safety_level
        self.blocked_count = 0
        self.allowed_count = 0
    
    def analyze(self, command: str) -> tuple[bool, ThreatLevel, str]:
        for pattern, level, description in self.DANGEROUS_PATTERNS:
            if re.search(pattern, command, re.IGNORECASE):
                blocked = level.value >= ThreatLevel.HIGH.value or self.safety_level == SafetyLevel.SAFE
                if blocked:
                    self.blocked_count += 1
                    return False, level, description
        self.allowed_count += 1
        return True, ThreatLevel.NONE, "Safe"
    
    def get_safety_report(self) -> Dict:
        total = self.blocked_count + self.allowed_count
        return {
            "blocked": self.blocked_count,
            "allowed": self.allowed_count,
            "total_checked": total,
            "block_rate": f"{(self.blocked_count/total*100):.1f}%" if total > 0 else "0%"
        }

# ================================================================
# ORCHESTRATOR - Coordinates all modules like a brain
# ================================================================

class Orchestrator:
    def __init__(self, memory: IntelligentMemory, safety: SafetyLayer):
        self.memory = memory
        self.safety = safety
        self.modules: Dict[str, Any] = {}
        self._register_modules()
    
    def _register_modules(self):
        try:
            from core.automation import get_automation, SafetyLevel as AutoSafety
            safety = AutoSafety.SAFE if self.safety.safety_level == SafetyLevel.SAFE else AutoSafety.ELEVATED
            self.modules["automation"] = get_automation(safety)
            logger.info("Orchestrator: automation module connected")
        except Exception as e:
            logger.error(f"Orchestrator: failed to load automation - {e}")
            self.modules["automation"] = None
        
        try:
            from core.installer import get_installer
            self.modules["installer"] = get_installer()
            logger.info("Orchestrator: installer module connected")
        except Exception as e:
            logger.error(f"Orchestrator: failed to load installer - {e}")
            self.modules["installer"] = None
        
        try:
            from core.cybersecurity import get_security
            self.modules["security"] = get_security()
            logger.info("Orchestrator: security module connected")
        except Exception as e:
            logger.error(f"Orchestrator: failed to load security - {e}")
            self.modules["security"] = None
    
    def execute_step(self, step: Step) -> ModuleResult:
        self.memory.think(Thought(
            timestamp=datetime.now(),
            stage=PipelineStage.EXECUTE,
            content=f"Executing: {step.action}",
            data={"module": step.module, "step": step.id}
        ))
        
        try:
            if step.module == "automation":
                return self._execute_automation(step)
            elif step.module == "installer":
                return self._execute_installer(step)
            elif step.module == "security":
                return self._execute_security(step)
            elif step.module == "safety":
                return self._execute_safety(step)
            elif step.module == "memory":
                return self._execute_memory(step)
            else:
                return ModuleResult(False, None, f"Unknown module: {step.module}")
        except Exception as e:
            logger.error(f"Step {step.id} failed: {e}")
            return ModuleResult(False, None, str(e))
    
    def _execute_automation(self, step: Step) -> ModuleResult:
        automation = self.modules.get("automation")
        if not automation:
            return ModuleResult(False, None, "Automation module not available")
        
        if step.action == "execute":
            command = step.params.get("command", "")
            safe, level, desc = self.safety.analyze(command)
            if not safe:
                return ModuleResult(False, None, f"Blocked: {desc}")
            
            result = automation.execute(command)
            return ModuleResult(result.success, result.stdout, result.stderr)
        
        return ModuleResult(False, None, f"Unknown action: {step.action}")
    
    def _execute_installer(self, step: Step) -> ModuleResult:
        installer = self.modules.get("installer")
        if not installer:
            return ModuleResult(False, None, "Installer module not available")
        
        if step.action == "check":
            package = step.params.get("package", "")
            return ModuleResult(True, installer.check_dependency(package), None)
        
        if step.action == "install":
            package = step.params.get("package", "")
            result = installer.install(package)
            return ModuleResult(result.success, f"Installed {package}" if result.success else None, result.stderr)
        
        return ModuleResult(False, None, f"Unknown action: {step.action}")
    
    def _execute_security(self, step: Step) -> ModuleResult:
        security = self.modules.get("security")
        if not security:
            return ModuleResult(False, None, "Security module not available")
        
        if step.action == "scan":
            target = step.params.get("target", "")
            if "port" in step.params:
                result = security.scan_port(target, step.params["port"])
                return ModuleResult(True, f"Port {result.port}: {result.status}", None)
            else:
                results = security.scan_common_ports(target)
                open_ports = [r for r in results if r.status == "open"]
                return ModuleResult(True, f"Open ports: {[r.port for r in open_ports]}", None)
        
        if step.action == "check_url":
            url = step.params.get("url", "")
            check = security.check_url_safety(url)
            return ModuleResult(check["safe"], check, None)
        
        return ModuleResult(False, None, f"Unknown action: {step.action}")
    
    def _execute_safety(self, step: Step) -> ModuleResult:
        if step.action == "check":
            command = step.params.get("command", "")
            safe, level, desc = self.safety.analyze(command)
            return ModuleResult(safe, {"level": level.value, "description": desc}, None)
        return ModuleResult(True, {"level": 0, "description": "OK"}, None)
    
    def _execute_memory(self, step: Step) -> ModuleResult:
        if step.action == "store":
            self.memory.remember(step.params.get("key", "unknown"), step.params.get("value"))
            return ModuleResult(True, "Stored", None)
        return ModuleResult(True, "OK", None)

# ================================================================
# EXECUTION ENGINE - Runs tasks step by step with retry logic
# ================================================================

class ExecutionEngine:
    def __init__(self, orchestrator: Orchestrator, memory: IntelligentMemory):
        self.orchestrator = orchestrator
        self.memory = memory
        self.max_retries = 3
    
    def execute_task(self, task: Task) -> Task:
        task.status = TaskStatus.EXECUTING
        
        while not self._all_steps_complete(task):
            for step in task.steps:
                if step.status in [TaskStatus.COMPLETED, TaskStatus.SKIPPED]:
                    continue
                
                if not self._dependencies_met(step, task):
                    continue
                
                step.status = TaskStatus.EXECUTING
                
                result = self.orchestrator.execute_step(step)
                
                if result.success:
                    step.status = TaskStatus.COMPLETED
                    step.result = result.output
                    self.memory.learn(f"{step.module}:{step.action}", True, {"output": str(result.output)})
                else:
                    if step.retries < self.max_retries:
                        step.retries += 1
                        step.status = TaskStatus.RETRYING
                        logger.warning(f"Retrying step {step.id} (attempt {step.retries})")
                    else:
                        step.status = TaskStatus.FAILED
                        step.error = result.error
                        self.memory.learn(f"{step.module}:{step.action}", False, {"error": result.error})
                
                self._update_task_status(task)
        
        task.completed_at = datetime.now()
        task.status = TaskStatus.COMPLETED if self._all_steps_success(task) else TaskStatus.FAILED
        return task
    
    def _dependencies_met(self, step: Step, task: Task) -> bool:
        for dep_id in step.depends_on:
            dep_step = next((s for s in task.steps if s.id == dep_id), None)
            if dep_step and dep_step.status != TaskStatus.COMPLETED:
                return False
        return True
    
    def _all_steps_complete(self, task: Task) -> bool:
        return all(s.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.SKIPPED] for s in task.steps)
    
    def _all_steps_success(self, task: Task) -> bool:
        return all(s.status == TaskStatus.COMPLETED for s in task.steps)
    
    def _update_task_status(self, task: Task):
        completed = sum(1 for s in task.steps if s.status == TaskStatus.COMPLETED)
        total = len(task.steps)
        task.context["progress"] = f"{completed}/{total}"

# ================================================================
# DECISION ENGINE - Intelligently routes and decides
# ================================================================

class DecisionEngine:
    def __init__(self, memory: IntelligentMemory):
        self.memory = memory
        
        self.intent_patterns = {
            Intent.INSTALL: [
                r'\b(install|add|get|download)\s+\w+',
                r'\b(pip|npm|apt|pacman)\s+(install|add)',
            ],
            Intent.SECURITY_SCAN: [
                r'\b(scan|nmap|check|analyze)\s+(url|ip|port|domain|network)',
                r'\b(check|detect)\s+(vulnerability|threat|phishing|malware)',
            ],
            Intent.THINK: [
                r'\b(think|analyze|reason|explain|how\s+to|why)',
            ],
            Intent.SYSTEM: [
                r'\b(system|process|memory|cpu|status|info|monitor)',
            ],
            Intent.FILE_OP: [
                r'\b(file|directory|folder|read|write|list|ls|dir)',
            ],
            Intent.CHAT: [
                r'\b(hi|hello|hey|thanks|bye|goodbye|good\s+morning)',
            ],
            Intent.CODE_GENERATION: [
                r'\b(create|make|build|generate|write)\s+(a\s+)?(login|register|signup|form|page|app|website|script|function|class)',
                r'\b(create|make|build)\s+\w+\s+(file|page|app|code)',
                r'\b(show|write|create)\s+me\s+(a\s+)?(login|simple|basic)',
            ],
            Intent.COMMAND: [
                r'^(ls|cd|cat|grep|find|ps|kill|rm|mkdir|touch|pwd|echo|chmod|chown|cp|mv|python|node|npm)',
            ],
        }
        
        self.param_extractors = {
            'url': r'(https?://\S+)',
            'ip': r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',
            'port': r'port[:\s]+(\d+)',
            'package': r'(?:install|add|get)\s+(\S+)',
            'domain': r'(?:scan|check)\s+(?:domain\s+)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        }
    
    def understand(self, user_input: str) -> tuple[Intent, Dict[str, Any]]:
        text = user_input.lower().strip()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    self.memory.think(Thought(
                        timestamp=datetime.now(),
                        stage=PipelineStage.UNDERSTAND,
                        content=f"Detected intent: {intent.value}",
                        data={"input": user_input, "pattern": pattern}
                    ))
                    params = self._extract_params(text)
                    return intent, params
        
        return Intent.COMMAND, {"command": user_input}
    
    def _extract_params(self, text: str) -> Dict[str, Any]:
        params = {"raw": text}
        
        for key, pattern in self.param_extractors.items():
            matches = re.findall(pattern, text)
            if matches:
                params[key] = matches[0]
        
        return params
    
    def should_retry(self, step: Step, error: str) -> bool:
        if step.retries >= step.max_retries:
            return False
        
        retry_keywords = ["not found", "not installed", "command not found", "no such file", "connection refused"]
        return any(kw in error.lower() for kw in retry_keywords)

# ================================================================
# MAIN CODE-02 SYSTEM - The living AI
# ================================================================

class Code02AI:
    VERSION = "4.0-LIVING"
    
    def __init__(self):
        self.name = "CODE-02"
        self.start_time = datetime.now()
        self.running = False
        self.session_id = f"session_{int(time.time())}"
        
        self.platform = self._detect_platform()
        self.safety_level = SafetyLevel.FULL if "linux" in self.platform else SafetyLevel.SAFE
        
        logger.info(f"{'='*60}")
        logger.info(f"CODE-02 v{self.VERSION} INITIALIZING...")
        logger.info(f"{'='*60}")
        
        self.memory = IntelligentMemory()
        self.safety = SafetyLayer(self.safety_level)
        self.planner = TaskPlanner(self.memory)
        self.decision = DecisionEngine(self.memory)
        self.orchestrator = Orchestrator(self.memory, self.safety)
        self.executor = ExecutionEngine(self.orchestrator, self.memory)
        
        self.config = {
            "auto_install": True,
            "retry_on_failure": True,
            "learn_enabled": True,
            "verbose_thinking": True
        }
        
        logger.info(f"Platform: {self.platform} | Safety: {self.safety_level.name}")
        logger.info(f"Memory: {len(self.memory.learned_patterns)} patterns | Modules: {len(self.orchestrator.modules)}")
        logger.info(f"{'='*60}")
        logger.info("SYSTEM READY")
        logger.info(f"{'='*60}\n")
    
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
    
    # ================================================================
    # MAIN LOOP - The heartbeat of the AI
    # ================================================================
    
    def run(self):
        self.running = True
        self._print_banner()
        
        logger.info("Entering main loop... (type 'exit' to quit)")
        
        while self.running:
            try:
                user_input = input(f"\n{self.name}> ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    self._shutdown()
                    break
                
                self._process_input(user_input)
                
            except KeyboardInterrupt:
                print("\n(Press 'exit' to quit)")
            except EOFError:
                break
            except Exception as e:
                logger.error(f"Error: {e}")
                print(f"Error: {e}")
        
        self._shutdown()
    
    def _process_input(self, user_input: str):
        context = ExecutionContext(
            session_id=self.session_id,
            user_input=user_input,
            original_input=user_input,
            intent=Intent.UNKNOWN
        )
        
        self.memory.think(Thought(
            timestamp=datetime.now(),
            stage=PipelineStage.RECEIVE,
            content=f"Received: {user_input}",
            data={}
        ))
        
        if user_input.lower() in ['help', '?']:
            print(self._get_help())
            return
        
        if user_input.lower() == 'status':
            print(self._get_status())
            return
        
        if user_input.lower() == 'brain':
            print(self._get_brain_state())
            return
        
        if user_input.lower() == 'safety':
            print(json.dumps(self.safety.get_safety_report(), indent=2))
            return
        
        intent, params = self.decision.understand(user_input)
        context.intent = intent
        
        if intent == Intent.CHAT:
            response = self._handle_chat(user_input)
            print(f"\n{response}")
            self.memory.learn(f"chat:{user_input}", True)
            return
        
        if intent == Intent.THINK:
            response = self._handle_think(user_input)
            print(f"\n{response}")
            self.memory.learn(f"think:{user_input}", True)
            return
        
        if intent == Intent.CODE_GENERATION:
            response = self._handle_code_generation(user_input)
            print(response)
            return
        
        self.memory.think(Thought(
            timestamp=datetime.now(),
            stage=PipelineStage.PLAN,
            content=f"Planning task for intent: {intent.value}",
            data={"params": params}
        ))
        
        task = self.planner.plan(user_input, intent, params)
        context.task = task
        
        if self.config.get("verbose_thinking"):
            print(f"\n[THINKING] Intent: {intent.value} | Steps: {len(task.steps)}")
        
        task = self.executor.execute_task(task)
        
        self._display_results(task)
        
        self.memory.think(Thought(
            timestamp=datetime.now(),
            stage=PipelineStage.LEARN,
            content=f"Task completed: {task.status.value}",
            data={"steps": len(task.steps), "success": task.status == TaskStatus.COMPLETED}
        ))
    
    def _display_results(self, task: Task):
        print(f"\n{'='*50}")
        print(f"TASK: {task.description}")
        print(f"{'='*50}")
        
        for step in task.steps:
            status_icon = {
                TaskStatus.COMPLETED: "[OK]",
                TaskStatus.FAILED: "[FAIL]",
                TaskStatus.PENDING: "[...]",
                TaskStatus.EXECUTING: "[RUN]",
                TaskStatus.RETRYING: "[RTY]",
                TaskStatus.SKIPPED: "[SKP]"
            }.get(step.status, "[???]")
            
            result_str = f" -> {step.result}" if step.result else ""
            error_str = f" ERROR: {step.error}" if step.error else ""
            
            print(f"  {status_icon} {step.description}{result_str}{error_str}")
        
        print(f"\nSTATUS: {task.status.value.upper()}")
        
        if task.completed_at:
            duration = (task.completed_at - task.created_at).total_seconds()
            print(f"DURATION: {duration:.2f}s")
    
    def _shutdown(self):
        uptime = datetime.now() - self.start_time
        print(f"\n{'='*50}")
        print("SHUTTING DOWN")
        print(f"{'='*50}")
        print(f"Uptime: {str(uptime).split('.')[0]}")
        print(f"Patterns learned: {len(self.memory.learned_patterns)}")
        print(f"Safety: {self.safety.get_safety_report()['blocked']} blocked, {self.safety.get_safety_report()['allowed']} allowed")
        print(f"{'='*50}\n")
        self.running = False
        logger.info("CODE-02 stopped")
    
    def _print_banner(self):
        print(f"""
+============================================================+
|                                                           |
|    CODE-02  INTELLIGENT AUTONOMOUS AI SYSTEM              |
|                     v{self.VERSION}                             |
|                                                           |
+============================================================+
|  Platform: {self.platform:<30}           |
|  Safety: {self.safety_level.name:<30}   |
|  Modules: {len(self.orchestrator.modules):<28}           |
|  Patterns Learned: {len(self.memory.learned_patterns):<20}         |
+============================================================+
|                                                           |
|    THINK  ->  DECIDE  ->  PLAN  ->  EXECUTE  ->  LEARN    |
|                                                           |
+============================================================+
""")
    
    def _get_status(self) -> str:
        uptime = datetime.now() - self.start_time
        return json.dumps({
            "name": self.name,
            "version": self.VERSION,
            "platform": self.platform,
            "safety": self.safety_level.name,
            "uptime_seconds": uptime.total_seconds(),
            "modules": [k for k, v in self.orchestrator.modules.items() if v],
            "patterns": len(self.memory.learned_patterns),
            "session_history": len(self.memory.session_history)
        }, indent=2)
    
    def _get_brain_state(self) -> str:
        context = self.memory.get_context()
        return json.dumps({
            "thinking": "ACTIVE",
            "context": context,
            "recent_thoughts": list(self.memory.short_term.keys())[-5:],
            "tool_success_rates": self.memory.tool_success_rate
        }, indent=2)
    
    def _get_help(self) -> str:
        return """
CODE-02 Commands:
==================

THINKING:
  think about <topic>     Analyze and reason about a topic

AUTOMATION:
  <any shell command>    Execute shell command (ls, cd, cat, etc.)

INSTALLATION:
  install <package>       Install package (auto-detects manager)
  pip install flask      Install Python package

SECURITY:
  scan <ip>              Scan IP for open ports
  scan <ip> port 80     Scan specific port
  check <url>            Check URL for threats

SYSTEM:
  status                 Show system information
  brain                  Show AI brain state
  safety                 Show safety report
  help                   Show this help

EXAMPLES:
  install nmap and scan 8.8.8.8
  scan 192.168.1.1 port 443
  check http://example.com
  think about machine learning

  The AI will:
  - Break complex tasks into steps
  - Auto-install missing tools
  - Retry on failure
  - Learn from every interaction
"""
    
    def _handle_chat(self, text: str) -> str:
        text_lower = text.lower()
        
        if any(kw in text_lower for kw in ['hello', 'hi', 'hey', 'good morning']):
            return "Hello! I'm CODE-02, your intelligent AI assistant. I can help you with commands, installations, security scans, and more. What would you like to do today?"
        
        if 'thanks' in text_lower or 'thank you' in text_lower:
            return "You're welcome! I'm here whenever you need me. Just let me know what you'd like to accomplish."
        
        if any(kw in text_lower for kw in ['bye', 'goodbye', 'see you']):
            return "Goodbye! It was great working with you. Feel free to return whenever you need assistance."
        
        return "I'm CODE-02. Type 'help' to see what I can do!"
    
    def _handle_think(self, text: str) -> str:
        topic = text.lower().replace('think', '').replace('about', '').replace('analyze', '').strip()
        
        return f"""
ANALYZING: "{topic}"
================================================================

[UNDERSTAND]
- Breaking down the topic into components
- Identifying key concepts and relationships
- Understanding the user's goal

[ANALYZE]
- Evaluating different perspectives
- Checking for dependencies or prerequisites
- Considering constraints and limitations

[REASON]
- Drawing logical connections
- Identifying patterns
- Formulating conclusions

[RECOMMEND]
- Suggesting actionable steps
- Identifying next actions
- Providing resources if applicable

================================================================
[Note: Connect LLM (Ollama/OpenAI) for deep reasoning]
"""

    def _handle_code_generation(self, user_input: str) -> str:
        text_lower = user_input.lower()
        
        if 'login' in text_lower and 'page' in text_lower:
            return self._create_login_page()
        
        if 'register' in text_lower or 'signup' in text_lower:
            return self._create_register_page()
        
        if 'simple' in text_lower or 'basic' in text_lower:
            if 'app' in text_lower:
                return self._create_simple_app()
        
        return f"I understand you want to create something. Could you be more specific?\n\nFor example:\n  - create a login page\n  - create a register form\n  - create a simple app"
    
    def _create_login_page(self) -> str:
        login_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Login</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .login-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            width: 350px;
        }
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #667eea;
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background: #5a6fd6;
        }
        .register-link {
            text-align: center;
            margin-top: 20px;
        }
        .register-link a {
            color: #667eea;
            text-decoration: none;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h2>Login</h2>
        <form action="/login" method="POST">
            <div class="input-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required placeholder="Enter your email">
            </div>
            <div class="input-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required placeholder="Enter your password">
            </div>
            <button type="submit">Login</button>
        </form>
        <div class="register-link">
            <a href="/register">Don't have an account? Register</a>
        </div>
    </div>
</body>
</html>'''
        
        filepath = os.path.join(project_root, "login.html")
        with open(filepath, 'w') as f:
            f.write(login_html)
        
        return f"""
CREATED: login.html

The login page has been created at:
  {filepath}

FEATURES:
  - Modern gradient background
  - Email and password fields
  - Responsive design
  - Login button with hover effect
  - Link to registration page

TO USE:
  Open the file in any web browser or serve it with a web server.

Preview the file with:
  python -m http.server 8000
  Then visit http://localhost:8000/login.html
"""
    
    def _create_register_page(self) -> str:
        register_html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Register</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
        }
        .register-container {
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            width: 400px;
        }
        h2 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
        }
        .input-group {
            margin-bottom: 15px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            color: #555;
        }
        input {
            width: 100%;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            box-sizing: border-box;
        }
        button {
            width: 100%;
            padding: 12px;
            background: #11998e;
            border: none;
            border-radius: 5px;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }
        button:hover {
            background: #0e8a7c;
        }
    </style>
</head>
<body>
    <div class="register-container">
        <h2>Create Account</h2>
        <form action="/register" method="POST">
            <div class="input-group">
                <label for="username">Username</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div class="input-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="input-group">
                <label for="password">Password</label>
                <input type="password" id="password" name="password" required>
            </div>
            <div class="input-group">
                <label for="confirm">Confirm Password</label>
                <input type="password" id="confirm" name="confirm" required>
            </div>
            <button type="submit">Register</button>
        </form>
    </div>
</body>
</html>'''
        
        filepath = os.path.join(project_root, "register.html")
        with open(filepath, 'w') as f:
            f.write(register_html)
        
        return f"""
CREATED: register.html

The registration page has been created at:
  {filepath}

FEATURES:
  - Username, email, password fields
  - Password confirmation
  - Green gradient theme

TO USE:
  Open the file in any web browser.
"""
    
    def _create_simple_app(self) -> str:
        app_py = '''"""
Simple Flask Application
Generated by CODE-02
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return '<h1>Welcome to CODE-02 App!</h1><a href="/login">Login</a>'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Add your authentication logic here
        return f'Login attempted for: {email}'
    return \'\'\'<!DOCTYPE html>
<html>
<head><title>Login</title></head>
<body>
    <h2>Login</h2>
    <form method="POST">
        <input type="email" name="email" placeholder="Email" required>
        <input type="password" name="password" placeholder="Password" required>
        <button type="submit">Login</button>
    </form>
</body>
</html>\'\'\'

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
        
        filepath = os.path.join(project_root, "app.py")
        with open(filepath, 'w') as f:
            f.write(app_py)
        
        return f"""
CREATED: app.py

A simple Flask application has been created at:
  {filepath}

FEATURES:
  - Home page
  - Login route with POST handling
  - Debug mode enabled

TO USE:
  1. pip install flask
  2. python app.py
  3. Visit http://localhost:5000
"""

# ================================================================
# ENTRY POINT
# ================================================================

def main():
    try:
        ai = Code02AI()
        ai.run()
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
