#!/bin/bash

# CODE: 02 - Cognitive Autonomous AI System
# Linux Launcher

echo ""
echo "  ██████╗ ██╗  ██╗██╗   ██╗ █████╗ ██████╗ ███████╗"
echo "  ██╔══██╗██║  ██║██║   ██║██╔══██╗██╔══██╗██╔════╝"
echo "  ██████╔╝███████║██║   ██║███████║██████╔╝███████╗"
echo "  ██╔═══╝ ██╔══██║╚██╗ ██╔╝██╔══██║██╔══██╗╚════██║"
echo "  ██║     ██║  ██║ ╚████╔╝ ██║  ██║██║  ██║███████║"
echo "  ╚═╝     ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝"
echo ""
echo "  COGNITIVE AUTONOMOUS AI SYSTEM"
echo "  ============================================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[!] Python 3 not found! Please install Python 3.8+"
    exit 1
fi

echo "[*] Python version: $(python3 --version)"

# Check pip
if ! command -v pip3 &> /dev/null; then
    echo "[!] pip3 not found! Please install pip"
    exit 1
fi

# Install dependencies
echo "[*] Checking dependencies..."
pip3 install -q flask flask-cors 2>/dev/null

echo ""
echo "  ============================================================="
echo "   Select Mode:"
echo "  ============================================================="
echo "   [1] Start Full System (API + UI)"
echo "   [2] Start API Server Only"
echo "   [3] Start UI Only"
echo "   [4] Run Python Demo"
echo "   [5] Exit"
echo ""
read -p "  Select option: " choice

case $choice in
    1)
        echo ""
        echo "[*] Starting API Server on port 5000..."
        cd "$SCRIPT_DIR/api"
        python3 server.py &
        API_PID=$!
        sleep 2
        
        echo "[*] Starting UI Server on port 3000..."
        cd "$SCRIPT_DIR/ui"
        npm install
        npm run dev &
        UI_PID=$!
        
        echo ""
        echo "[*] System started!"
        echo "    API: http://localhost:5000"
        echo "    UI:  http://localhost:3000"
        echo ""
        echo "    Press Ctrl+C to stop"
        
        # Wait for any process to exit
        wait
        ;;
    2)
        echo ""
        echo "[*] Starting API Server on port 5000..."
        cd "$SCRIPT_DIR/api"
        python3 server.py
        ;;
    3)
        echo ""
        echo "[*] Starting UI Server on port 3000..."
        cd "$SCRIPT_DIR/ui"
        npm install
        npm run dev
        ;;
    4)
        echo ""
        echo "[*] Running Python Demo..."
        cd "$SCRIPT_DIR"
        python3 -c "
import asyncio
from core import get_code02

async def demo():
    code02 = get_code02()
    print('=' * 60)
    print('CODE: 02 - Cognitive Autonomous AI System')
    print('=' * 60)
    print()
    
    result = await code02.process('Analyze this data: 10, 20, 30, 40, 50')
    
    print(f'Status: {result[\"success\"]}')
    print(f'Intent: {result.get(\"intent\", {}).get(\"type\", \"unknown\")}')
    print(f'Plan Steps: {len(result.get(\"plan\", {}).get(\"steps\", []))}')
    print(f'Response: {result.get(\"response\", \"No response\")}')
    print()
    print('=' * 60)

asyncio.run(demo())
"
        ;;
    5)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid option!"
        exit 1
        ;;
esac
