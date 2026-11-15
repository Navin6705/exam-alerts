@echo off
title EduAlert WhatsApp Bot Runner
color 0A
echo =======================================================
echo     EduAlert - NTA, JEE, NEET, VITEEE WhatsApp Bot     
echo =======================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b
)

echo [1/2] Checking and installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo [2/2] Launching EduAlert Web Dashboard and Bot Service...
echo.
echo Dashboard URL: http://localhost:5000
echo.
echo Press Ctrl+C in this window anytime to stop the bot.
echo =======================================================
echo.

python app.py
pause
