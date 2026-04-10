@echo off
REM GitHub Push Script for CODE-02
REM This script will:
REM 1. Install Git if not present
REM 2. Initialize CODE-02 repository
REM 3. Push to your GitHub

echo.
echo ============================================================
echo   CODE-02 GitHub Push Script
echo ============================================================
echo.

REM Check if git is installed
where git >nul 2>&1
if %errorlevel% neq 0 (
    echo [1/4] Git not found. Installing Git...
    winget install --id Git.Git -e --source winget --accept-package-agreements --accept-source-agreements
    echo.
    echo Git installed. Please run this script again.
    echo.
    set /p dummy="Press Enter to continue or close this window..."
    exit /b
)

echo [1/4] Git found. Continuing...
echo.

REM Navigate to CODE-02 directory
cd /d "%~dp0CODE-02"

REM Check if already a git repo
if exist ".git" (
    echo [2/4] Git repository already initialized
    echo.
) else (
    echo [2/4] Initializing Git repository...
    git init
    git config user.name "Manojkumar"
    git config user.email "manojkumar@github.com"
    echo.
)

REM Add remote
echo [3/4] Setting up GitHub remote...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/manojkumar20081604-lang/Code-02.git
echo.

REM Create .gitignore
echo [4/4] Creating .gitignore...
(
    echo __pycache__/
    echo *.pyc
    echo .env
    echo *.log
    echo node_modules/
    echo .venv/
    echo venv/
    echo data/memory/*.jsonl
    echo *.egg-info/
    echo .DS_Store
    echo Thumbs.db
    echo .idea/
    echo .vscode/
) > .gitignore

REM Stage all files
echo.
echo Staging files...
git add .

REM Check if there are files to commit
git status --porcelain > temp_status.txt
findstr /r "." temp_status.txt >nul
if %errorlevel% neq 0 (
    echo No files to commit.
    del temp_status.txt
    exit /b
)
del temp_status.txt

REM Commit
echo.
set /p commit_msg="Enter commit message (or press Enter for default): "
if "%commit_msg%"=="" set commit_msg=CODE-02 v4.0-LIVING - Complete Intelligent Autonomous AI System

git commit -m "%commit_msg%"

REM Push to GitHub
echo.
echo ============================================================
echo   Pushing to GitHub...
echo ============================================================
echo.
git branch -M main
git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo.
    echo ============================================================
    echo   SUCCESS! CODE-02 pushed to GitHub!
    echo   https://github.com/manojkumar20081604-lang/Code-02
    echo ============================================================
) else (
    echo.
    echo ============================================================
    echo   PUSH FAILED
    echo ============================================================
    echo.
    echo Possible reasons:
    echo 1. GitHub credentials not configured
    echo 2. Repository doesn't exist yet (create it on GitHub first)
    echo 3. Network issues
    echo.
    echo Solutions:
    echo 1. Run: gh auth login
    echo 2. Create repo at: https://github.com/new
    echo 3. Check your internet connection
    echo.
)

echo.
pause
