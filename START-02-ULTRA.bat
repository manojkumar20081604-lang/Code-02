@echo off
title 02 Ultra - Level 5 AI System
color 0C
echo.
echo  ╔══════════════════════════════════════════════════════════════════════════╗
echo  ║                                                                      ║
echo  ║                    02 ULTRA - LEVEL 5 AI SYSTEM                       ║
echo  ║                                                                      ║
echo  ║              "Think. Plan. Learn. Evolve. Execute. Improve."         ║
echo  ║                                                                      ║
echo  ╚══════════════════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [*] Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo [*] Installing Flask...
    pip install flask flask-cors
)

echo [*] Starting 02 Ultra Server...
echo [*] Dashboard: http://localhost:5000/
echo.

python ultra_server.py

pause
