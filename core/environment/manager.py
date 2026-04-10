"""
============================================================
ENVIRONMENT MANAGER - Auto-Install Dependencies
============================================================
Automatically detects, downloads, and installs required tools
"""

import subprocess
import os
import json
import re
import platform
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PackageManager(Enum):
    APT = "apt"
    PACMAN = "pacman"
    DNF = "dnf"
    YUM = "yum"
    BREW = "brew"
    PIP = "pip"
    NPM = "npm"
    CARGO = "cargo"
    UNKNOWN = "unknown"


@dataclass
class Package:
    name: str
    manager: PackageManager
    installed: bool = False
    version: Optional[str] = None
    required: bool = True


@dataclass
class InstallResult:
    success: bool
    package: str
    manager: str
    output: str
    error: Optional[str] = None


class EnvironmentManager:
    """
    Automatically manages environment setup
    - Detects missing dependencies
    - Installs packages using appropriate package manager
    - Sets up Python venv, Node.js environments
    - Downloads AI models and tools
    - Fixes broken setups automatically
    """
    
    def __init__(self):
        self.system = platform.system().lower()
        self.distribution = self._detect_distribution()
        self.package_manager = self._detect_package_manager()
        self.installed_packages: Dict[str, Package] = {}
        self.python_version = self._check_python_version()
        
    def _detect_distribution(self) -> str:
        """Detect Linux distribution"""
        if os.path.exists("/etc/arch-release"):
            return "arch"
        elif os.path.exists("/etc/debian_version"):
            return "debian"
        elif os.path.exists("/etc/fedora-release"):
            return "fedora"
        elif os.path.exists("/etc/redhat-release"):
            return "redhat"
        elif os.path.exists("/etc/SuSE-release"):
            return "suse"
        return "unknown"
    
    def _detect_package_manager(self) -> PackageManager:
        """Detect available package managers"""
        managers = [
            (["pacman", "-h"], PackageManager.PACMAN),
            (["apt-get", "--version"], PackageManager.APT),
            (["dnf", "--version"], PackageManager.DNF),
            (["yum", "--version"], PackageManager.YUM),
            (["brew", "--version"], PackageManager.BREW),
        ]
        
        for cmd, manager in managers:
            if self._command_exists(cmd[0]):
                return manager
        
        return PackageManager.UNKNOWN
    
    def _command_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        result = subprocess.run(
            f"which {cmd} 2>/dev/null",
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
    
    def _check_python_version(self) -> Tuple[int, int]:
        """Check Python version"""
        import sys
        return (sys.version_info.major, sys.version_info.minor)
    
    async def check_dependencies(self, requirements: List[str]) -> Dict[str, bool]:
        """Check which dependencies are missing"""
        results = {}
        
        for req in requirements:
            # Parse requirement
            if req.startswith("pip:"):
                pkg = req[4:]
                results[pkg] = self._check_python_package(pkg)
            elif req.startswith("npm:"):
                pkg = req[4:]
                results[pkg] = self._check_npm_package(pkg)
            elif req.startswith("sys:"):
                pkg = req[4:]
                results[pkg] = self._command_exists(pkg)
            else:
                # Check as system command
                results[req] = self._command_exists(req)
        
        return results
    
    def _check_python_package(self, package: str) -> bool:
        """Check if Python package is installed"""
        result = subprocess.run(
            f"pip show {package}",
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
    
    def _check_npm_package(self, package: str) -> bool:
        """Check if npm package is installed globally"""
        result = subprocess.run(
            f"npm list -g {package}",
            shell=True,
            capture_output=True
        )
        return result.returncode == 0
    
    async def install(
        self, 
        package: str, 
        package_manager: Optional[PackageManager] = None,
        sudo: bool = True
    ) -> InstallResult:
        """Install a package using appropriate manager"""
        
        manager = package_manager or self._detect_manager_for_package(package)
        
        cmd_prefix = "sudo " if sudo and os.getuid() != 0 else ""
        
        if manager == PackageManager.PIP:
            cmd = f"{cmd_prefix}pip install {package}"
        elif manager == PackageManager.NPM:
            cmd = f"{cmd_prefix}npm install -g {package}"
        elif manager == PackageManager.APT:
            cmd = f"{cmd_prefix}apt-get install -y {package}"
        elif manager == PackageManager.PACMAN:
            cmd = f"{cmd_prefix}pacman -S --noconfirm {package}"
        elif manager == PackageManager.DNF:
            cmd = f"{cmd_prefix}dnf install -y {package}"
        elif manager == PackageManager.CARGO:
            cmd = f"cargo install {package}"
        else:
            return InstallResult(
                success=False,
                package=package,
                manager="unknown",
                output="",
                error="No suitable package manager found"
            )
        
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )
        
        return InstallResult(
            success=result.returncode == 0,
            package=package,
            manager=manager.value,
            output=result.stdout,
            error=result.stderr if result.returncode != 0 else None
        )
    
    def _detect_manager_for_package(self, package: str) -> PackageManager:
        """Detect appropriate package manager for a package"""
        
        # Python packages
        if self._is_python_package(package):
            return PackageManager.PIP
        
        # Node.js packages
        if package in ["node", "npm"] or self._is_nodejs_package(package):
            return PackageManager.NPM
        
        # Rust packages
        if package.endswith("-rs") or self._is_rust_package(package):
            return PackageManager.CARGO
        
        # System packages
        return self.package_manager
    
    def _is_python_package(self, package: str) -> bool:
        """Check if package is a Python package"""
        python_indicators = [
            "flask", "django", "fastapi", "numpy", "pandas", "torch",
            "tensorflow", "requests", "aiohttp", "openai", "anthropic",
            "transformers", "sentence-transformers", "chromadb", "sqlite3"
        ]
        return any(pkg in package.lower() for pkg in python_indicators)
    
    def _is_nodejs_package(self, package: str) -> bool:
        """Check if package is a Node.js package"""
        return package in ["react", "vue", "angular", "electron", "vite", "webpack"]
    
    def _is_rust_package(self, package: str) -> bool:
        """Check if package is a Rust crate"""
        return "-" in package and not os.path.exists(package)
    
    async def setup_python_venv(self, path: str, requirements: List[str] = None) -> bool:
        """Create Python virtual environment and install requirements"""
        
        # Create venv
        result = subprocess.run(
            f"python -m venv {path}",
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            return False
        
        # Install requirements
        if requirements:
            req_file = os.path.join(path, "requirements.txt")
            with open(req_file, "w") as f:
                f.write("\n".join(requirements))
            
            pip_path = os.path.join(path, "bin", "pip")
            if os.name == "nt":
                pip_path = os.path.join(path, "Scripts", "pip.exe")
            
            result = subprocess.run(
                f"{pip_path} install -r {req_file}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return result.returncode == 0
        
        return True
    
    async def download_ai_model(self, model_name: str, backend: str = "ollama") -> Dict:
        """Download AI models (Ollama, HuggingFace)"""
        
        result = {
            "model": model_name,
            "backend": backend,
            "status": "pending"
        }
        
        if backend == "ollama":
            # Pull model using Ollama
            cmd_result = subprocess.run(
                f"ollama pull {model_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            result["success"] = cmd_result.returncode == 0
            result["output"] = cmd_result.stdout
            result["error"] = cmd_result.stderr if cmd_result.returncode != 0 else None
            
        elif backend == "huggingface":
            # Download using huggingface-cli
            cmd_result = subprocess.run(
                f"huggingface-cli download {model_name}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=3600
            )
            result["success"] = cmd_result.returncode == 0
            result["output"] = cmd_result.stdout
        
        return result
    
    async def fix_broken_setup(self) -> List[str]:
        """Attempt to fix broken system setups"""
        fixes_applied = []
        
        # Fix pip
        if not self._command_exists("pip"):
            result = await self.install("python3-pip")
            if result.success:
                fixes_applied.append("Installed pip")
        
        # Fix broken packages (Arch Linux)
        if self.distribution == "arch":
            result = subprocess.run(
                "sudo pacman -Sy --noconfirm",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                fixes_applied.append("Updated package database")
        
        return fixes_applied
    
    async def get_system_info(self) -> Dict:
        """Get comprehensive system information"""
        return {
            "os": self.system,
            "distribution": self.distribution,
            "package_manager": self.package_manager.value,
            "python_version": f"{self.python_version[0]}.{self.python_version[1]}",
            "architecture": platform.machine(),
            "hostname": platform.node(),
            "kernel": platform.release(),
            "memory_total": self._get_memory_info(),
            "disk_space": self._get_disk_info()
        }
    
    def _get_memory_info(self) -> Dict:
        """Get memory information"""
        try:
            with open("/proc/meminfo", "r") as f:
                lines = f.readlines()
            
            info = {}
            for line in lines:
                if ":" in line:
                    key, value = line.split(":", 1)
                    if "MemTotal" in key:
                        info["total_kb"] = int(value.strip().split()[0])
                    elif "MemAvailable" in key:
                        info["available_kb"] = int(value.strip().split()[0])
            
            return info
        except:
            return {}
    
    def _get_disk_info(self) -> Dict:
        """Get disk space information"""
        try:
            result = subprocess.run(
                "df -h / --output=size,used,avail",
                shell=True,
                capture_output=True,
                text=True
            )
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                parts = lines[1].split()
                return {
                    "size": parts[0],
                    "used": parts[1],
                    "available": parts[2]
                }
        except:
            pass
        return {}
    
    def get_required_packages(self) -> List[str]:
        """Get list of required packages for Code-02"""
        return [
            # System
            "git", "curl", "wget", "build-essential",
            # Python
            "pip:flask>=2.3", "pip:flask-cors>=4.0",
            "pip:fastapi>=0.100", "pip:uvicorn>=0.23",
            "pip:sqlalchemy>=2.0", "pip:aiosqlite>=0.19",
            "pip:aiohttp>=3.8", "pip:redis>=4.5",
            # AI
            "pip:ollama>=0.1", "pip:langchain>=0.1",
            "pip:transformers>=4.30", "pip:chromadb>=0.4",
            # Tools
            "npm:electron>=28.0", "npm:vite>=5.0"
        ]


# Singleton instance
_env_manager: Optional[EnvironmentManager] = None

def get_env_manager() -> EnvironmentManager:
    global _env_manager
    if _env_manager is None:
        _env_manager = EnvironmentManager()
    return _env_manager
