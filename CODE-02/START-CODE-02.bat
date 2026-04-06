@echo off
title CODE: 02 - Cognitive Autonomous AI System
color 0A
mode con:cols=100 lines=35

echo.
echo  ██████╗ ██╗  ██╗██╗   ██╗ █████╗ ██████╗ ███████╗
echo  ██╔══██╗██║  ██║██║   ██║██╔══██╗██╔══██╗██╔════╝
echo  ██████╔╝███████║██║   ██║███████║██████╔╝███████╗
echo  ██╔═══╝ ██╔══██║╚██╗ ██╔╝██╔══██║██╔══██╗╚════██║
echo  ██║     ██║  ██║ ╚████╔╝ ██║  ██║██║  ██║███████║
echo  ╚═╝     ╚═╝  ╚═╝  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
echo.
echo  COGNITIVE AUTONOMOUS AI SYSTEM
echo  ================================================================
echo.

cd /d "%~dp0"

echo [*] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [!] Python not found! Please install Python 3.8+
    pause
    exit /b 1
)

echo [*] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [!] Installing dependencies...
    pip install flask flask-cors
)

echo.
echo  ================================================================
echo   Starting CODE: 02 System
echo  ================================================================
echo.
echo  [1] Start Full System (API + UI)
echo  [2] Start API Server Only
echo  [3] Start UI Only
echo  [4] Run Python Demo
echo  [5] Exit
echo.
choice /c 12345 /n /m "Select option: "

if errorlevel 5 exit
if errorlevel 4 goto DEMO
if errorlevel 3 goto UI
if errorlevel 2 goto API
if errorlevel 1 goto FULL

:FULL
echo.
echo [*] Starting API Server on port 5000...
start "CODE:02 API" cmd /c "cd /d %~dp0CODE-02\api && python server.py"
timeout /t 3 >nul

echo [*] Starting UI Server on port 3000...
cd %~dp0CODE-02\ui
call npm run dev
goto end

:API
echo.
echo [*] Starting API Server on port 5000...
cd %~dp0CODE-02\api
python server.py
goto end

:UI
echo.
echo [*] Starting UI Server on port 3000...
cd %~dp0CODE-02\ui
call npm install
call npm run dev
goto end

:DEMO
echo.
echo [*] Running Python Demo...
cd %~dp0CODE-02
python -c "
import asyncio
from core import get_code02

async def demo():
    code02 = get_code02()
    print('=' * 60)
    print('CODE: 02 - Cognitive Autonomous AI System')
    print('=' * 60)
    print()
    
    # Process a goal
    result = await code02.process('Analyze this data: 10, 20, 30, 40, 50')
    
    print(f'Status: {result[\"success\"]}')
    print(f'Intent: {result.get(\"intent\", {}).get(\"type\", \"unknown\")}')
    print(f'Plan Steps: {len(result.get(\"plan\", {}).get(\"steps\", []))}')
    print(f'Response: {result.get(\"response\", \"No response\")}')
    print()
    print('=' * 60)

asyncio.run(demo())
"
goto end

:end
pause
