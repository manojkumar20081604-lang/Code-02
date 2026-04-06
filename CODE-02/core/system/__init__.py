"""
============================================================
SYSTEM MODULE - Core System Components
============================================================
Contains: Executor, Installer, Decision Engine, Main Loop
"""

from .executor import CommandExecutor, SafetyLevel, ExecutionResult, CommandContext
from .installer import AutonomousInstaller, PackageManager, InstallResult, Package
from .decision import DecisionEngine, Intent, Decision
from .main_loop import Code02Loop

__all__ = [
    # Executor
    "CommandExecutor",
    "SafetyLevel",
    "ExecutionResult",
    "CommandContext",
    "get_executor",
    # Installer
    "AutonomousInstaller",
    "PackageManager",
    "InstallResult",
    "Package",
    "get_installer",
    # Decision
    "DecisionEngine",
    "Intent",
    "Decision",
    "get_decision_engine",
    # Main Loop
    "Code02Loop",
]
