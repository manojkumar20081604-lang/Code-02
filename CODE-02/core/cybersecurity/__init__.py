"""
============================================================
CYBERSECURITY MODULE - Security Operations
============================================================
Real security capabilities: scanning, threat detection, monitoring
"""

import socket
import struct
import subprocess
import re
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import urllib.parse
import ssl

logger = logging.getLogger("Security")


class ThreatLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ScanResult:
    target: str
    port: int
    status: str  # open, closed, filtered
    service: str
    threat_level: ThreatLevel


@dataclass
class ThreatDetection:
    threat_type: str
    threat_level: ThreatLevel
    description: str
    indicators: List[str]
    recommendation: str


class CybersecurityModule:
    """
    Cybersecurity module with real security capabilities
    """
    
    def __init__(self):
        self.scan_history: List[Dict] = []
        self.threat_log: List[ThreatDetection] = []
        self.blocked_urls: List[str] = []
        
        # Known malicious patterns
        self.phishing_patterns = [
            r"login.*verify", r"account.*suspend",
            r"urgent.*action", r"confirm.*identity",
            r"free.*gift", r"winner.*claim"
        ]
        
        self.suspicious_tlds = [
            ".tk", ".ml", ".ga", ".cf", ".gq",
            ".xyz", ".top", ".club", ".online"
        ]
        
        logger.info("Cybersecurity module initialized")
    
    # ================================================================
    # PORT SCANNING
    # ================================================================
    
    def scan_port(self, target: str, port: int, timeout: float = 1.0) -> ScanResult:
        """Scan a single port"""
        
        service = self._get_service_name(port)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((target, port))
            sock.close()
            
            if result == 0:
                return ScanResult(
                    target=target,
                    port=port,
                    status="open",
                    service=service,
                    threat_level=self._assess_port_threat(port)
                )
            else:
                return ScanResult(
                    target=target,
                    port=port,
                    status="closed",
                    service=service,
                    threat_level=ThreatLevel.SAFE
                )
                
        except socket.timeout:
            return ScanResult(
                target=target,
                port=port,
                status="filtered",
                service=service,
                threat_level=ThreatLevel.LOW
            )
        except Exception as e:
            return ScanResult(
                target=target,
                port=port,
                status="error",
                service=service,
                threat_level=ThreatLevel.SAFE
            )
    
    def scan_ports(self, target: str, ports: List[int] = None, 
                   timeout: float = 0.5) -> List[ScanResult]:
        """Scan multiple ports"""
        
        if ports is None:
            ports = self._common_ports()
        
        results = []
        
        for port in ports:
            result = self.scan_port(target, port, timeout)
            results.append(result)
            
            # Log open ports
            if result.status == "open":
                self.scan_history.append({
                    "target": target,
                    "port": port,
                    "service": result.service,
                    "timestamp": datetime.now().isoformat()
                })
        
        return results
    
    def scan_common_ports(self, target: str) -> List[ScanResult]:
        """Scan common ports quickly"""
        common = [
            21, 22, 23, 25, 53, 80, 110, 143, 443, 445,
            993, 995, 1433, 1521, 3306, 3389, 5432, 5900, 8080, 8443
        ]
        return self.scan_ports(target, common, timeout=1.0)
    
    def _common_ports(self) -> List[int]:
        """Return list of common ports"""
        return [
            20, 21, 22, 23, 25, 53, 80, 110, 143, 443,
            445, 993, 995, 1433, 1521, 3306, 3389, 5432,
            5900, 8080, 8443, 8888, 9000, 9090
        ]
    
    def _get_service_name(self, port: int) -> str:
        """Get service name for port"""
        services = {
            20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "TELNET",
            25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
            143: "IMAP", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
            995: "POP3S", 1433: "MSSQL", 1521: "ORACLE", 3306: "MYSQL",
            3389: "RDP", 5432: "POSTGRESQL", 5900: "VNC", 8080: "HTTP-PROXY",
            8443: "HTTPS-ALT"
        }
        return services.get(port, "UNKNOWN")
    
    def _assess_port_threat(self, port: int) -> ThreatLevel:
        """Assess threat level of open port"""
        dangerous = [23, 21, 445, 1433, 1521, 3306, 3389, 5900]
        if port in dangerous:
            return ThreatLevel.MEDIUM
        return ThreatLevel.SAFE
    
    # ================================================================
    # THREAT DETECTION
    # ================================================================
    
    def detect_phishing(self, url: str) -> ThreatDetection:
        """Detect phishing attempts in URLs"""
        
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        
        indicators = []
        threat_level = ThreatLevel.SAFE
        
        # Check for IP address instead of domain
        ip_pattern = r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'
        if re.match(ip_pattern, domain):
            indicators.append("URL uses IP address instead of domain")
            threat_level = ThreatLevel.MEDIUM
        
        # Check for suspicious TLDs
        for tld in self.suspicious_tlds:
            if domain.endswith(tld):
                indicators.append(f"Suspicious TLD: {tld}")
                threat_level = ThreatLevel.MEDIUM
        
        # Check for phishing patterns
        full_url = (domain + path).lower()
        for pattern in self.phishing_patterns:
            if re.search(pattern, full_url):
                indicators.append(f"Phishing pattern detected: {pattern}")
                threat_level = ThreatLevel.HIGH
        
        # Check for suspicious subdomains
        if "login" in domain or "signin" in domain or "verify" in domain:
            if not any(safe in domain for safe in ["google", "microsoft", "apple", "amazon"]):
                indicators.append("Suspicious login subdomain")
                threat_level = ThreatLevel.HIGH
        
        # Check for URL shorteners
        shorteners = ["bit.ly", "tinyurl", "goo.gl", "t.co", "ow.ly"]
        if any(s in domain for s in shorteners):
            indicators.append("URL shortener detected")
            threat_level = ThreatLevel.MEDIUM
        
        # Check for data exfiltration patterns
        if "@" in url or "?" in path and "=" in path:
            if not any(safe in domain for safe in ["google.com", "amazon.com"]):
                indicators.append("Possible data exfiltration")
                threat_level = ThreatLevel.HIGH
        
        return ThreatDetection(
            threat_type="phishing",
            threat_level=threat_level,
            description="Phishing URL analysis",
            indicators=indicators,
            recommendation=self._get_recommendation(threat_level)
        )
    
    def check_url_safety(self, url: str) -> Dict[str, Any]:
        """Check if URL is safe"""
        
        detection = self.detect_phishing(url)
        
        return {
            "url": url,
            "safe": detection.threat_level == ThreatLevel.SAFE,
            "threat_level": detection.threat_level.value,
            "indicators": detection.indicators,
            "recommendation": detection.recommendation
        }
    
    def analyze_file_hash(self, filepath: str) -> Dict[str, str]:
        """Calculate file hashes"""
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
                
            return {
                "filepath": filepath,
                "md5": hashlib.md5(data).hexdigest(),
                "sha1": hashlib.sha1(data).hexdigest(),
                "sha256": hashlib.sha256(data).hexdigest(),
                "size_bytes": len(data),
                "size_human": self._format_size(len(data))
            }
        except FileNotFoundError:
            return {"error": "File not found"}
        except Exception as e:
            return {"error": str(e)}
    
    def check_command_safety(self, command: str) -> ThreatDetection:
        """Check if a command is potentially dangerous"""
        
        dangerous_patterns = [
            (r"rm\s+-rf\s+/\s*", "Attempting to delete root directory", ThreatLevel.CRITICAL),
            (r"curl.*\|\s*bash", "Piping downloaded script to bash", ThreatLevel.HIGH),
            (r"wget.*\|\s*bash", "Piping downloaded script to bash", ThreatLevel.HIGH),
            (r":\(\)\s*:\s*\|", "Fork bomb detected", ThreatLevel.CRITICAL),
            (r"chmod\s+777", "Setting dangerous permissions (777)", ThreatLevel.MEDIUM),
            (r"chmod\s+-R\s+777", "Recursive dangerous permissions", ThreatLevel.HIGH),
            (r"wget.*-O\s+/etc", "Writing to system directory", ThreatLevel.HIGH),
            (r"curl.*-o\s+/etc", "Writing to system directory", ThreatLevel.HIGH),
            (r"nc\s+-e", "Netcat reverse shell pattern", ThreatLevel.HIGH),
            (r"/dev/tcp/", "Raw TCP manipulation", ThreatLevel.MEDIUM),
        ]
        
        indicators = []
        max_threat = ThreatLevel.SAFE
        
        for pattern, description, threat in dangerous_patterns:
            if re.search(pattern, command.lower()):
                indicators.append(description)
                if threat.value > max_threat.value:
                    max_threat = threat
        
        return ThreatDetection(
            threat_type="command",
            threat_level=max_threat,
            description="Command safety analysis",
            indicators=indicators,
            recommendation=self._get_recommendation(max_threat)
        )
    
    # ================================================================
    # NETWORK ANALYSIS
    # ================================================================
    
    def get_local_ips(self) -> List[str]:
        """Get local IP addresses"""
        
        ips = []
        
        try:
            # Get hostname
            hostname = socket.gethostname()
            
            # Get all IPs
            addr_info = socket.getaddrinfo(hostname, None)
            
            for info in addr_info:
                ip = info[4][0]
                if '.' in ip and not ip.startswith('127.'):
                    ips.append(ip)
                    
        except:
            pass
        
        return list(set(ips))
    
    def resolve_domain(self, domain: str) -> Optional[str]:
        """Resolve domain to IP"""
        
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return None
    
    def check_port_security(self, target: str, port: int) -> Dict[str, Any]:
        """Check if a port is securely configured"""
        
        result = self.scan_port(target, port)
        
        issues = []
        
        if result.status == "open":
            if port == 23:
                issues.append("Telnet is insecure - use SSH")
            elif port == 21:
                issues.append("FTP is insecure - use SFTP")
            elif port == 445:
                issues.append("SMB may be vulnerable - restrict access")
            elif port == 3389:
                issues.append("RDP exposed - ensure VPN or firewall")
            elif port not in [22, 443, 80]:
                issues.append("Non-standard port open - verify necessity")
        
        return {
            "port": port,
            "status": result.status,
            "service": result.service,
            "issues": issues,
            "recommendation": "Close unused ports" if issues else "Port appears secure"
        }
    
    # ================================================================
    # HELPER METHODS
    # ================================================================
    
    def _get_recommendation(self, threat_level: ThreatLevel) -> str:
        """Get recommendation based on threat level"""
        
        recommendations = {
            ThreatLevel.SAFE: "No action required",
            ThreatLevel.LOW: "Monitor for unusual activity",
            ThreatLevel.MEDIUM: "Review and verify before proceeding",
            ThreatLevel.HIGH: "Do not proceed - potential threat detected",
            ThreatLevel.CRITICAL: "BLOCK - Dangerous operation detected"
        }
        
        return recommendations.get(threat_level, "Unknown threat level")
    
    def _format_size(self, size: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def get_threat_summary(self) -> Dict[str, Any]:
        """Get summary of detected threats"""
        
        threat_counts = {}
        for threat in self.threat_log:
            threat_type = threat.threat_type
            threat_counts[threat_type] = threat_counts.get(threat_type, 0) + 1
        
        return {
            "total_scans": len(self.scan_history),
            "total_threats": len(self.threat_log),
            "threats_by_type": threat_counts,
            "blocked_urls": len(self.blocked_urls)
        }
    
    def get_capabilities(self) -> List[str]:
        """Get security capabilities"""
        return [
            "port_scanning",
            "phishing_detection",
            "command_safety_check",
            "file_hash_analysis",
            "threat_logging",
            "network_analysis"
        ]


# Singleton
_security_module: Optional[CybersecurityModule] = None

def get_security() -> CybersecurityModule:
    """Get cybersecurity module singleton"""
    global _security_module
    if _security_module is None:
        _security_module = CybersecurityModule()
    return _security_module
