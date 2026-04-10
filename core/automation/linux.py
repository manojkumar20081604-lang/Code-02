"""
============================================================
LINUX AUTOMATION
============================================================
Full system control for Linux systems
"""

import subprocess
import shlex
import os
import signal
import psutil
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .base import BaseAutomation, SafetyLevel, ExecutionResult

logger = logging.getLogger("LinuxAutomation")


class LinuxAutomation(BaseAutomation):
    """
    Full automation for Linux systems
    Supports bash, pacman, apt, systemctl, and all Linux tools
    """
    
    # Blocked dangerous commands
    BLOCKED_PATTERNS = [
        r"rm\s+-rf\s+/\s*",
        r"rm\s+-rf\s+/\*",
        r":\(\)\s*:\s*\|",  # Fork bomb
        r"mkfs",
        r"dd\s+if=",
        r">\s*/dev/sd[a-z]",
    ]
    
    # Commands requiring elevated permissions
    ELEVATED_COMMANDS = [
        "sudo", "su ", "useradd", "userdel", "usermod",
        "chmod 777", "chown", "visudo",
        "iptables", "ufw", "firewall-cmd",
        "systemctl --user", "service ",
        "kill -9", "killall",
        "shutdown", "reboot", "init 0", "init 6",
    ]
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.SAFE):
        super().__init__(safety_level)
        self.shell = "/bin/bash"
        logger.info("LinuxAutomation initialized")
    
    def _validate_command(self, command: str) -> tuple[bool, str]:
        """Validate command against safety rules"""
        
        cmd_lower = command.lower()
        
        # Check blocked patterns
        import re
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, cmd_lower):
                return False, f"Blocked dangerous pattern: {pattern}"
        
        # Check safety level for elevated commands
        if self.safety_level.value < SafetyLevel.ELEVATED.value:
            for cmd in self.ELEVATED_COMMANDS:
                if cmd.lower() in cmd_lower:
                    return False, f"Command requires elevated permissions: {cmd}"
        
        return True, "OK"
    
    def execute(self, command: str, timeout: int = 60) -> ExecutionResult:
        """Execute a Linux command"""
        
        # Validate
        safe, reason = self._validate_command(command)
        if not safe:
            return self._error_result(command, reason, "SafetyBlocked")
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                executable=self.shell,
                capture_output=True,
                text=True,
                timeout=timeout,
                env=os.environ.copy()
            )
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                command=command,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_ms=duration
            )
            
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = self._error_result(command, f"Timeout after {timeout}s", "Timeout", duration)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = self._error_result(command, str(e), "Exception", duration)
        
        self._add_to_history(exec_result)
        return exec_result
    
    def execute_script(self, script: str, interpreter: str = "bash") -> ExecutionResult:
        """Execute a shell script"""
        
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix=f'.{interpreter}',
            delete=False
        ) as f:
            f.write(f"#!/bin/{interpreter}\n")
            f.write(script)
            script_path = f.name
        
        try:
            os.chmod(script_path, 0o755)
            return self.execute(f"{interpreter} {script_path}")
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
    
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
            return self.execute(f"python3 {script_path}", timeout=timeout)
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
    
    def get_process_list(self) -> List[Dict]:
        """Get running processes using psutil"""
        
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
                try:
                    info = proc.info
                    processes.append({
                        "pid": info['pid'],
                        "name": info['name'],
                        "user": info['username'],
                        "cpu": info['cpu_percent'],
                        "memory": info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except:
            # Fallback to ps command
            result = self.execute("ps aux --no-headers | head -50")
            if result.success:
                for line in result.stdout.strip().split('\n'):
                    parts = line.split()
                    if len(parts) >= 11:
                        processes.append({
                            "pid": parts[1],
                            "name": " ".join(parts[10:])[:50],
                            "user": parts[0],
                            "cpu": parts[2],
                            "memory": parts[3]
                        })
        
        return processes[:50]
    
    def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        
        info = {}
        
        # CPU info
        result = self.execute("nproc")
        info["cpu_cores"] = int(result.stdout.strip()) if result.success else "Unknown"
        
        # Memory
        result = self.execute("free -m")
        if result.success:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                mem_parts = lines[1].split()
                info["memory_total_mb"] = int(mem_parts[1])
                info["memory_used_mb"] = int(mem_parts[2])
        
        # Disk
        result = self.execute("df -h / --output=source,size,used,avail")
        if result.success:
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                parts = lines[1].split()
                info["disk_total"] = parts[1]
                info["disk_used"] = parts[2]
                info["disk_available"] = parts[3]
        
        # Load average
        result = self.execute("cat /proc/loadavg")
        if result.success:
            info["load_average"] = result.stdout.strip().split()[0:3]
        
        # Uptime
        result = self.execute("uptime -p")
        info["uptime"] = result.stdout.strip() if result.success else "Unknown"
        
        return info
    
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        return os.path.exists(path)
    
    def read_file(self, path: str) -> str:
        """Read file contents"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
    
    def write_file(self, path: str, content: str) -> bool:
        """Write to file"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return False
    
    def manage_service(self, service: str, action: str) -> ExecutionResult:
        """Manage system services (systemctl)"""
        
        if self.safety_level.value < SafetyLevel.ELEVATED.value:
            return self._error_result(
                f"systemctl {action} {service}",
                "Service management requires elevated permissions",
                "PermissionDenied"
            )
        
        valid_actions = ["start", "stop", "restart", "enable", "disable", "status"]
        if action not in valid_actions:
            return self._error_result(
                f"systemctl {action} {service}",
                f"Invalid action. Use: {valid_actions}",
                "InvalidAction"
            )
        
        return self.execute(f"sudo systemctl {action} {service}")
    
    def install_package(self, package: str, use_sudo: bool = True) -> ExecutionResult:
        """Install a package using appropriate package manager"""
        
        # Detect package manager
        if os.path.exists("/etc/arch-release"):
            cmd = f"{'sudo ' if use_sudo else ''}pacman -S --noconfirm {package}"
        elif os.path.exists("/etc/debian_version"):
            cmd = f"{'sudo ' if use_sudo else ''}apt-get install -y {package}"
        elif os.path.exists("/etc/fedora-release"):
            cmd = f"{'sudo ' if use_sudo else ''}dnf install -y {package}"
        else:
            cmd = f"pip install {package}"  # Fallback
        
        return self.execute(cmd)
    
    def kill_process(self, pid: int, force: bool = False) -> ExecutionResult:
        """Kill a process"""
        
        if self.safety_level.value < SafetyLevel.ELEVATED.value:
            return self._error_result(
                f"kill{' -9' if force else ''} {pid}",
                "Process killing requires elevated permissions",
                "PermissionDenied"
            )
        
        signal = "-9" if force else ""
        return self.execute(f"kill {signal} {pid}")
    
    def _error_result(self, command: str, error: str, error_type: str, duration: float = 0) -> ExecutionResult:
        """Create error result"""
        return ExecutionResult(
            success=False,
            command=command,
            stdout="",
            stderr=error,
            exit_code=-1,
            duration_ms=duration,
            error_type=error_type
        )
    
    def _add_to_history(self, result: ExecutionResult):
        """Add result to history"""
        self.execution_history.append(result)
        if len(self.execution_history) > self.max_history:
            self.execution_history = self.execution_history[-self.max_history:]
