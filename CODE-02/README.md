# CODE: 02 - Autonomous AI Operating System

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

**Not just a chatbot. An AI that thinks, plans, executes, and evolves.**

---

## Overview

CODE: 02 is a next-generation autonomous AI operating system that functions as a personal AI machine. It goes beyond simple chat interactions to become a self-managing, self-improving intelligent system that controls, automates, and enhances your entire computing experience.

### Core Features

- **Autonomous Environment Management** - Auto-installs dependencies, downloads AI models, fixes broken setups
- **LLM-Based Reasoning** - Local (Ollama) or cloud (OpenAI, Anthropic) AI brain
- **Enhanced Memory System** - SQLite + Vector search + Knowledge graph
- **Automation Engine** - Safe, controlled task execution and workflows
- **Multi-Module Parallel System** - Run multiple AI modules simultaneously
- **Linux Daemon Service** - Background operation with socket-based IPC
- **Cyberpunk UI** - Futuristic interface with real-time visualization

---

## Architecture

```
CODE-02/
├── core/                    # Core AI Modules
│   ├── __init__.py         # Base Code-02 (original)
│   ├── main.py             # NEW: Main orchestrator
│   ├── brain/              # Original brain module
│   ├── memory/             # Original memory module
│   ├── environment/         # NEW: Environment manager
│   │   └── manager.py      # Auto-install, model downloads
│   ├── llm/                # NEW: LLM integration
│   │   └── __init__.py     # Ollama, OpenAI, Anthropic
│   ├── database/           # NEW: Enhanced storage
│   │   └── __init__.py     # SQLite, Vector DB, Knowledge Graph
│   ├── automation/          # NEW: Task execution
│   │   └── __init__.py     # Safe execution, workflows
│   ├── planning/           # Original planning
│   ├── tools/              # Original tools
│   ├── agents/             # Original multi-agent
│   ├── learning/           # Original learning loop
│   └── voice/              # Original voice
├── services/               # Background services
│   └── code02d.py          # Linux daemon
├── api/                   # Flask REST API
├── ui/                    # React web UI
├── ui-electron/           # NEW: Electron desktop app
└── data/                  # Data storage
```

---

## Installation

### Quick Start (Linux/Arch)

```bash
# Clone repository
git clone https://github.com/manojkumar20081604-lang/Code-02.git
cd Code-02/CODE-02

# Install dependencies
pip install -r requirements.txt

# Install Ollama (for local AI)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Run Code-02
python core/main.py
```

### Full Setup

```bash
# Install system dependencies
sudo pacman -S python python-pip git curl wget

# Install Python packages
pip install flask flask-cors fastapi uvicorn sqlalchemy aiosqlite aiohttp

# Install AI packages
pip install langchain langchain-community chromadb transformers

# Install optional packages
pip install ollama redis  # For enhanced features

# Start daemon (optional)
python services/code02d.py start
```

---

## Usage

### Interactive Mode

```bash
python core/main.py
```

```
CODE: 02 - Autonomous AI Operating System
==================================================

System initialized
  [✓] LLM Brain: online (ollama/llama3.2)
  [✓] Memory: online (125 memories, 48 vectors)
  [✓] Automation: online (safe mode)
  [✓] Environment: online (arch linux)

Ready! Type 'help' for commands.

Code-02> hello
Hello! I'm CODE: 02, your autonomous AI system.

Code-02> exec ls -la
Status: completed
(total files...)

Code-02> install numpy
Success: True

Code-02> think about building a web scraper
[Deep thinking output...]
```

### Daemon Mode (Background)

```bash
# Start daemon
python services/code02d.py start

# Send commands
python services/code02d.py status

# Client example
python -c "
from services.code02d import Code02Client
client = Code02Client()
print(client.status())
print(client.process('Hello'))
"

# Stop daemon
python services/code02d.py stop
```

### Python API

```python
import asyncio
from core.main import get_code02_os

async def main():
    code02 = get_code02_os()
    await code02.initialize()
    
    # Chat with AI
    response = await code02.process("Build me a Python web server")
    print(response['response'])
    
    # Execute command
    result = await code02.execute_task("ls -la")
    print(result['stdout'])
    
    # Install dependency
    await code02.install_dependency("flask>=2.3")
    
    # Deep thinking
    thought = await code02.think("How do I build a REST API?")
    print(thought['reasoning'])
    
    # System status
    print(code02.get_system_status())

asyncio.run(main())
```

---

## Module Details

### 1. Environment Manager

Automatically manages your computing environment:
- Detects missing dependencies
- Installs packages (pacman, apt, pip, npm, cargo)
- Downloads AI models (Ollama, HuggingFace)
- Fixes broken setups automatically

```python
env = get_env_manager()

# Check dependencies
missing = await env.check_dependencies(["pip:flask", "npm:electron"])
print(missing)  # {'flask': True, 'electron': False}

# Auto-install
result = await env.install("python-numpy")
print(result.success)

# Download AI model
result = await env.download_ai_model("llama3.2", "ollama")
```

### 2. LLM Brain

Intelligent AI reasoning with multiple backends:

```python
# Create LLM brain
llm = create_llm_brain(provider="ollama", model="llama3.2")
await llm.initialize()

# Generate response
response = await llm.generate("Write a Python function")
print(response.text)

# Deep thinking
thought = await llm.think("How does blockchain work?", method="chain_of_thought")
print(thought['reasoning'])
```

### 3. Enhanced Memory

Multi-layer memory with search capabilities:

```python
memory = get_enhanced_memory()

# Store memories
memory.store("user_preference", "dark mode", tags=["ui", "setting"])
memory.store_knowledge("Python", "is a", "programming language")

# Recall
value = memory.recall("user_preference")

# Search
results = memory.search("programming")
print(results)

# Knowledge graph
related = memory.recall_knowledge("Python")
print(related)
```

### 4. Automation Engine

Safe, controlled task execution:

```python
automation = get_automation_engine(mode=ExecutionMode.SAFE)

# Execute command
task = await automation.execute("ls -la")
print(task.stdout)
print(task.status)

# Execute workflow
workflow = automation.create_workflow("Setup Project", [
    {"name": "Clone repo", "command": "git clone ...", "delay": 1},
    {"name": "Install deps", "command": "pip install -r requirements.txt"},
    {"name": "Run tests", "command": "pytest", "continue_on_error": True}
])
result = await automation.execute_workflow(workflow)
```

---

## Configuration

Config file: `data/config/code02.json`

```json
{
  "llm": {
    "provider": "ollama",
    "model": "llama3.2",
    "temperature": 0.7
  },
  "automation": {
    "mode": "safe",
    "timeout": 60
  },
  "memory": {
    "data_dir": "data/memory",
    "auto_cleanup_days": 30
  },
  "environment": {
    "auto_install": true
  }
}
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Process message |
| `/api/execute` | POST | Execute command |
| `/api/status` | GET | System status |
| `/api/memory` | GET/POST | Memory operations |
| `/api/think` | POST | Deep thinking |
| `/api/install` | POST | Install package |
| `/api/think` | POST | Deep thinking |

---

## System Requirements

- **OS**: Linux (Arch, Debian, Fedora), macOS, Windows
- **Python**: 3.8+
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 2GB for models + dependencies

### Optional
- **Ollama**: For local AI models
- **Node.js**: For UI development
- **Redis**: For caching (optional)

---

## Development Roadmap

- [x] Core AI Brain (Intent, Planning, Memory)
- [x] Multi-Agent System
- [x] Voice Interaction
- [x] LLM Integration (Ollama, OpenAI, Anthropic)
- [x] Enhanced Memory (Vector DB, Knowledge Graph)
- [x] Automation Engine
- [x] Environment Manager
- [x] Linux Daemon Service
- [ ] Electron Desktop UI
- [ ] Plugin System
- [ ] Multi-user Support
- [ ] Mobile Companion App

---

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## License

MIT License - See LICENSE file

---

## Author

**Manojkumar M**
B.Tech AI & Data Science

---

*"CODE: 02 - Not just a chatbot, but a thinking partner and autonomous AI machine."*
