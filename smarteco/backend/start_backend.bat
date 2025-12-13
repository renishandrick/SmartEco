@echo off
echo ========================================
echo Starting SmartEco Backend Server
echo ========================================
echo.
echo MongoDB Atlas: Connected
echo Database: smarteco
echo.

cd /d "%~dp0"

echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
