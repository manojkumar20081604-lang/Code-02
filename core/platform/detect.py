"""
============================================================
OS DETECTION MODULE
============================================================
Automatically detects operating system and provides platform info
"""

import platform
import os
import sys
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional, List
import logging

logger = logging.getLogger("OSDetect")


class OSType(Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    UNKNOWN = "unknown"


class LinuxDistro(Enum):
    ARCH = "arch"
    DEBIAN = "debian"
    UBUNTU = "ubuntu"
    FEDORA = "fedora"
    REDHAT = "redhat"
    SUSE = "suse"
    UNKNOWN = "unknown"


@dataclass
class OSInfo:
    os_type: OSType
    distro: Optional[LinuxDistro]
    version: str
    arch: str
    hostname: str
    python_version: str
    capabilities: List[str]


class OSDetector:
    """
    Detects operating system and provides platform information
    """
    
    def __init__(self):
        self._os_type: Optional[OSType] = None
        self._distro: Optional[LinuxDistro] = None
        self._info: Optional[OSInfo] = None
        self._detect()
    
    def _detect(self):
        """Detect OS and populate info"""
        
        system = platform.system().lower()
        
        if system == "windows" or os.name == "nt":
            self._os_type = OSType.WINDOWS
            self._distro = None
            self._info = self._create_info()
            
        elif system == "linux":
            self._os_type = OSType.LINUX
            self._distro = self._detect_linux_distro()
            self._info = self._create_info()
            
        elif system == "darwin":
            self._os_type = OSType.MACOS
            self._distro = None
            self._info = self._create_info()
            
        else:
            self._os_type = OSType.UNKNOWN
            self._distro = None
            self._info = self._create_info()
        
        logger.info(f"OS Detected: {self._os_type.value} ({self._distro.value if self._distro else 'N/A'})")
    
    def _detect_linux_distro(self) -> LinuxDistro:
        """Detect Linux distribution"""
        
        # Check common files
        if os.path.exists("/etc/arch-release"):
            return LinuxDistro.ARCH
        
        if os.path.exists("/etc/debian_version"):
            return LinuxDistro.DEBIAN
        
        if os.path.exists("/etc/fedora-release"):
            return LinuxDistro.FEDORA
        
        if os.path.exists("/etc/redhat-release"):
            return LinuxDistro.REDHAT
        
        if os.path.exists("/etc/SuSE-release"):
            return LinuxDistro.SUSE
        
        # Check os-release
        if os.path.exists("/etc/os-release"):
            try:
                with open("/etc/os-release") as f:
                    content = f.read().lower()
                    
                    if "arch" in content:
                        return LinuxDistro.ARCH
                    elif "ubuntu" in content:
                        return LinuxDistro.UBUNTU
                    elif "debian" in content:
                        return LinuxDistro.DEBIAN
                    elif "fedora" in content:
                        return LinuxDistro.FEDORA
                    elif "red hat" in content:
                        return LinuxDistro.REDHAT
                    elif "suse" in content or "opensuse" in content:
                        return LinuxDistro.SUSE
            except:
                pass
        
        return LinuxDistro.UNKNOWN
    
    def _create_info(self) -> OSInfo:
        """Create OS info object"""
        
        capabilities = []
        
        # Base capabilities
        capabilities.extend(["chat", "reasoning", "memory", "logging"])
        
        # OS-specific capabilities
        if self._os_type == OSType.LINUX:
            capabilities.extend([
                "command_execution",
                "bash_automation",
                "system_control",
                "pacman_install",
                "apt_install",
                "dnf_install",
                "service_management",
                "process_control",
                "file_operations",
                "network_tools",
                "full_system_access"
            ])
            
        elif self._os_type == OSType.WINDOWS:
            capabilities.extend([
                "command_execution",
                "powershell_automation",
                "cmd_automation",
                "winget_install",
                "pip_install",
                "process_control",
                "file_operations"
            ])
            
        elif self._os_type == OSType.MACOS:
            capabilities.extend([
                "command_execution",
                "bash_automation",
                "brew_install",
                "process_control",
                "file_operations"
            ])
        
        return OSInfo(
            os_type=self._os_type,
            distro=self._distro,
            version=platform.release(),
            arch=platform.machine(),
            hostname=platform.node(),
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            capabilities=capabilities
        )
    
    @property
    def os_type(self) -> OSType:
        """Get OS type"""
        return self._os_type
    
    @property
    def distro(self) -> Optional[LinuxDistro]:
        """Get Linux distro (only on Linux)"""
        return self._distro
    
    @property
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return self._os_type == OSType.LINUX
    
    @property
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return self._os_type == OSType.WINDOWS
    
    @property
    def is_macos(self) -> bool:
        """Check if running on macOS"""
        return self._os_type == OSType.MACOS
    
    @property
    def info(self) -> OSInfo:
        """Get full OS info"""
        return self._info
    
    def has_capability(self, capability: str) -> bool:
        """Check if OS has a capability"""
        return capability in self._info.capabilities
    
    def get_capabilities(self) -> Dict[str, any]:
        """Get all OS capabilities"""
        return {
            "os_type": self._os_type.value,
            "distro": self._distro.value if self._distro else None,
            "version": self._info.version,
            "arch": self._info.arch,
            "capabilities": self._info.capabilities,
            "full_power": self._os_type == OSType.LINUX,
            "safe_mode": self._os_type != OSType.LINUX
        }
    
    def __str__(self) -> str:
        if self._distro:
            return f"{self._os_type.value}/{self._distro.value}"
        return self._os_type.value


# Singleton instance
_os_detector: Optional[OSDetector] = None

def get_os() -> OSDetector:
    """Get OS detector singleton"""
    global _os_detector
    if _os_detector is None:
        _os_detector = OSDetector()
    return _os_detector


def is_linux() -> bool:
    """Quick check if Linux"""
    return get_os().is_linux

def is_windows() -> bool:
    """Quick check if Windows"""
    return get_os().is_windows

def is_macos() -> bool:
    """Quick check if macOS"""
    return get_os().is_macos

def get_platform() -> str:
    """Get platform string"""
    os_detector = get_os()
    if os_detector.distro:
        return f"{os_detector.os_type.value}/{os_detector.distro.value}"
    return os_detector.os_type.value
