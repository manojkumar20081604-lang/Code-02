"""
============================================================
ACTION EXECUTOR - Operating System Interaction
============================================================
Executes terminal commands, manages files, runs applications
"""

import os
import subprocess
import asyncio
import platform
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger("ActionExecutor")


@dataclass
class ActionResult:
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    duration: float = 0.0


class ActionExecutor:
    """
    Executes actions at the operating system level
    - Terminal commands
    - File operations
    - Application launching
    - Script execution
    """
    
    def __init__(self):
        self.os_type = platform.system().lower()
        self.execution_history: List[ActionResult] = []
        self.env_vars = os.environ.copy()
        
        logger.info(f"ActionExecutor initialized on {self.os_type}")
    
    async def execute_command(self, command: str, shell: bool = True) -> ActionResult:
        """Execute a terminal command"""
        
        import time
        start_time = time.time()
        
        try:
            if self.os_type == "windows":
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=60
                )
            else:
                result = subprocess.run(
                    command,
                    shell=shell,
                    capture_output=True,
                    text=True,
                    timeout=60,
                    env=self.env_vars
                )
            
            duration = time.time() - start_time
            
            action_result = ActionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                exit_code=result.returncode,
                duration=duration
            )
            
            self.execution_history.append(action_result)
            
            return action_result
            
        except subprocess.TimeoutExpired:
            return ActionResult(
                success=False,
                output="",
                error="Command timed out after 60 seconds",
                exit_code=-1,
                duration=time.time() - start_time
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                duration=time.time() - start_time
            )
    
    async def execute_python(self, code: str) -> ActionResult:
        """Execute Python code"""
        
        import time
        start_time = time.time()
        
        try:
            result = subprocess.run(
                ["python", "-c", code],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            return ActionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                exit_code=result.returncode,
                duration=time.time() - start_time
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1,
                duration=time.time() - start_time
            )
    
    async def read_file(self, file_path: str) -> ActionResult:
        """Read file contents"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return ActionResult(
                success=True,
                output=content,
                exit_code=0
            )
        except FileNotFoundError:
            return ActionResult(
                success=False,
                output="",
                error=f"File not found: {file_path}",
                exit_code=1
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1
            )
    
    async def write_file(self, file_path: str, content: str) -> ActionResult:
        """Write content to file"""
        
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return ActionResult(
                success=True,
                output=f"File written: {file_path}",
                exit_code=0
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1
            )
    
    async def list_directory(self, path: str = ".") -> ActionResult:
        """List directory contents"""
        
        try:
            items = os.listdir(path)
            formatted = "\n".join([
                f"{'[DIR]' if os.path.isdir(os.path.join(path, i)) else '[FILE]'} {i}"
                for i in sorted(items)
            ])
            
            return ActionResult(
                success=True,
                output=formatted,
                exit_code=0
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1
            )
    
    async def create_directory(self, path: str) -> ActionResult:
        """Create a directory"""
        
        try:
            os.makedirs(path, exist_ok=True)
            
            return ActionResult(
                success=True,
                output=f"Directory created: {path}",
                exit_code=0
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1
            )
    
    async def delete_file(self, file_path: str) -> ActionResult:
        """Delete a file"""
        
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                return ActionResult(
                    success=True,
                    output=f"File deleted: {file_path}",
                    exit_code=0
                )
            elif os.path.isdir(file_path):
                import shutil
                shutil.rmtree(file_path)
                return ActionResult(
                    success=True,
                    output=f"Directory deleted: {file_path}",
                    exit_code=0
                )
            else:
                return ActionResult(
                    success=False,
                    output="",
                    error=f"Path not found: {file_path}",
                    exit_code=1
                )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=1
            )
    
    async def run_script(self, script_path: str, args: List[str] = None) -> ActionResult:
        """Run a script file"""
        
        ext = os.path.splitext(script_path)[1].lower()
        
        if ext == ".py":
            cmd = ["python", script_path]
        elif ext in [".sh", ".bash"]:
            cmd = ["bash", script_path]
        elif ext == ".ps1":
            cmd = ["powershell", "-File", script_path]
        elif ext in [".bat", ".cmd"]:
            cmd = [script_path]
        else:
            return ActionResult(
                success=False,
                output="",
                error=f"Unknown script type: {ext}",
                exit_code=1
            )
        
        if args:
            cmd.extend(args)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            return ActionResult(
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                exit_code=result.returncode
            )
        except Exception as e:
            return ActionResult(
                success=False,
                output="",
                error=str(e),
                exit_code=-1
            )
    
    def get_history(self, limit: int = 10) -> List[Dict]:
        """Get execution history"""
        return [
            {
                "success": h.success,
                "output": h.output[:200] + "..." if len(h.output) > 200 else h.output,
                "error": h.error,
                "exit_code": h.exit_code,
                "duration": f"{h.duration:.2f}s"
            }
            for h in self.execution_history[-limit:]
        ]
    
    def get_system_info(self) -> Dict:
        """Get system information"""
        return {
            "os": self.os_type,
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "architecture": platform.machine()
        }
