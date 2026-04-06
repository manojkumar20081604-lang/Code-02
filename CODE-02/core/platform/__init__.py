"""
============================================================
PLATFORM MODULE - OS Detection and Abstraction
============================================================
"""

from .detect import (
    OSType,
    LinuxDistro,
    OSInfo,
    OSDetector,
    get_os,
    is_linux,
    is_windows,
    is_macos,
    get_platform
)

__all__ = [
    "OSType",
    "LinuxDistro",
    "OSInfo",
    "OSDetector",
    "get_os",
    "is_linux",
    "is_windows",
    "is_macos",
    "get_platform"
]
