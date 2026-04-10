"""
============================================================
AUTONOMOUS INSTALLER - Auto-Dependency Management
============================================================
Automatically detects and installs missing dependencies
"""

import subprocess
import os
import re
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger("Installer")


class PackageManager(Enum):
    PACMAN = "pacman"      # Arch Linux
    APT = "apt"            # Debian/Ubuntu
    DNF = "dnf"           # Fedora
    YUM = "yum"           # RedHat/CentOS
    BREW = "brew"         # macOS
    PIP = "pip"           # Python
    NPM = "npm"           # Node.js
    CARGO = "cargo"       # Rust
    UNKNOWN = "unknown"


@dataclass
class Package:
    name: str
    manager: PackageManager
    version: Optional[str] = None
    installed: bool = False
    required: bool = True


@dataclass
class InstallResult:
    success: bool
    package: str
    manager: str
    stdout: str
    stderr: str
    exit_code: int
    timestamp: str


@dataclass
class DependencyCheck:
    package: str
    required: bool
    installed: bool
    manager: PackageManager


class AutonomousInstaller:
    """
    Autonomous installer that:
    - Detects missing dependencies
    - Installs using appropriate package manager
    - Handles errors and retries
    - Verifies installation success
    """
    
    def __init__(self):
        self.os_type = os.name
        self.distribution = self._detect_linux_dist()
        self.package_manager = self._detect_package_manager()
        self.install_history: List[InstallResult] = []
        
        # Retry configuration
        self.max_retries = 2
        self.retry_delay = 2  # seconds
        
        logger.info(f"Installer initialized: {self.distribution} ({self.package_manager.value})")
    
    def _detect_linux_dist(self) -> str:
        """Detect Linux distribution"""
        if os.name == "nt":
            return "windows"
        
        try:
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
            elif os.path.exists("/etc/os-release"):
                with open("/etc/os-release") as f:
                    content = f.read().lower()
                    if "arch" in content:
                        return "arch"
                    elif "ubuntu" in content or "debian" in content:
                        return "debian"
                    elif "fedora" in content:
                        return "fedora"
        except:
            pass
        
        return "unknown"
    
    def _detect_package_manager(self) -> PackageManager:
        """Detect available package manager"""
        checkers = [
            (["pacman", "--version"], PackageManager.PACMAN),
            (["apt-get", "--version"], PackageManager.APT),
            (["dnf", "--version"], PackageManager.DNF),
            (["yum", "--version"], PackageManager.YUM),
            (["brew", "--version"], PackageManager.BREW),
            (["cargo", "--version"], PackageManager.CARGO),
        ]
        
        for cmd, manager in checkers:
            if self._command_exists(cmd[0]):
                return manager
        
        return PackageManager.UNKNOWN
    
    def _command_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            result = subprocess.run(
                f"where {cmd}" if os.name == "nt" else f"which {cmd}",
                shell=True,
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_dependency(self, package: str) -> bool:
        """Check if a dependency is installed"""
        
        # Python packages
        if self._is_python_package(package):
            result = subprocess.run(
                f"pip show {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        # Node packages
        if self._is_npm_package(package):
            result = subprocess.run(
                f"npm list -g {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        # System packages
        if self.package_manager == PackageManager.PACMAN:
            result = subprocess.run(
                f"pacman -Q {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        elif self.package_manager == PackageManager.APT:
            result = subprocess.run(
                f"dpkg -l {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        elif self.package_manager == PackageManager.DNF:
            result = subprocess.run(
                f"dnf list installed {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        # Generic check
        return self._command_exists(package)
    
    def _is_python_package(self, package: str) -> bool:
        """Check if it's a Python package"""
        indicators = [
            "flask", "django", "fastapi", "requests", "numpy",
            "pandas", "torch", "tensorflow", "aiohttp", "sqlalchemy",
            "openai", "anthropic", "ollama", "transformers", "chromadb"
        ]
        return any(pkg in package.lower() for pkg in indicators)
    
    def _is_npm_package(self, package: str) -> bool:
        """Check if it's an npm package"""
        indicators = [
            "react", "vue", "angular", "electron", "vite",
            "webpack", "typescript", "eslint", "nodemon"
        ]
        return any(pkg in package.lower() for pkg in indicators)
    
    def _detect_manager_for_package(self, package: str) -> PackageManager:
        """Detect appropriate package manager"""
        
        if self._is_python_package(package):
            return PackageManager.PIP
        
        if self._is_npm_package(package):
            return PackageManager.NPM
        
        if self.package_manager != PackageManager.UNKNOWN:
            return self.package_manager
        
        return PackageManager.UNKNOWN
    
    def install(
        self,
        package: str,
        manager: Optional[PackageManager] = None,
        sudo: bool = True,
        upgrade: bool = False
    ) -> InstallResult:
        """Install a single package"""
        
        pkg_manager = manager or self._detect_manager_for_package(package)
        
        sudo_prefix = "sudo " if sudo and os.getuid() != 0 else ""
        
        # Build command
        if pkg_manager == PackageManager.PIP:
            cmd = f"pip install {'-U ' if upgrade else ''}{package}"
            sudo_prefix = ""  # pip doesn't need sudo usually
        elif pkg_manager == PackageManager.NPM:
            cmd = f"{sudo_prefix}npm install -g {package}"
        elif pkg_manager == PackageManager.PACMAN:
            cmd = f"{sudo_prefix}pacman -S --noconfirm {package}"
        elif pkg_manager == PackageManager.APT:
            cmd = f"{sudo_prefix}apt-get install -y {package}"
        elif pkg_manager == PackageManager.DNF:
            cmd = f"{sudo_prefix}dnf install -y {package}"
        elif pkg_manager == PackageManager.YUM:
            cmd = f"{sudo_prefix}yum install -y {package}"
        elif pkg_manager == PackageManager.CARGO:
            cmd = f"cargo install {package}"
            sudo_prefix = ""
        else:
            return InstallResult(
                success=False,
                package=package,
                manager="unknown",
                stdout="",
                stderr="No suitable package manager found",
                exit_code=-1,
                timestamp=datetime.now().isoformat()
            )
        
        logger.info(f"Installing: {package} using {pkg_manager.value}")
        
        # Execute with retries
        for attempt in range(self.max_retries + 1):
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            install_result = InstallResult(
                success=result.returncode == 0,
                package=package,
                manager=pkg_manager.value,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                timestamp=datetime.now().isoformat()
            )
            
            if install_result.success or attempt >= self.max_retries:
                self.install_history.append(install_result)
                return install_result
            
            logger.warning(f"Retry {attempt + 1}/{self.max_retries} for {package}")
            import time
            time.sleep(self.retry_delay)
        
        return install_result
    
    async def install_async(
        self,
        package: str,
        manager: Optional[PackageManager] = None
    ) -> InstallResult:
        """Install package asynchronously"""
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.install,
            package,
            manager
        )
    
    def check_multiple(
        self,
        packages: List[str]
    ) -> List[DependencyCheck]:
        """Check multiple dependencies at once"""
        
        results = []
        
        for package in packages:
            installed = self.check_dependency(package)
            manager = self._detect_manager_for_package(package)
            
            results.append(DependencyCheck(
                package=package,
                required=True,
                installed=installed,
                manager=manager
            ))
        
        return results
    
    def install_missing(
        self,
        packages: List[str],
        auto: bool = True
    ) -> Dict[str, InstallResult]:
        """Check and install missing packages"""
        
        missing = []
        
        # Find missing packages
        for package in packages:
            if not self.check_dependency(package):
                missing.append(package)
        
        results = {}
        
        if not missing:
            logger.info("All dependencies already installed")
            return results
        
        logger.info(f"Missing packages: {missing}")
        
        if auto:
            # Auto-install missing
            for package in missing:
                result = self.install(package)
                results[package] = result
                
                if not result.success:
                    logger.error(f"Failed to install {package}: {result.stderr}")
        else:
            # Just report
            for package in missing:
                results[package] = InstallResult(
                    success=False,
                    package=package,
                    manager=self._detect_manager_for_package(package).value,
                    stdout="",
                    stderr="Not installed (auto-install disabled)",
                    exit_code=-1,
                    timestamp=datetime.now().isoformat()
                )
        
        return results
    
    def verify_installation(self, package: str) -> bool:
        """Verify a package was installed successfully"""
        return self.check_dependency(package)
    
    def get_system_packages(self) -> List[str]:
        """Get list of commonly required system packages"""
        return [
            "git", "curl", "wget", "build-essential",
            "python3", "python3-pip", "python3-venv",
            "nodejs", "npm"
        ]
    
    def get_python_packages(self) -> List[str]:
        """Get list of commonly required Python packages"""
        return [
            "flask", "flask-cors",
            "fastapi", "uvicorn",
            "aiohttp", "requests",
            "sqlalchemy", "aiosqlite",
            "pyttsx3", "SpeechRecognition",
            "edge-tts", "pygame"
        ]
    
    def install_all_defaults(self) -> Dict[str, InstallResult]:
        """Install all default dependencies"""
        
        all_packages = []
        all_packages.extend(self.get_system_packages())
        all_packages.extend(self.get_python_packages())
        
        return self.install_missing(all_packages, auto=True)
    
    def get_status(self) -> Dict[str, Any]:
        """Get installer status"""
        return {
            "os_type": self.os_type,
            "distribution": self.distribution,
            "package_manager": self.package_manager.value,
            "total_installed": len([r for r in self.install_history if r.success]),
            "total_failed": len([r for r in self.install_history if not r.success]),
            "history": [
                {
                    "package": r.package,
                    "manager": r.manager,
                    "success": r.success,
                    "timestamp": r.timestamp
                }
                for r in self.install_history[-20:]
            ]
        }


# Singleton
_installer: Optional[AutonomousInstaller] = None

def get_installer() -> AutonomousInstaller:
    global _installer
    if _installer is None:
        _installer = AutonomousInstaller()
    return _installer
