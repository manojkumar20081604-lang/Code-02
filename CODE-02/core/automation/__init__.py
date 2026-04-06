"""
============================================================
UNIFIED AUTOMATION MODULE
============================================================
Automatically selects the correct OS implementation
"""

from typing import Dict, Any, Optional
import logging

from .base import BaseAutomation, SafetyLevel, ExecutionResult
from .linux import LinuxAutomation
from .windows import WindowsAutomation

logger = logging.getLogger("Automation")

# Lazy import to avoid circular imports
_automation_instance: Optional[BaseAutomation] = None


def get_automation(safety_level: SafetyLevel = SafetyLevel.SAFE) -> BaseAutomation:
    """
    Get the appropriate automation instance for the current OS
    
    Usage:
        automation = get_automation()
        result = automation.execute("ls -la")
    """
    global _automation_instance
    
    if _automation_instance is None:
        from core.platform import detect
        os_detector = detect.get_os()
        
        if os_detector.is_linux:
            _automation_instance = LinuxAutomation(safety_level)
            logger.info("Using LinuxAutomation")
        elif os_detector.is_windows:
            _automation_instance = WindowsAutomation(safety_level)
            logger.info("Using WindowsAutomation")
        else:
            # Default to LinuxAutomation (works on most systems)
            _automation_instance = LinuxAutomation(safety_level)
            logger.warning("Unknown OS, defaulting to LinuxAutomation")
    
    return _automation_instance


def reset_automation():
    """Reset automation instance (useful for testing)"""
    global _automation_instance
    _automation_instance = None


# Convenience functions that delegate to the automation instance
def execute(command: str, timeout: int = 60) -> ExecutionResult:
    """Execute a command on the current OS"""
    return get_automation().execute(command, timeout)


def execute_script(script: str, interpreter: str = "bash") -> ExecutionResult:
    """Execute a script on the current OS"""
    return get_automation().execute_script(script, interpreter)


def get_process_list() -> list:
    """Get running processes"""
    return get_automation().get_process_list()


def get_system_info() -> Dict:
    """Get system information"""
    return get_automation().get_system_info()


def file_exists(path: str) -> bool:
    """Check if file exists"""
    return get_automation().file_exists(path)


def read_file(path: str) -> str:
    """Read file contents"""
    return get_automation().read_file(path)


def write_file(path: str, content: str) -> bool:
    """Write to file"""
    return get_automation().write_file(path, content)


def install_package(package: str) -> ExecutionResult:
    """Install a package"""
    return get_automation().install_package(package)


def kill_process(pid: int, force: bool = False) -> ExecutionResult:
    """Kill a process"""
    return get_automation().kill_process(pid, force)


__all__ = [
    "BaseAutomation",
    "SafetyLevel", 
    "ExecutionResult",
    "get_automation",
    "reset_automation",
    "execute",
    "execute_script",
    "get_process_list",
    "get_system_info",
    "file_exists",
    "read_file",
    "write_file",
    "install_package",
    "kill_process",
    "LinuxAutomation",
    "WindowsAutomation",
]
