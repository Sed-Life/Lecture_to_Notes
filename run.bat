@echo off
title AI Class Note Generator
color 0A

cd /d D:\Desktop\AI_Class_Note_Generator

echo.
echo ==========================================
echo      AI CLASS NOTE GENERATOR v3.2
echo ==========================================
echo.

REM ---- Check Python ----
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python not installed
    echo Install from: https://www.python.org/downloads/
    pause
    exit
)

REM ---- Setup venv if not exists ----
if not exist venv (
    echo [SETUP] Creating virtual environment...
    python -m venv venv

    echo [SETUP] Activating venv...
    call venv\Scripts\activate

    echo [SETUP] Installing dependencies...
    pip install --upgrade pip
    pip install -r requirements.txt

    echo [SETUP] Setup complete.
) else (
    call venv\Scripts\activate
)

REM ---- Check FFmpeg ----
where ffmpeg >nul 2>nul
if %errorlevel% neq 0 (
    echo [SETUP] FFmpeg not found. Installing...

    winget install --id=Gyan.FFmpeg -e --source winget

    echo [INFO] FFmpeg installed. Restarting environment...
)

REM ---- Check Ollama ----
where ollama >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Ollama not installed
    echo ------------------------------------------
    echo Install from: https://ollama.com/download
    echo OR run:
    echo winget install Ollama.Ollama
    echo ------------------------------------------
    pause
    exit
)

REM ---- Start Ollama if not running ----
echo [INFO] Checking AI engine...

powershell -Command "try {Invoke-WebRequest http://127.0.0.1:11434/api/version -UseBasicParsing | Out-Null} catch {exit 1}"
if %errorlevel% neq 0 (
    echo [INFO] Starting AI engine...
    start "" /B ollama serve >nul 2>&1
)

REM ---- Wait for Ollama ----
:waitloop
powershell -Command "try {Invoke-WebRequest http://127.0.0.1:11434/api/version -UseBasicParsing | Out-Null} catch {exit 1}"
if %errorlevel% neq 0 (
    timeout /t 1 >nul
    goto waitloop
)

echo [READY] AI engine online
echo ------------------------------------------

REM ---- Run main program ----
echo Launching system...
echo ------------------------------------------
echo.

python process_lecture.py

echo.
echo ------------------------------------------
echo [DONE] Session complete
echo ------------------------------------------

pause
exit