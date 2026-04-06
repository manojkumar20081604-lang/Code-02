@echo off
title AI Master System - OpenClaud + 02 + Cyber
color 0A
mode con cols=70 lines=35

:main
cls
echo.
echo  ==================================================================
echo.
echo     ███╗   ███╗██╗██╗  ██╗██╗  ██╗███████╗
echo     ████╗ ████║██║╚██╗██╔╝██║ ██╔╝██╔════╝
echo     ██╔████╔██║██║ ╚███╔╝ █████╔╝ █████╗
echo     ██║╚██╔╝██║██║ ██╔██╗ ██╔═██╗ ██╔══╝
echo     ██║ ╚═╝ ██║██║██╔╝ ██╗██║  ██╗███████╗
echo     ╚═╝     ╚═╝╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝
echo.
echo  ==================================================================
echo.
echo     OPENCLAUD + 02 + CYBER ASSISTANT
echo     Level 5 Cognitive AI System
echo.
echo  ==================================================================
echo.
echo   1.  OpenClaud     - Voice ^& Desktop AI
echo   2.  02 AI         - Level 5 Cognitive Assistant
echo   3.  Cyber         - Security + Data Science
echo   4.  ALL IN ONE    - Start All Systems
echo   5.  Dashboard     - Web Interface
echo  ------------------------------------------------------------------
echo   0.  Exit
echo.
echo  ==================================================================
echo.

set /p choice="Select: "

if "%choice%"=="1" goto openclaud
if "%choice%"=="2" goto ai02
if "%choice%"=="3" goto cyber
if "%choice%"=="4" goto allinone
if "%choice%"=="5" goto dashboard
if "%choice%"=="0" goto end

:openclaud
echo.
echo [*] Starting OpenClaud...
cd openclaude
if exist package.json (
    echo [*] Run: npm run dev
    start cmd /k "npm run dev"
) else (
    echo [!] OpenClaud not found
)
cd ..
pause
goto main

:ai02
echo.
echo [*] Starting 02 AI...
cd 02-v1
echo [*] Starting Flask server...
start "02-AI" cmd /k "python ultra_server.py"
timeout /t 2 /nobreak >nul
start http://localhost:5000
cd ..
echo.
echo [+] 02 AI running at http://localhost:5000
pause
goto main

:cyber
echo.
echo [*] Starting Cyber Assistant...
cd cyber-assistant
echo [*] Starting dashboard...
start "Cyber-Dashboard" cmd /k "python dashboard.py"
timeout /t 2 /nobreak >nul
start http://localhost:5001
cd ..
echo.
echo [+] Cyber Dashboard running at http://localhost:5001
pause
goto main

:allinone
echo.
echo [*] Starting ALL systems...
echo.
echo [*] Starting 02 AI...
cd 02-v1
start "02-AI" cmd /k "python ultra_server.py"
cd ..

echo [*] Starting Cyber Assistant...
cd cyber-assistant
start "Cyber-Dashboard" cmd /k "python dashboard.py"
cd ..

echo.
echo [*] Opening dashboard...
timeout /t 3 /nobreak >nul
start http://localhost:5000

echo.
echo [+] ALL SYSTEMS STARTED!
echo     - 02 AI:      http://localhost:5000
echo     - Cyber:      http://localhost:5001
echo.
pause
goto main

:dashboard
echo.
echo [*] Opening dashboard...
start http://localhost:5000
pause
goto main

:end
echo.
echo Goodbye!
timeout /t 1 /nobreak >nul
exit
