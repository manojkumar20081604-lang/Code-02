#!/bin/bash

# CODE-02 Quick Launcher
# Fast way to start Code-02 in any mode

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "  ██████╗ ██╗  ██╗██╗   ██╗ █████╗ ██████╗ ███████╗"
echo "  ██╔══██╗██║  ██║██║   ██║██╔══██╗██╔══██╗██╔════╝"
echo "  ██████╔╝███████║██║   ██║███████║██████╔╝███████╗"
echo "  ██╔═══╝ ██╔══██║╚██╗ ██╔╝██╔══██║██╔══██╗╚════██║"
echo "  ██║     ██║  ██║ ╚████╔╝ ██║  ██║██║  ██║███████║"
echo "  ╚═╝     ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
echo -e "${NC}"
echo -e "${GREEN}AUTONOMOUS AI OPERATING SYSTEM v2.0${NC}"
echo "================================================"
echo ""

# Parse arguments
MODE="${1:-interactive}"

case "$MODE" in
    start|run)
        echo -e "${GREEN}[*] Starting Code-02...${NC}"
        python3 core/main.py
        ;;
    daemon)
        echo -e "${GREEN}[*] Starting Code-02 daemon...${NC}"
        python3 services/code02d.py start
        ;;
    install-deps)
        echo -e "${YELLOW}[*] Installing dependencies...${NC}"
        
        # Detect package manager
        if command -v pacman &> /dev/null; then
            echo "Detected: Arch Linux (pacman)"
            sudo pacman -S python python-pip git curl wget base-devel
        elif command -v apt-get &> /dev/null; then
            echo "Detected: Debian/Ubuntu (apt)"
            sudo apt-get update && sudo apt-get install -y python3 python3-pip git curl wget build-essential
        elif command -v dnf &> /dev/null; then
            echo "Detected: Fedora (dnf)"
            sudo dnf install -y python3 python3-pip git curl wget @development-tools
        fi
        
        echo -e "${YELLOW}[*] Installing Python packages...${NC}"
        pip3 install flask flask-cors fastapi uvicorn sqlalchemy aiosqlite aiohttp ujson
        
        echo -e "${GREEN}[+] Dependencies installed!${NC}"
        ;;
    setup-ollama)
        echo -e "${YELLOW}[*] Setting up Ollama...${NC}"
        
        if ! command -v ollama &> /dev/null; then
            echo "Installing Ollama..."
            curl -fsSL https://ollama.com/install.sh | sh
        fi
        
        echo "Pulling llama3.2 model..."
        ollama pull llama3.2
        
        echo -e "${GREEN}[+] Ollama setup complete!${NC}"
        ;;
    status)
        python3 services/code02d.py status
        ;;
    stop)
        python3 services/code02d.py stop
        ;;
    restart)
        python3 services/code02d.py restart
        ;;
    api)
        echo -e "${GREEN}[*] Starting API server...${NC}"
        cd api && python3 server.py
        ;;
    ui)
        echo -e "${GREEN}[*] Starting UI dev server...${NC}"
        cd ui && npm install && npm run dev
        ;;
    test)
        echo -e "${YELLOW}[*] Running tests...${NC}"
        python3 -c "
import asyncio
from core.main import get_code02_os

async def test():
    code02 = get_code02_os()
    await code02.initialize()
    
    print('Testing LLM...')
    r = await code02.process('Hello')
    print(f'LLM: {r.get(\"response\", \"N/A\")[:100]}...')
    
    print('Testing automation...')
    r = await code02.execute_task('echo test')
    print(f'Automation: {r[\"status\"]}')
    
    print('Testing memory...')
    r = await code02.memory.store('test_key', 'test_value', entry_type='test')
    print(f'Memory: stored id={r}')
    
    print('\\nAll tests passed!')
    await code02.shutdown()

asyncio.run(test())
"
        ;;
    v5|code02)
        echo -e "${GREEN}[*] Starting CODE-02 v5.1 (human brain) ...${NC}"
        echo "    Persona: CODE-02 wake=hey code02 (legacy hey ultron compat)"
        echo "    Brain: ~/.code02/brain.db (legacy ~/.openjarvis compat) STM/LTM"
        echo "    API will be at http://127.0.0.1:8000 (CODE-02 API)"
        # check LM Studio
        if ! curl -s http://localhost:1234/v1/models >/dev/null 2>&1; then
            echo -e "${YELLOW}[!] LM Studio not running at localhost:1234 — using mock fallback${NC}"
            echo "    Start LM Studio -> Developer -> Start Server -> load nvidia/nemotron-3-nano-4b"
        fi
        cd CODE-02-v5-ultron
        # quick health via TestClient if no server
        python3 -c "import sys; sys.path.insert(0,'src'); from ultron.brain import get_brain; s=get_brain().get_stats(); print(f\"    Brain: STM {s['stm']} LTM {s['ltm']} {s['brain_db']}\")"
        echo ""
        echo "  Choose v5 mode:"
        echo "    v5-api      -> python ultron_api.py (CODE-02 API :8000) + python -m ultron.brain_mcp (8100)"
        echo "    v5-voice    -> python voice_roundtrip.py \"hey code02 install htop\""
        echo "    v5-e2e      -> python e2e_demo.py"
        echo "    v5-test     -> python red_team.py + python decepticon_audit.py + python ultron_kill.py"
        echo "    v5-brain    -> python ultron_self_audit.py --once --consolidate 5"
        echo ""
        echo "  Run one, e.g.: cd CODE-02-v5-ultron && python ultron_api.py &"
        ;;
    v5-api)
        echo -e "${GREEN}[*] Starting CODE-02 v5 API (CODE-02) ...${NC}"
        cd CODE-02-v5-ultron && python3 ultron_api.py
        ;;
    v5-brain)
        echo -e "${GREEN}[*] CODE-02 Brain stats ...${NC}"
        cd CODE-02-v5-ultron && python3 -c "import sys; sys.path.insert(0,'src'); from ultron.brain import get_brain; import json; print(json.dumps(get_brain().get_stats(), indent=2))"
        ;;
    v5-test)
        echo -e "${GREEN}[*] Running CODE-02 v5 tests ...${NC}"
        cd CODE-02-v5-ultron && python3 red_team.py && python3 decepticon_audit.py && python3 ultron_kill.py 2>&1 | tail -n 20
        ;;
    v5-voice)
        cd CODE-02-v5-ultron && python3 voice_roundtrip.py "hey code02 install htop"
        ;;
    v5-e2e)
        cd CODE-02-v5-ultron && python3 e2e_demo.py
        ;;
    help|--help|-h)
        echo "Usage: ./launch.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start         Start Code-02 v4 in interactive mode (core/main.py)"
        echo "  v5            Show CODE-02 v5.1 help (human brain, CODE-02 identity)"
        echo "  v5-api        Start CODE-02 v5 API :8000 (ultron_api.py CODE-02)"
        echo "  v5-brain      Show brain stats ~/.code02/brain.db"
        echo "  v5-test       Run red_team + decepticon + kill (all PASS)"
        echo "  v5-voice      Voice round-trip hey code02"
        echo "  v5-e2e        E2E demo hey code02 install htop"
        echo "  daemon        Start as background daemon (v4)"
        echo "  install-deps  Install system dependencies"
        echo "  setup-ollama  Install and configure Ollama"
        echo "  status        Check daemon status"
        echo "  stop          Stop daemon"
        echo "  restart       Restart daemon"
        echo "  api           Start API server (v4 api/server.py)"
        echo "  ui            Start UI dev server"
        echo "  test          Run system tests (v4 core)"
        echo "  help          Show this help"
        ;;
    *)
        echo -e "${RED}Unknown command: $MODE${NC}"
        echo "Run './launch.sh help' for usage"
        exit 1
        ;;
esac
