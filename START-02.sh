#!/bin/bash
echo "============================================================"
echo "   02 - ZERO TWO - AI CYBER DEFENSE ASSISTANT"
echo "============================================================"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js not found. Please install Node.js"
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Python dependencies
echo "[1/4] Installing Python dependencies..."
cd "$SCRIPT_DIR/cyber-assistant"
pip3 install -q flask flask-cors requests 2>/dev/null

# Install Node dependencies
echo "[2/4] Checking Node dependencies..."
cd "$SCRIPT_DIR/voiceai"
if [ ! -d "node_modules" ]; then
    echo "         Installing Node modules..."
    npm install
fi

# Start Python backend in background
echo "[3/4] Starting Python Backend Server..."
cd "$SCRIPT_DIR/cyber-assistant"
python3 api_server.py &
BACKEND_PID=$!
sleep 3

# Start Electron app
echo "[4/4] Starting Electron App..."
cd "$SCRIPT_DIR/voiceai"
npm run dev

# Cleanup on exit
trap "kill $BACKEND_PID 2>/dev/null" EXIT
