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
    pause
)

echo.
echo Starting FsExplorer Web UI...
echo.
echo Once started, open your browser to:
echo   http://localhost:8001
echo.
echo Press Ctrl+C to stop the server.
echo ============================================
echo.

:: Start the server
uv run uvicorn fs_explorer.server:app --host 127.0.0.1 --port 8001

pause
