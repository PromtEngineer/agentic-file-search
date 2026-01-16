@echo off
echo ============================================
echo   FsExplorer - CLI Demo
echo ============================================
echo.

:: Set UTF-8 encoding for console and Python
chcp 65001 >nul 2>&1
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
echo Running CLI demo with IT Project documents...
echo Query: "What are all the dependencies blocking Phase 2 launch?"
echo ============================================
echo.

uv run explore --task "Look in data/demo_project/. What are all the dependencies blocking Phase 2 launch?"

echo.
pause
