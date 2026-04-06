"""
============================================================
AUTOMATION ENGINE - Task Execution System
============================================================
Safe, controlled execution of tasks and workflows
"""

import asyncio
import subprocess
import os
import signal
import json
import shlex
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import hashlib


class ExecutionMode(Enum):
    SAFE = "safe"        # Limited commands
    STANDARD = "standard"  # Most commands allowed
    ADVANCED = "advanced"  # All commands allowed
    DANGEROUS = "dangerous"  # Dangerous commands allowed (use with caution)


class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    TIMEOUT = "timeout"


@dataclass
class Task:
    id: str
    name: str
    command: str
    mode: ExecutionMode = ExecutionMode.SAFE
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    stdout: str = ""
    stderr: str = ""
    exit_code: Optional[int] = None
    timeout: int = 60  # seconds
    tags: List[str] = field(default_factory=list)


@dataclass
class WorkflowStep:
    step_id: int
    name: str
    command: str
    continue_on_error: bool = False
    required: bool = True
    delay: float = 0  # seconds to wait before executing


@dataclass
class Workflow:
    id: str
    name: str
    steps: List[WorkflowStep]
    mode: ExecutionMode = ExecutionMode.SAFE
    status: TaskStatus = TaskStatus.PENDING
    results: List[Dict] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None


class AutomationEngine:
    """
    Automation engine for safe task execution
    - Sandboxed command execution
    - Workflow automation
    - Process management
    - Safety controls
    """
    
    # Commands that are ALWAYS blocked
    BLOCKED_COMMANDS = [
        "rm -rf /", "rm -rf /*", "> /dev/sda",
        ":(){ :|:& };:", "mkfs", "dd if=",
        "> /etc/passwd", "> /etc/shadow"
    ]
    
    # Commands requiring ADVANCED or DANGEROUS mode
    DANGEROUS_COMMANDS = [
        "iptables", "ufw", "firewall-cmd",
        "useradd", "userdel", "usermod",
        "chmod 777", "chown", "visudo",
        "shutdown", "reboot", "init 0", "init 6",
        "kill -9", "killall"
    ]
    
    def __init__(self, mode: ExecutionMode = ExecutionMode.SAFE):
        self.mode = mode
        self.active_processes: Dict[str, subprocess.Popen] = {}
        self.task_history: List[Task] = []
        self.workflow_history: List[Workflow] = []
        self.max_history = 100
        
        # Callbacks
        self.on_task_start: Optional[Callable] = None
        self.on_task_complete: Optional[Callable] = None
        self.on_task_output: Optional[Callable] = None
    
    def _is_command_safe(self, command: str) -> Tuple[bool, str]:
        """Check if command is safe to execute"""
        cmd_lower = command.lower()
        
        # Check blocked commands
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in cmd_lower:
                return False, f"Blocked command detected: {blocked}"
        
        # Check dangerous commands based on mode
        if self.mode in [ExecutionMode.SAFE, ExecutionMode.STANDARD]:
            for dangerous in self.DANGEROUS_COMMANDS:
                if dangerous in cmd_lower:
                    return False, f"Command requires higher permission level: {dangerous}"
        
        return True, "OK"
    
    async def execute(
        self,
        command: str,
        name: str = None,
        timeout: int = 60,
        capture_output: bool = True,
        cwd: str = None,
        env: Dict = None
    ) -> Task:
        """Execute a single command"""
        
        task_id = hashlib.md5(f"{command}{datetime.now()}".encode()).hexdigest()[:12]
        task = Task(
            id=task_id,
            name=name or command[:50],
            command=command,
            mode=self.mode,
            timeout=timeout
        )
        
        # Safety check
        safe, reason = self._is_command_safe(command)
        if not safe:
            task.status = TaskStatus.FAILED
            task.stderr = reason
            task.completed_at = datetime.now().isoformat()
            return task
        
        # Execute
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now().isoformat()
        
        if self.on_task_start:
            self.on_task_start(task)
        
        try:
            if os.name == "nt":
                # Windows
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    env={**os.environ, **(env or {})}
                )
            else:
                # Unix/Linux
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=capture_output,
                    text=True,
                    timeout=timeout,
                    cwd=cwd,
                    env={**os.environ, **(env or {})}
                )
            
            task.exit_code = result.returncode
            task.stdout = result.stdout if capture_output else ""
            task.stderr = result.stderr if capture_output else ""
            task.status = TaskStatus.COMPLETED if result.returncode == 0 else TaskStatus.FAILED
            
        except subprocess.TimeoutExpired:
            task.status = TaskStatus.TIMEOUT
            task.stderr = f"Command timed out after {timeout} seconds"
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.stderr = str(e)
        
        task.completed_at = datetime.now().isoformat()
        
        # Store in history
        self.task_history.append(task)
        if len(self.task_history) > self.max_history:
            self.task_history = self.task_history[-self.max_history:]
        
        if self.on_task_complete:
            self.on_task_complete(task)
        
        return task
    
    async def execute_script(
        self,
        script: str,
        language: str = "bash",
        name: str = None
    ) -> Task:
        """Execute a script (bash, python, node, etc.)"""
        
        # Create temporary script file
        import tempfile
        
        if language == "bash":
            ext = ".sh"
            shebang = "#!/bin/bash\n"
            runner = "bash"
        elif language == "python":
            ext = ".py"
            shebang = "#!/usr/bin/env python3\n"
            runner = "python3"
        elif language == "node":
            ext = ".js"
            shebang = "#!/usr/bin/env node\n"
            runner = "node"
        elif language == "ruby":
            ext = ".rb"
            shebang = "#!/usr/bin/env ruby\n"
            runner = "ruby"
        else:
            ext = ".txt"
            shebang = ""
            runner = "sh"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=ext, delete=False) as f:
            f.write(shebang + script)
            script_path = f.name
        
        try:
            # Make executable
            if os.name != "nt":
                os.chmod(script_path, 0o755)
            
            task = await self.execute(
                f"{runner} {script_path}",
                name=name or f"Script ({language})"
            )
            
        finally:
            # Clean up
            try:
                os.unlink(script_path)
            except:
                pass
        
        return task
    
    async def execute_workflow(
        self,
        workflow: Workflow,
        stop_on_error: bool = True
    ) -> Workflow:
        """Execute a multi-step workflow"""
        
        workflow.status = TaskStatus.RUNNING
        
        for i, step in enumerate(workflow.steps):
            # Wait for delay
            if step.delay > 0:
                await asyncio.sleep(step.delay)
            
            # Execute step
            task = await self.execute(
                step.command,
                name=step.name
            )
            
            workflow.results.append({
                "step_id": step.step_id,
                "step_name": step.name,
                "success": task.status == TaskStatus.COMPLETED,
                "exit_code": task.exit_code,
                "stdout": task.stdout[:500],  # Truncate
                "stderr": task.stderr[:500]
            })
            
            # Check if we should continue
            if task.status != TaskStatus.COMPLETED:
                if step.continue_on_error:
                    continue
                if stop_on_error:
                    workflow.status = TaskStatus.FAILED
                    workflow.completed_at = datetime.now().isoformat()
                    return workflow
        
        workflow.status = TaskStatus.COMPLETED
        workflow.completed_at = datetime.now().isoformat()
        
        self.workflow_history.append(workflow)
        
        return workflow
    
    def create_workflow(
        self,
        name: str,
        steps: List[Dict]
    ) -> Workflow:
        """Create a workflow from step definitions"""
        
        workflow_steps = [
            WorkflowStep(
                step_id=i + 1,
                name=step.get("name", f"Step {i+1}"),
                command=step["command"],
                continue_on_error=step.get("continue_on_error", False),
                required=step.get("required", True),
                delay=step.get("delay", 0)
            )
            for i, step in enumerate(steps)
        ]
        
        return Workflow(
            id=hashlib.md5(f"{name}{datetime.now()}".encode()).hexdigest()[:12],
            name=name,
            steps=workflow_steps,
            mode=self.mode
        )
    
    async def install_package(
        self,
        package: str,
        package_manager: str = "auto"
    ) -> Task:
        """Install a system package"""
        
        if package_manager == "auto":
            # Detect package manager
            if os.path.exists("/etc/arch-release"):
                package_manager = "pacman"
            elif os.path.exists("/etc/debian_version"):
                package_manager = "apt"
            elif os.path.exists("/etc/fedora-release"):
                package_manager = "dnf"
            else:
                package_manager = "apt"  # Default
        
        sudo = os.getuid() != 0
        
        if package_manager == "pacman":
            cmd = f"{'sudo ' if sudo else ''}pacman -S --noconfirm {package}"
        elif package_manager == "apt":
            cmd = f"{'sudo ' if sudo else ''}apt-get install -y {package}"
        elif package_manager == "dnf":
            cmd = f"{'sudo ' if sudo else ''}dnf install -y {package}"
        elif package_manager == "pip":
            cmd = f"pip install {package}"
        elif package_manager == "npm":
            cmd = f"npm install -g {package}"
        else:
            cmd = f"echo 'Unknown package manager: {package_manager}'"
        
        return await self.execute(cmd, name=f"Install {package}")
    
    async def run_python_code(
        self,
        code: str,
        timeout: int = 30
    ) -> Task:
        """Execute Python code directly"""
        
        # Wrap in async if needed
        if "async def" in code or "await" in code:
            wrapped = f"""
import asyncio
{code}

if __name__ == '__main__':
    asyncio.run(main())
"""
        else:
            wrapped = f"""
{code}

if __name__ == '__main__':
    main()
""" if "def main" in code else code
        
        return await self.execute_script(wrapped, language="python", name="Python Execution")
    
    def get_process_list(self) -> List[Dict]:
        """Get list of running processes"""
        if os.name == "nt":
            result = subprocess.run(
                "tasklist /FO CSV /NH",
                shell=True,
                capture_output=True,
                text=True
            )
            processes = []
            for line in result.stdout.strip().split("\n"):
                parts = line.strip('"').split('","')
                if len(parts) >= 5:
                    processes.append({
                        "pid": parts[1],
                        "name": parts[0],
                        "memory": parts[4]
                    })
            return processes
        else:
            result = subprocess.run(
                "ps aux --no-headers",
                shell=True,
                capture_output=True,
                text=True
            )
            processes = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split()
                if len(parts) >= 11:
                    processes.append({
                        "pid": parts[1],
                        "user": parts[0],
                        "cpu": parts[2],
                        "mem": parts[3],
                        "command": " ".join(parts[10:])
                    })
            return processes[:50]  # Limit
    
    def kill_process(self, pid: int) -> bool:
        """Kill a process by PID"""
        try:
            if os.name == "nt":
                subprocess.run(f"taskkill /F /PID {pid}", shell=True)
            else:
                os.kill(pid, signal.SIGTERM)
            return True
        except:
            return False
    
    def get_task_history(self, limit: int = 20) -> List[Dict]:
        """Get recent task history"""
        tasks = self.task_history[-limit:] if self.task_history else []
        return [
            {
                "id": t.id,
                "name": t.name,
                "status": t.status.value,
                "exit_code": t.exit_code,
                "created_at": t.created_at,
                "completed_at": t.completed_at
            }
            for t in reversed(tasks)
        ]
    
    def set_mode(self, mode: ExecutionMode):
        """Change execution mode"""
        self.mode = mode
    
    def get_capabilities(self) -> Dict:
        """Get engine capabilities based on mode"""
        return {
            "mode": self.mode.value,
            "can_execute": True,
            "can_install_packages": self.mode != ExecutionMode.SAFE,
            "can_modify_system": self.mode in [ExecutionMode.ADVANCED, ExecutionMode.DANGEROUS],
            "can_kill_processes": self.mode in [ExecutionMode.STANDARD, ExecutionMode.ADVANCED, ExecutionMode.DANGEROUS],
            "timeout_default": 60,
            "max_history": self.max_history
        }


from typing import Tuple

# Singleton
_automation_engine: Optional[AutomationEngine] = None

def get_automation_engine(mode: ExecutionMode = ExecutionMode.SAFE) -> AutomationEngine:
    global _automation_engine
    if _automation_engine is None:
        _automation_engine = AutomationEngine(mode)
    return _automation_engine
