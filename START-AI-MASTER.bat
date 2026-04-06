@echo off
title AI Master System - Desktop App
color 0A
mode con cols=80 lines=30

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
echo     Desktop Application - No Server Required!
echo.
echo  ==================================================================
echo.

echo Starting AI Master System...
echo.

python "C:\Users\aizen\Desktop\OPEN CODE\OPEN CLAUD\AI-MASTER-SYSTEM.py"

if errorlevel 1 (
    echo.
    echo ERROR: Failed to start!
    echo.
    pause
)
