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
    help|--help|-h)
        echo "Usage: ./launch.sh [command]"
        echo ""
        echo "Commands:"
        echo "  start         Start Code-02 in interactive mode"
        echo "  daemon        Start as background daemon"
        echo "  install-deps  Install system dependencies"
        echo "  setup-ollama  Install and configure Ollama"
        echo "  status        Check daemon status"
        echo "  stop          Stop daemon"
        echo "  restart       Restart daemon"
        echo "  api           Start API server"
        echo "  ui            Start UI dev server"
        echo "  test          Run system tests"
        echo "  help          Show this help"
        ;;
    *)
        echo -e "${RED}Unknown command: $MODE${NC}"
        echo "Run './launch.sh help' for usage"
        exit 1
        ;;
esac
