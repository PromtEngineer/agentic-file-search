@echo off
echo ============================================
echo   FsExplorer - Agentic AI Demo
echo ============================================
echo.

:: Set UTF-8 encoding for Python
set PYTHONIOENCODING=utf-8

:: Change to project directory
cd /d "%~dp0.."

:: Check if ProxyPal is running
echo Checking ProxyPal connection...
curl -s http://localhost:8317/v1/models >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: ProxyPal does not seem to be running on port 8317
    echo Please start ProxyPal before running the demo.
    echo.
    choice /M "Continue anyway?"
    if %ERRORLEVEL% NEQ 1 exit /b
)

echo.
echo Starting FsExplorer Web UI on port 8001...
echo.

:: Start browser after a delay (in background)
start "" cmd /c "timeout /t 3 /nobreak >nul && start http://localhost:8001"

:: Start the server (this blocks until Ctrl+C)
echo Press Ctrl+C to stop the server.
echo ============================================
echo.

uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8001

pause
