"""
============================================================
CROSS-PLATFORM AUTOMATION INTERFACE
============================================================
Abstract interface for OS-specific automation
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger("Automation")


class SafetyLevel(Enum):
    PARANOID = 0   # Read-only operations
    SAFE = 1       # Standard safe operations
    ELEVATED = 2   # System changes allowed
    DANGEROUS = 3  # All operations allowed


@dataclass
class ExecutionResult:
    success: bool
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    error_type: Optional[str] = None


class BaseAutomation(ABC):
    """
    Abstract base class for OS-specific automation
    All implementations must follow this interface
    """
    
    def __init__(self, safety_level: SafetyLevel = SafetyLevel.SAFE):
        self.safety_level = safety_level
        self.execution_history: List[ExecutionResult] = []
        self.max_history = 500
    
    @abstractmethod
    def execute(self, command: str, timeout: int = 60) -> ExecutionResult:
        """Execute a command"""
        pass
    
    @abstractmethod
    def execute_script(self, script: str, interpreter: str = "bash") -> ExecutionResult:
        """Execute a script"""
        pass
    
    @abstractmethod
    def get_process_list(self) -> List[Dict]:
        """Get running processes"""
        pass
    
    @abstractmethod
    def get_system_info(self) -> Dict:
        """Get system information"""
        pass
    
    @abstractmethod
    def file_exists(self, path: str) -> bool:
        """Check if file exists"""
        pass
    
    @abstractmethod
    def read_file(self, path: str) -> str:
        """Read file contents"""
        pass
    
    @abstractmethod
    def write_file(self, path: str, content: str) -> bool:
        """Write to file"""
        pass
    
    def get_history(self, limit: int = 50) -> List[Dict]:
        """Get execution history"""
        return [
            {
                "command": r.command[:100],
                "success": r.success,
                "exit_code": r.exit_code,
                "duration_ms": r.duration_ms
            }
            for r in self.execution_history[-limit:]
        ]
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get automation capabilities"""
        return {
            "safety_level": self.safety_level.name,
            "can_execute": True,
            "can_run_scripts": True,
            "can_manage_processes": True,
            "can_manage_files": True,
            "history_count": len(self.execution_history)
        }
    
    def set_safety_level(self, level: SafetyLevel):
        """Change safety level"""
        self.safety_level = level
        logger.info(f"Safety level set to: {level.name}")
