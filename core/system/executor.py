"""
============================================================
COMMAND EXECUTOR - Secure Command Execution
============================================================
Safe command execution for Linux with output capture
"""

import subprocess
import shlex
import os
import signal
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger("Executor")


class SafetyLevel(Enum):
    PARANOID = 0   # Only read operations
    SAFE = 1       # Standard operations
    ELEVATED = 2   # Some system changes allowed
    DANGEROUS = 3  # Almost everything allowed


@dataclass
class ExecutionResult:
    success: bool
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    timestamp: str
    error_type: Optional[str] = None


@dataclass
class CommandContext:
    cwd: Optional[str] = None
    env: Dict[str, str] = None
    timeout: int = 60
    shell: bool = True


class CommandExecutor:
    """
    Secure command executor with safety controls
    """
    
    # Dangerous patterns - always blocked
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/\s*",
        r"rm\s+-rf\s+/\*",
        r":\(\)\s*:\s*\|",
        r"mkfs",
        r"dd\s+if=",
        r">\s*/dev/sd[a-z]",
        r"shred\s+",
        r"mv\s+.*\s+/dev/null",
        r">\s*/etc/passwd",
        r">\s*/etc/shadow",
    ]
    
    # Commands requiring elevated safety level
    ELEVATED_COMMANDS = [
        "sudo", "su ", "useradd", "userdel", "usermod",
        "chmod", "chown", "visudo", "passwd",
        "iptables", "ufw", "firewall-cmd",
        "systemctl", "service ",
        "kill -9", "killall",
        "shutdown", "reboot", "init 0", "init 6",
        "dd ", "fdisk", "parted",
    ]
    
    # Read-only commands (always safe)
    SAFE_READ_COMMANDS = [
        "ls", "cat", "head", "tail", "grep", "find",
        "which", "whereis", "type", "file",
        "ps", "top", "htop", "df", "du",
        "free", "uname", "hostname", "whoami",
        "id", "pwd", "echo", "date", "cal",
        "wc", "sort", "uniq", "cut", "awk", "sed",
    ]
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.SAFE):
        self.safety_level = safety_level
        self.execution_history: List[ExecutionResult] = []
        self.max_history = 500
        
    def validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command against safety rules"""
        
        cmd_lower = command.lower().strip()
        
        # Check blocked patterns
        for pattern in self.BLOCKED_PATTERNS:
            import re
            if re.search(pattern, cmd_lower):
                return False, f"Blocked dangerous pattern: {pattern}"
        
        # Check safety level for elevated commands
        if self.safety_level.value < SafetyLevel.ELEVATED.value:
            for elevated in self.ELEVATED_COMMANDS:
                if elevated.lower() in cmd_lower:
                    return False, f"Command requires elevated safety level: {elevated}"
        
        return True, "OK"
    
    def execute(
        self,
        command: str,
        context: Optional[CommandContext] = None,
        capture: bool = True
    ) -> ExecutionResult:
        """Execute a command and return structured result"""
        
        # Validate
        safe, reason = self.validate_command(command)
        if not safe:
            return ExecutionResult(
                success=False,
                command=command,
                stdout="",
                stderr=reason,
                exit_code=-1,
                duration_ms=0,
                timestamp=datetime.now().isoformat(),
                error_type="SafetyBlocked"
            )
        
        # Set defaults
        ctx = context or CommandContext()
        
        # Prepare environment
        env = os.environ.copy()
        if ctx.env:
            env.update(ctx.env)
        
        start_time = datetime.now()
        
        try:
            # Execute
            result = subprocess.run(
                command if ctx.shell else shlex.split(command),
                shell=ctx.shell,
                capture_output=capture,
                text=True,
                timeout=ctx.timeout,
                cwd=ctx.cwd,
                env=env
            )
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                command=command,
                stdout=result.stdout if capture else "",
                stderr=result.stderr if capture else "",
                exit_code=result.returncode,
                duration_ms=duration,
                timestamp=start_time.isoformat()
            )
            
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = ExecutionResult(
                success=False,
                command=command,
                stdout="",
                stderr=f"Command timed out after {ctx.timeout} seconds",
                exit_code=-2,
                duration_ms=duration,
                timestamp=start_time.isoformat(),
                error_type="Timeout"
            )
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = ExecutionResult(
                success=False,
                command=command,
                stdout="",
                stderr=str(e),
                exit_code=-3,
                duration_ms=duration,
                timestamp=start_time.isoformat(),
                error_type="Exception"
            )
        
        # Store in history
        self.execution_history.append(exec_result)
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history:]
        
        logger.info(f"Executed: {command[:50]}... -> {exec_result.success}")
        
        return exec_result
    
    def execute_script(
        self,
        script: str,
        interpreter: str = "bash",
        context: Optional[CommandContext] = None
    ) -> ExecutionResult:
        """Execute a script file"""
        
        import tempfile
        
        # Create temp script
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{interpreter}',
            delete=False
        ) as f:
            f.write(f"#!/bin/{interpreter}\n")
            f.write(script)
            script_path = f.name
        
        try:
            # Make executable
            os.chmod(script_path, 0o755)
            
            # Execute
            result = self.execute(
                f"{interpreter} {script_path}",
                context=context
            )
            
        finally:
            # Cleanup
            try:
                os.unlink(script_path)
            except:
                pass
        
        return result
    
    def execute_python(self, code: str, timeout: int = 30) -> ExecutionResult:
        """Execute Python code"""
        
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            f.write(code)
            script_path = f.name
        
        try:
            return self.execute(
                f"python3 {script_path}",
                context=CommandContext(timeout=timeout)
            )
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get execution history"""
        return [
            {
                "command": r.command[:100],
                "success": r.success,
                "exit_code": r.exit_code,
                "duration_ms": r.duration_ms,
                "timestamp": r.timestamp
            }
            for r in self.execution_history[-limit:]
        ]
    
    def set_safety_level(self, level: SafetyLevel):
        """Change safety level"""
        self.safety_level = level
        logger.info(f"Safety level changed to: {level.name}")
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get executor capabilities"""
        return {
            "safety_level": self.safety_level.name,
            "history_count": len(self.execution_history),
            "can_execute": True,
            "can_run_scripts": True,
            "can_run_python": True,
            "read_only": self.safety_level == SafetyLevel.PARANOID
        }


# Singleton
_executor: Optional[CommandExecutor] = None

def get_executor(safety_level: SafetyLevel = SafetyLevel.SAFE) -> CommandExecutor:
    global _executor
    if _executor is None:
        _executor = CommandExecutor(safety_level)
    return _executor
