@echo off
title BizMind AI Assistant Launcher
color 0A

echo.
echo  ============================================
echo   🧠 BizMind AI Assistant - Starting Up...
echo  ============================================
echo.

:: Check if Ollama is accessible
echo [1/3] Checking Ollama connection...
curl -s http://localhost:11434 >nul 2>&1
if %errorlevel% neq 0 (
    echo  [WARNING] Ollama does not appear to be running.
    echo  Please start Ollama and ensure qwen2.5 is loaded:
    echo    ollama run qwen2.5
    echo.
    pause
) else (
    echo  [OK] Ollama is running.
)

:: Seed database if it doesn't exist
echo [2/3] Checking database...
if not exist "database\bizmind.db" (
    echo  [INFO] Database not found. Running seed script...
    python database\seed_data.py
) else (
    echo  [OK] Database found.
)

:: Launch Streamlit
echo [3/3] Starting BizMind application...
echo.
echo  App will open at: http://localhost:8501
echo  Default login - admin / admin123
echo.
start "" http://localhost:8501
python -m streamlit run app.py --server.port 8501

pause
