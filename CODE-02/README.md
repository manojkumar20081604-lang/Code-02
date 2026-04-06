# CODE: 02 - Cognitive Autonomous AI System

## Overview

CODE: 02 is a next-generation personal AI assistant that functions as a **Cognitive Autonomous AI System** rather than a simple chatbot. It operates on goals instead of direct commands, understanding user intent, creating step-by-step plans, executing tasks using available tools, evaluating outcomes, and continuously improving through a feedback loop.

## Architecture

```
CODE: 02
├── core/                      # AI Core Components
│   ├── brain/                 # Brain Module
│   │   ├── intent_detector.py # Intent detection & classification
│   │   ├── planner.py         # Goal decomposition & planning
│   │   └── orchestrator.py    # Task coordination & execution
│   ├── memory/                # Memory Systems
│   │   ├── short_term.py      # Active context memory
│   │   └── long_term.py       # Persistent knowledge storage
│   ├── planning/              # Planning Engine
│   │   └── reasoning.py       # Chain-of-thought reasoning
│   ├── tools/                 # Modular Tool System
│   │   └── tool_registry.py   # Dynamic tool invocation
│   ├── action/                # Action Engine
│   │   └── executor.py        # OS interaction & command execution
│   ├── agents/               # Multi-Agent Architecture
│   ├── learning/              # Learning Loop
│   └── voice/                # Voice Interaction
├── api/                      # REST API Server
├── ui/                       # React Frontend
└── data/                     # Data Storage
```

## Features

### 1. Central AI Core (Brain)
- **Intent Detection**: Understands user goals and classifies intents
- **Planning**: Decomposes complex goals into actionable steps
- **Orchestration**: Coordinates tools and agents for execution
- **Decision Making**: Evaluates options and selects optimal actions

### 2. Dual-Layer Memory System
- **Short-Term Memory**: Active context storage (50 items max)
- **Long-Term Memory**: User behavior, past interactions, learned patterns
- Enables adaptation to user over time
- Provides contextual responses and proactive suggestions

### 3. Planning & Reasoning Engine
- Chain-of-thought reasoning
- Multiple reasoning methods (deductive, inductive, abductive, analogical, causal)
- Dynamic plan adjustment based on results
- Multi-step autonomous workflow support

### 4. Multi-Agent Architecture
- **Planner Agent**: Creates execution plans
- **Developer Agent**: Handles code development tasks
- **Data Processor Agent**: Manages data operations
- **Security Agent**: Performs security operations
- **System Control Agent**: OS-level control
- **Assistant Agent**: General purpose responses

### 5. Modular Tool System
- Dynamic tool invocation based on context
- Categories: Development, Data, Security, System, Information
- Easy to extend with new tools

### 6. Action Engine
- Terminal command execution
- File operations (read, write, delete, list)
- Script execution
- Application launching
- Cross-platform support (Windows, Linux)

### 7. Learning Loop
- Performance evaluation
- Feedback collection
- Strategy storage and retrieval
- Continuous improvement

### 8. Voice Interaction
- Speech recognition
- Text-to-speech with natural voices
- Continuous listening mode

## Installation

```bash
# Clone the repository
git clone https://github.com/manojkumar20081604-lang/Code-02.git
cd Code-02/CODE-02

# Install Python dependencies
pip install flask flask-cors

# Install UI dependencies
cd ui
npm install
```

## Usage

### Windows
```bash
START-CODE-02.bat
```

### Manual Start

**API Server:**
```bash
cd api
python server.py
```

**UI Server:**
```bash
cd ui
npm run dev
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Process user input |
| `/api/think` | POST | Deep reasoning mode |
| `/api/status` | GET | System status |
| `/api/memory` | GET | Memory state |
| `/api/execute` | POST | Execute command |
| `/api/files` | GET/POST/DELETE | File operations |
| `/api/tools` | GET | Available tools |
| `/api/agents` | GET | Agent status |
| `/api/voice/speak` | POST | Text-to-speech |
| `/api/voice/listen` | POST | Speech recognition |
| `/api/performance` | GET | Learning report |

## Example Usage

```python
import asyncio
from core import get_code02

async def main():
    code02 = get_code02()
    
    # Process a goal
    result = await code02.process("Analyze the data: 10, 20, 30, 40, 50")
    
    print(f"Success: {result['success']}")
    print(f"Intent: {result['intent']['type']}")
    print(f"Response: {result['response']}")

asyncio.run(main())
```

## UI Features

### Cyberpunk Design
- Dark theme with neon accents
- Glassmorphism effects
- Smooth animations
- Real-time activity visualization

### Panels
- **Left Sidebar**: Navigation and quick actions
- **Main Panel**: AI interaction and visualization
- **Right Panel**: System status and logs

### Modules
1. **AI Chat**: Natural conversation with AI
2. **Deep Think**: Chain-of-thought reasoning
3. **Workflow**: Visual workflow builder
4. **Memory**: Memory visualization and management
5. **Data**: Data analysis tools
6. **Security**: Security operations
7. **Terminal**: Command execution
8. **Settings**: Configuration

## System Requirements

- Python 3.8+
- Node.js 16+ (for UI)
- 4GB RAM minimum
- Internet connection (for voice features)

## Author

**Manojkumar M**
B.Tech AI & Data Science

## License

MIT License

---

*"CODE: 02 - Not just a chatbot, but a thinking partner."*
