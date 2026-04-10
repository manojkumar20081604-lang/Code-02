"""
============================================================
WINDOWS AUTOMATION
============================================================
Automation for Windows systems using PowerShell/CMD
"""

import subprocess
import os
import psutil
from typing import Dict, List, Optional
from datetime import datetime
import logging

from .base import BaseAutomation, SafetyLevel, ExecutionResult

logger = logging.getLogger("WindowsAutomation")


class WindowsAutomation(BaseAutomation):
    """
    Automation for Windows systems
    Uses PowerShell and CMD for system control
    """
    
    # Blocked dangerous commands
    BLOCKED_PATTERNS = [
        r"format\s+[a-z]:",  # Format drives
        r"del\s+/[sq]\s+/f\s+/s\s+/q\s+\\",  # Recursive delete
        r"rd\s+/s\s+/q\s+\\",  # Remove directories
    ]
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.SAFE):
        super().__init__(safety_level)
        self.powershell = "powershell.exe"
        self.use_powershell = True
        logger.info("WindowsAutomation initialized")
    
    def _validate_command(self, command: str) -> tuple[bool, str]:
        """Validate command against safety rules"""
        
        import re
        cmd_lower = command.lower()
        
        for pattern in self.BLOCKED_PATTERNS:
            if re.search(pattern, cmd_lower, re.IGNORECASE):
                return False, f"Blocked dangerous pattern: {pattern}"
        
        return True, "OK"
    
    def execute(self, command: str, timeout: int = 60) -> ExecutionResult:
        """Execute a Windows command"""
        
        # Validate
        safe, reason = self._validate_command(command)
        if not safe:
            return self._error_result(command, reason, "SafetyBlocked")
        
        start_time = datetime.now()
        
        try:
            # Use PowerShell for better functionality
            if self.use_powershell and not command.strip().lower().startswith(("cmd", "dir", "type", "copy", "move")):
                cmd = f'powershell.exe -Command "{command}"'
            else:
                cmd = command
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
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
    
    def execute_powershell(self, script: str, timeout: int = 60) -> ExecutionResult:
        """Execute PowerShell script"""
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                ["powershell.exe", "-Command", script],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            exec_result = ExecutionResult(
                success=result.returncode == 0,
                command=script,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                duration_ms=duration
            )
            
        except subprocess.TimeoutExpired:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = self._error_result(script, f"Timeout after {timeout}s", "Timeout", duration)
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds() * 1000
            exec_result = self._error_result(script, str(e), "Exception", duration)
        
        self._add_to_history(exec_result)
        return exec_result
    
    def execute_script(self, script: str, interpreter: str = "powershell") -> ExecutionResult:
        """Execute a script (PowerShell or CMD)"""
        
        if interpreter == "powershell":
            return self.execute_powershell(script)
        else:
            return self.execute(script)
    
    def execute_python(self, code: str, timeout: int = 30) -> ExecutionResult:
        """Execute Python code"""
        
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False,
            encoding='utf-8'
        ) as f:
            f.write(code)
            script_path = f.name
        
        try:
            return self.execute(f'python "{script_path}"', timeout=timeout)
        finally:
            try:
                os.unlink(script_path)
            except:
                pass
    
    def get_process_list(self) -> List[Dict]:
        """Get running processes"""
        
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
        except Exception as e:
            logger.error(f"Error getting processes: {e}")
        
        return processes[:50]
    
    def get_system_info(self) -> Dict:
        """Get Windows system information"""
        
        info = {}
        
        # CPU cores
        result = self.execute_powershell("(Get-CimInstance Win32_ComputerSystem).NumberOfLogicalProcessors")
        if result.success:
            try:
                info["cpu_cores"] = int(result.stdout.strip())
            except:
                pass
        
        # Memory
        result = self.execute_powershell("""
            $os = Get-CimInstance Win32_OperatingSystem
            @{
                Total = [math]::Round($os.TotalVisibleMemorySize / 1MB, 2)
                Free = [math]::Round($os.FreePhysicalMemory / 1MB, 2)
            } | ConvertTo-Json
        """)
        if result.success:
            import json
            try:
                mem = json.loads(result.stdout.strip())
                info["memory_total_gb"] = mem.get("Total", "Unknown")
                info["memory_free_gb"] = mem.get("Free", "Unknown")
            except:
                pass
        
        # Disk
        result = self.execute_powershell("""
            Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'" | 
            Select-Object Size,FreeSpace | 
            ConvertTo-Json
        """)
        if result.success:
            import json
            try:
                disk = json.loads(result.stdout.strip())
                info["disk_total_gb"] = round(int(disk.get("Size", 0)) / (1024**3), 2)
                info["disk_free_gb"] = round(int(disk.get("FreeSpace", 0)) / (1024**3), 2)
            except:
                pass
        
        # Computer name
        result = self.execute_powershell("$env:COMPUTERNAME")
        if result.success:
            info["hostname"] = result.stdout.strip()
        
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
        """Manage Windows services"""
        
        valid_actions = ["start", "stop", "restart", "status"]
        if action not in valid_actions:
            return self._error_result(
                f"service {action} {service}",
                f"Invalid action. Use: {valid_actions}",
                "InvalidAction"
            )
        
        return self.execute_powershell(f"{action.title()}-Service -Name '{service}'")
    
    def install_package(self, package: str) -> ExecutionResult:
        """Install package using pip (Windows)"""
        
        return self.execute(f'pip install {package}')
    
    def kill_process(self, pid: int, force: bool = False) -> ExecutionResult:
        """Kill a process"""
        
        return self.execute(f"taskkill{' /F' if force else ''} /PID {pid}")
    
    def get_running_services(self) -> List[Dict]:
        """Get Windows services"""
        
        result = self.execute_powershell("""
            Get-Service | Select-Object Name, Status, DisplayName | 
            ConvertTo-Json
        """)
        
        if result.success:
            import json
            try:
                services = json.loads(result.stdout.strip())
                if isinstance(services, dict):
                    return [services]
                return services
            except:
                pass
        
        return []
    
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
