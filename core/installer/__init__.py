"""
============================================================
CROSS-PLATFORM INSTALLER
============================================================
Auto-detects OS and uses appropriate package manager
"""

import subprocess
import os
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger("Installer")


class PackageManager(Enum):
    PACMAN = "pacman"
    APT = "apt"
    DNF = "dnf"
    YUM = "yum"
    BREW = "brew"
    PIP = "pip"
    NPM = "npm"
    WINGET = "winget"
    CHOCO = "choco"
    UNKNOWN = "unknown"


@dataclass
class InstallResult:
    success: bool
    package: str
    manager: str
    stdout: str
    stderr: str
    exit_code: int


@dataclass
class DependencyCheck:
    package: str
    installed: bool
    manager: PackageManager


class BaseInstaller:
    """Base installer class"""
    
    def __init__(self):
        self.os_type = self._detect_os()
        self.distribution = self._detect_distro()
        self.package_manager = self._detect_package_manager()
        self.install_history: List[InstallResult] = []
        self.max_retries = 2
    
    def _detect_os(self) -> str:
        """Detect OS"""
        if os.name == "nt":
            return "windows"
        elif os.name == "posix":
            return "linux" if os.path.exists("/etc/os-release") else "macos"
        return "unknown"
    
    def _detect_distro(self) -> Optional[str]:
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
        elif os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release") as f:
                    content = f.read().lower()
                    if "ubuntu" in content:
                        return "ubuntu"
            except:
                pass
        return None
    
    def _detect_package_manager(self) -> PackageManager:
        """Detect available package manager"""
        managers = [
            ("pacman", PackageManager.PACMAN),
            ("apt-get", PackageManager.APT),
            ("dnf", PackageManager.DNF),
            ("yum", PackageManager.YUM),
            ("brew", PackageManager.BREW),
            ("winget", PackageManager.WINGET),
            ("choco", PackageManager.CHOCO),
        ]
        
        for cmd, manager in managers:
            if self._command_exists(cmd):
                return manager
        
        return PackageManager.UNKNOWN
    
    def _command_exists(self, cmd: str) -> bool:
        """Check if command exists"""
        try:
            result = subprocess.run(
                ["where" if os.name == "nt" else "which", cmd],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def check_dependency(self, package: str) -> bool:
        """Check if dependency is installed"""
        raise NotImplementedError
    
    def install(self, package: str, upgrade: bool = False) -> InstallResult:
        """Install a package"""
        raise NotImplementedError
    
    def get_status(self) -> Dict[str, Any]:
        """Get installer status"""
        return {
            "os": self.os_type,
            "distro": self.distribution,
            "package_manager": self.package_manager.value,
            "installed_count": len([r for r in self.install_history if r.success]),
            "failed_count": len([r for r in self.install_history if not r.success])
        }


class LinuxInstaller(BaseInstaller):
    """Package installer for Linux systems"""
    
    def __init__(self):
        super().__init__()
        self.sudo_available = self._check_sudo()
        logger.info(f"LinuxInstaller: {self.distribution} ({self.package_manager.value})")
    
    def _check_sudo(self) -> bool:
        """Check if sudo is available"""
        if os.getuid() == 0:
            return False  # Already root
        return self._command_exists("sudo")
    
    def check_dependency(self, package: str) -> bool:
        """Check if package is installed"""
        
        # Check Python packages
        if self._is_python_package(package):
            result = subprocess.run(
                f"pip show {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        # Check npm packages
        if self._is_npm_package(package):
            result = subprocess.run(
                f"npm list -g {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        # Check system packages based on manager
        if self.package_manager == PackageManager.PACMAN:
            result = subprocess.run(
                f"pacman -Q {package}",
                shell=True,
                capture_output=True
            )
        elif self.package_manager == PackageManager.APT:
            result = subprocess.run(
                f"dpkg -l {package}",
                shell=True,
                capture_output=True
            )
        elif self.package_manager == PackageManager.DNF:
            result = subprocess.run(
                f"dnf list installed {package}",
                shell=True,
                capture_output=True
            )
        else:
            return self._command_exists(package)
        
        return result.returncode == 0
    
    def _is_python_package(self, package: str) -> bool:
        """Check if it's a Python package"""
        indicators = [
            "flask", "django", "fastapi", "requests", "numpy",
            "pandas", "torch", "aiohttp", "sqlalchemy", "openai"
        ]
        return any(pkg in package.lower() for pkg in indicators)
    
    def _is_npm_package(self, package: str) -> bool:
        """Check if it's an npm package"""
        indicators = ["react", "vue", "angular", "electron", "vite"]
        return any(pkg in package.lower() for pkg in indicators)
    
    def _detect_manager_for_package(self, package: str) -> PackageManager:
        """Detect package manager for a specific package"""
        
        if self._is_python_package(package):
            return PackageManager.PIP
        
        if self._is_npm_package(package):
            return PackageManager.NPM
        
        return self.package_manager
    
    def install(self, package: str, upgrade: bool = False) -> InstallResult:
        """Install a package on Linux"""
        
        manager = self._detect_manager_for_package(package)
        sudo = self.sudo_available and manager != PackageManager.PIP
        
        # Build command
        if manager == PackageManager.PIP:
            cmd = f"pip install {'-U ' if upgrade else ''}{package}"
            sudo_prefix = ""
        elif manager == PackageManager.NPM:
            cmd = f"npm install -g {package}"
            sudo_prefix = f"{'sudo ' if sudo else ''}"
        elif manager == PackageManager.PACMAN:
            cmd = f"sudo pacman -S --noconfirm {package}"
        elif manager == PackageManager.APT:
            cmd = f"sudo apt-get install -y {package}"
        elif manager == PackageManager.DNF:
            cmd = f"sudo dnf install -y {package}"
        else:
            return InstallResult(
                success=False,
                package=package,
                manager="unknown",
                stdout="",
                stderr="No suitable package manager found",
                exit_code=-1
            )
        
        if not cmd.startswith("sudo") and not cmd.startswith("pip"):
            cmd = f"sudo {cmd}" if sudo else cmd
        
        logger.info(f"Installing: {package} using {manager.value}")
        
        # Execute
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
                manager=manager.value,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )
            
            if install_result.success or attempt >= self.max_retries:
                self.install_history.append(install_result)
                return install_result
            
            logger.warning(f"Retry {attempt + 1} for {package}")
        
        return install_result


class WindowsInstaller(BaseInstaller):
    """Package installer for Windows systems"""
    
    def __init__(self):
        super().__init__()
        logger.info(f"WindowsInstaller: {self.package_manager.value}")
    
    def check_dependency(self, package: str) -> bool:
        """Check if package is installed"""
        
        # Check pip
        if self._is_python_package(package):
            result = subprocess.run(
                f"pip show {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        # Check npm
        if self._is_npm_package(package):
            result = subprocess.run(
                f"npm list -g {package}",
                shell=True,
                capture_output=True
            )
            return result.returncode == 0
        
        return False
    
    def _is_python_package(self, package: str) -> bool:
        """Check if it's a Python package"""
        indicators = ["flask", "django", "fastapi", "requests", "numpy"]
        return any(pkg in package.lower() for pkg in indicators)
    
    def _is_npm_package(self, package: str) -> bool:
        """Check if it's an npm package"""
        indicators = ["react", "vue", "angular", "electron", "vite"]
        return any(pkg in package.lower() for pkg in indicators)
    
    def install(self, package: str, upgrade: bool = False) -> InstallResult:
        """Install a package on Windows"""
        
        # Use pip for Python packages
        if self._is_python_package(package):
            cmd = f"pip install {'-U ' if upgrade else ''}{package}"
        elif self._is_npm_package(package):
            cmd = f"npm install -g {package}"
        elif self._command_exists("winget"):
            cmd = f"winget install {package}"
        elif self._command_exists("choco"):
            cmd = f"choco install -y {package}"
        else:
            cmd = f"pip install {package}"  # Fallback
        
        logger.info(f"Installing: {package}")
        
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
            manager="pip" if self._is_python_package(package) else "npm",
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode
        )
        
        self.install_history.append(install_result)
        return install_result


# Unified installer factory
_installer_instance: Optional[BaseInstaller] = None


def get_installer() -> BaseInstaller:
    """Get the appropriate installer for the current OS"""
    global _installer_instance
    
    if _installer_instance is None:
        if os.name == "nt":
            _installer_instance = WindowsInstaller()
        else:
            _installer_instance = LinuxInstaller()
    
    return _installer_instance


def install(package: str, upgrade: bool = False) -> InstallResult:
    """Install a package"""
    return get_installer().install(package, upgrade)


def check_dependency(package: str) -> bool:
    """Check if dependency is installed"""
    return get_installer().check_dependency(package)


def install_many(packages: List[str]) -> Dict[str, InstallResult]:
    """Install multiple packages"""
    results = {}
    for pkg in packages:
        results[pkg] = install(pkg)
    return results


__all__ = [
    "PackageManager",
    "InstallResult",
    "DependencyCheck",
    "BaseInstaller",
    "LinuxInstaller",
    "WindowsInstaller",
    "get_installer",
    "install",
    "check_dependency",
    "install_many",
]
