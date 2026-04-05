@echo off
title 02 v1 - Cognitive AI Ecosystem
color 0A
echo.
echo  ╔══════════════════════════════════════════════════════════════╗
echo  ║                                                              ║
echo  ║              02 v1 - COGNITIVE AI ECOSYSTEM                 ║
echo  ║                                                              ║
echo  ║               "Think. See. Act. Learn."                     ║
echo  ║                                                              ║
echo  ╚══════════════════════════════════════════════════════════════╝
echo.

cd /d "%~dp0"

echo [*] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

echo [*] Starting 02 v1 Server...
echo [*] Opening dashboard at http://localhost:5000
echo.

python server.py

pause
