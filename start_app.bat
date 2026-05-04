@echo off
title Lecture to Notes - SYSTEM START
color 0A

echo ===================================================
echo   LECTURE TO NOTES - CINEMATIC WORKSPACE
echo ===================================================
echo.

:: 1. Start Ollama
echo [1/4] Initializing AI Engine (Ollama)...
start "" /min ollama serve
timeout /t 2 /nobreak > nul

:: 2. Start Backend
echo [2/4] Initializing AI Backend (Python)...
start "AI Backend" /min cmd /c "python main.py"
timeout /t 3 /nobreak > nul

:: 3. Start Frontend
echo [3/4] Initializing User Interface (Vite)...
cd frontend
start "Cinematic UI" /min cmd /c "npm run dev"
cd ..

:: 4. Launch Browser
echo [4/4] Launching Workspace in browser...
timeout /t 5 /nobreak > nul
start http://localhost:5173

echo.
echo ===================================================
echo   ALL SYSTEMS ONLINE. HAPPY STUDYING!
echo ===================================================
echo.
pause
exit
