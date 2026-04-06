@echo off
title 02 - JARVIS AI SYSTEM
color 0A
echo.
echo  ============================================================
echo       02 - UNIVERSAL AI ASSISTANT
echo       "At your service."
echo  ============================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

:: Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found. Please install Node.js
    pause
    exit /b 1
)

:: Get script directory
set SCRIPT_DIR=%~dp0

:: Install Python dependencies
echo [1/5] Installing Python dependencies...
cd /d "%SCRIPT_DIR%cyber-assistant"
pip install -q flask flask-cors requests openai anthropic numpy pandas scikit-learn matplotlib beautifulsoup4 pyttsx3 2>nul

:: Install Node dependencies
echo [2/5] Installing Node dependencies...
cd /d "%SCRIPT_DIR%voiceai"
if not exist "node_modules" (
    call npm install
)

:: Start Python backend server
echo [3/5] Starting Python Backend (JARVIS Brain)...
cd /d "%SCRIPT_DIR%cyber-assistant"
start "02 Backend - JARVIS" cmd /k "python server.py"

:: Wait for backend to start
echo          Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

:: Check if backend is running
curl -s http://localhost:5000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo          [OK] Backend connected
) else (
    echo          [WARNING] Backend may not be running
)

:: Start Electron app
echo [4/5] Starting Electron App...
cd /d "%SCRIPT_DIR%voiceai"
start "02 Desktop" cmd /k "npm run dev"

echo.
echo [5/5] Starting Voice Assistant...
start "" "%SCRIPT_DIR%cyber-assistant\voice\voice_assistant.py"

echo.
echo ============================================================
echo    02 JARVIS SYSTEM STARTED
echo ============================================================
echo.
echo    Backend:  http://localhost:5000
echo    Frontend: http://localhost:5173
echo    Dashboard: http://localhost:5001
echo.
echo    Commands:
echo    - 'mode passive' - Standard mode
echo    - 'mode active' - Suggest actions
echo    - 'mode autonomous' - Full automation
echo.
echo    Press Ctrl+C in backend window to stop
echo ============================================================
echo.

pause
