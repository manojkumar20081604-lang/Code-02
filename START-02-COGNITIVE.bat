@echo off
title 02 - COGNITIVE AI
color 0A
mode con: cols=90 lines=35
cls
echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════╗
echo  ║                                                                           ║
echo  ║                    02 - COGNITIVE AUTONOMOUS AI OS                        ║
echo  ║                                                                           ║
echo  ║                       "At your service, sir."                              ║
echo  ║                                                                           ║
echo  ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo  INITIALIZING...
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found! Install Python 3.8+ first.
    pause
    exit /b 1
)

:: Set directories
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Install dependencies silently
echo [1/3] Installing dependencies...
pip install -q flask flask-cors requests numpy pandas scikit-learn 2>nul

:: Check Node
node --version >nul 2>&1
set NODE_FOUND=%errorlevel%

:: Start Cognitive Server
echo [2/3] Starting Cognitive AI Server...
start "02 COGNITIVE SERVER" cmd /k "cd /d %SCRIPT_DIR%cyber-assistant && python cognitive_server.py"

:: Wait for server
timeout /t 3 /nobreak >nul

:: Check server status
curl -s http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo          [OK] Cognitive Server ONLINE
) else (
    echo          [!] Server starting...
)

:: Start Frontend if Node exists
if %NODE_FOUND% equ 0 (
    echo [3/3] Starting Desktop App...
    start "02 DESKTOP" cmd /k "cd /d %SCRIPT_DIR%voiceai && npm run dev 2>nul"
)

:: Done
echo.
echo  ╔═══════════════════════════════════════════════════════════════════════════╗
echo  ║                                                                           ║
echo  ║                    02 COGNITIVE AI SYSTEM ONLINE                        ║
echo  ║                                                                           ║
echo  ║   Cognitive Brain:     THINKING                                         ║
echo  ║   Memory System:       LEARNING                                          ║
echo  ║   Autonomous Agent:     READY                                            ║
echo  ║                                                                           ║
echo  ╠═══════════════════════════════════════════════════════════════════════════╣
echo  ║                                                                           ║
echo  ║   Endpoints:                                                            ║
echo  ║     http://localhost:5000/chat    - Chat with 02                         ║
echo  ║     http://localhost:5173        - Desktop App                           ║
echo  ║                                                                           ║
echo  ╚═══════════════════════════════════════════════════════════════════════════╝
echo.
echo  Say: "02 improve my project" or "02 analyze this"
echo.
pause
