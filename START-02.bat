@echo off
echo ============================================================
echo    02 - ZERO TWO - AI CYBER DEFENSE ASSISTANT
echo ============================================================
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

:: Install Python dependencies if needed
echo [1/4] Checking Python dependencies...
cd /d "%~dp0cyber-assistant"
pip install -q flask flask-cors requests 2>nul
if %errorlevel% neq 0 (
    echo [WARNING] Could not install Python dependencies automatically
    echo          Please run: pip install flask flask-cors requests
)

:: Install Node dependencies if needed
echo [2/4] Checking Node dependencies...
cd /d "%~dp0voiceai"
if not exist "node_modules" (
    echo          Installing Node modules...
    call npm install
)

:: Start Python backend in background
echo [3/4] Starting Python Backend Server...
cd /d "%~dp0cyber-assistant"
start "02 Backend" python api_server.py

:: Wait for backend to start
echo          Waiting for backend server...
timeout /t 3 /nobreak >nul

:: Start Electron app
echo [4/4] Starting Electron App...
cd /d "%~dp0voiceai"
call npm run dev

pause
